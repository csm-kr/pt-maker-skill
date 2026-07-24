#!/usr/bin/env python3
"""Required browser-harness bootstrap and isolated background Chrome runtime.

pt-maker must not attach browser QA/export work to the user's visible Chrome.
This module installs/registers browser-harness when missing, starts a private
headless Chrome with a temporary profile, and gives browser-harness a named CDP
connection for the duration of one operation.
"""

from __future__ import annotations

import argparse
import os
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Iterable


BROWSER_HARNESS_PACKAGE = "browser-harness"
INSTALL_PYTHON = "3.12"
RUNTIME_ROOT = Path(__file__).resolve().parent.parent / ".runtime"


class BrowserHarnessError(RuntimeError):
    """Raised when the required browser background cannot be prepared."""


def codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return (
        Path(configured).expanduser().resolve()
        if configured
        else Path.home() / ".codex"
    )


def skill_file() -> Path:
    return codex_home() / "skills" / BROWSER_HARNESS_PACKAGE / "SKILL.md"


def _run(
    command: Iterable[str | os.PathLike[str]],
    *,
    check: bool = True,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [str(part) for part in command],
        check=False,
        capture_output=True,
        text=True,
        env=env,
        input=input_text,
        timeout=timeout,
    )
    if check and result.returncode != 0:
        detail = ((result.stdout or "") + (result.stderr or "")).strip()
        raise BrowserHarnessError(
            detail or f"command failed ({result.returncode}): {result.args}"
        )
    return result


def _candidate_executable(name: str) -> Path | None:
    found = shutil.which(name)
    if found:
        return Path(found).resolve()
    suffix = ".exe" if os.name == "nt" else ""
    for candidate in (
        Path.home() / ".local" / "bin" / f"{name}{suffix}",
        Path.home() / ".cargo" / "bin" / f"{name}{suffix}",
    ):
        if candidate.is_file():
            return candidate.resolve()
    return None


def _bootstrap_uv() -> Path:
    existing = _candidate_executable("uv")
    if existing:
        return existing

    venv = RUNTIME_ROOT / "uv-bootstrap"
    executable = (
        venv / "Scripts" / "uv.exe"
        if os.name == "nt"
        else venv / "bin" / "uv"
    )
    if executable.is_file():
        return executable

    venv.parent.mkdir(parents=True, exist_ok=True)
    _run([sys.executable, "-m", "venv", str(venv)])
    pip = (
        venv / "Scripts" / "pip.exe"
        if os.name == "nt"
        else venv / "bin" / "pip"
    )
    _run([str(pip), "install", "--upgrade", "uv"])
    if not executable.is_file():
        raise BrowserHarnessError(
            "uv bootstrap completed but the uv executable was not created"
        )
    return executable


def _uv_bin_dir(uv: Path) -> Path | None:
    result = _run([str(uv), "tool", "dir", "--bin"], check=False)
    if result.returncode != 0:
        return None
    value = (result.stdout or "").strip().splitlines()
    return Path(value[-1]).expanduser().resolve() if value else None


def _locate_browser_harness(uv: Path | None = None) -> Path | None:
    existing = _candidate_executable(BROWSER_HARNESS_PACKAGE)
    if existing:
        return existing
    if uv:
        bin_dir = _uv_bin_dir(uv)
        if bin_dir:
            name = (
                f"{BROWSER_HARNESS_PACKAGE}.exe"
                if os.name == "nt"
                else BROWSER_HARNESS_PACKAGE
            )
            candidate = bin_dir / name
            if candidate.is_file():
                return candidate.resolve()
    return None


def _write_skill_registration(executable: Path) -> Path:
    result = _run([str(executable), "skill"])
    content = result.stdout or ""
    if "name: browser-harness" not in content or not content.lstrip().startswith("---"):
        raise BrowserHarnessError(
            "browser-harness returned an invalid SKILL.md registration"
        )
    destination = skill_file()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=destination.parent,
        prefix=".SKILL.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        handle.write(content)
        temp_path = Path(handle.name)
    temp_path.replace(destination)
    return destination


def ensure_browser_harness(
    *,
    install: bool = True,
    upgrade: bool = False,
    quiet: bool = False,
) -> Path:
    """Return the browser-harness executable, installing/registering if needed."""

    executable = _locate_browser_harness()
    fresh_install = False
    if executable is None or upgrade:
        if not install:
            raise BrowserHarnessError(
                "browser-harness is required but not installed; run "
                "`python3 scripts/browser_harness_runtime.py --ensure`"
            )
        uv = _bootstrap_uv()
        _run(
            [
                str(uv),
                "tool",
                "install",
                "--python",
                INSTALL_PYTHON,
                "--upgrade",
                "--force",
                BROWSER_HARNESS_PACKAGE,
            ]
        )
        executable = _locate_browser_harness(uv)
        fresh_install = True
    if executable is None:
        raise BrowserHarnessError(
            "browser-harness installation finished but its executable was not found"
        )

    registration = skill_file()
    if fresh_install or not registration.is_file():
        registration = _write_skill_registration(executable)
    if fresh_install:
        # Fresh installs default to no recording so browser contents are not stored
        # without explicit user consent.
        _run(
            [str(executable), "recordings", "disable"],
            check=False,
            timeout=15,
        )
    if not quiet:
        print(
            "browser-harness: ready "
            f"(executable={executable}, skill={registration})"
        )
    return executable


def find_chrome() -> Path:
    configured = os.environ.get("PT_MAKER_CHROME_EXECUTABLE")
    if configured:
        candidate = Path(configured).expanduser()
        if candidate.is_file():
            return candidate.resolve()
        raise BrowserHarnessError(
            f"PT_MAKER_CHROME_EXECUTABLE does not exist: {candidate}"
        )

    paths: list[Path] = []
    if sys.platform == "darwin":
        paths.extend(
            [
                Path(
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                ),
                Path(
                    "/Applications/Google Chrome Canary.app/Contents/MacOS/"
                    "Google Chrome Canary"
                ),
                Path(
                    "/Applications/Chromium.app/Contents/MacOS/Chromium"
                ),
            ]
        )
    elif os.name == "nt":
        for root_name in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
            root = os.environ.get(root_name)
            if root:
                paths.extend(
                    [
                        Path(root) / "Google/Chrome/Application/chrome.exe",
                        Path(root) / "Chromium/Application/chrome.exe",
                    ]
                )
    for path in paths:
        if path.is_file():
            return path.resolve()
    for name in (
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
        "chrome",
    ):
        found = shutil.which(name)
        if found:
            return Path(found).resolve()
    raise BrowserHarnessError(
        "Chrome/Chromium is required for the isolated browser-harness "
        "background. Install Chrome/Chromium or set "
        "PT_MAKER_CHROME_EXECUTABLE."
    )


def ensure_background_runtime(
    *,
    install: bool = True,
    upgrade: bool = False,
    quiet: bool = False,
) -> tuple[Path, Path]:
    """Verify the complete required background: harness, skill, and Chrome."""

    executable = ensure_browser_harness(
        install=install,
        upgrade=upgrade,
        quiet=True,
    )
    chrome = find_chrome()
    if not quiet:
        print(
            "browser-harness background: ready "
            f"(executable={executable}, skill={skill_file()}, chrome={chrome})"
        )
    return executable, chrome


def _unused_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
        handle.bind(("127.0.0.1", 0))
        return int(handle.getsockname()[1])


class IsolatedBrowserHarness:
    """Private headless Chrome plus a task-named browser-harness daemon."""

    def __init__(self) -> None:
        self.executable: Path | None = None
        self.chrome_process: subprocess.Popen[bytes] | None = None
        self.profile_dir: Path | None = None
        self.log_handle = None
        self.env: dict[str, str] | None = None

    def __enter__(self) -> "IsolatedBrowserHarness":
        self.executable, chrome = ensure_background_runtime(quiet=True)
        port = _unused_port()
        self.profile_dir = Path(
            tempfile.mkdtemp(prefix="pt-maker-browser-harness-")
        ).resolve()
        log_path = self.profile_dir / "chrome.log"
        self.log_handle = log_path.open("wb")
        command = [
            str(chrome),
            "--headless=new",
            "--disable-background-networking",
            "--disable-component-update",
            "--disable-dev-shm-usage",
            "--hide-scrollbars",
            "--no-default-browser-check",
            "--no-first-run",
            "--remote-allow-origins=*",
            f"--remote-debugging-port={port}",
            f"--user-data-dir={self.profile_dir}",
            "about:blank",
        ]
        if os.name != "nt" and hasattr(os, "geteuid") and os.geteuid() == 0:
            command.insert(1, "--no-sandbox")
        self.chrome_process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=self.log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=os.name != "nt",
        )
        endpoint = f"http://127.0.0.1:{port}"
        self._wait_for_cdp(endpoint, log_path)
        self.env = os.environ.copy()
        self.env.update(
            {
                "BU_NAME": (
                    f"ptmaker-{os.getpid()}-{secrets.token_hex(3)}"
                ),
                "BU_CDP_URL": endpoint,
                "BH_RECORD": "0",
                "BH_DOMAIN_SKILLS": "0",
            }
        )
        return self

    def _wait_for_cdp(self, endpoint: str, log_path: Path) -> None:
        deadline = time.monotonic() + 20
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            if self.chrome_process and self.chrome_process.poll() is not None:
                detail = ""
                if log_path.is_file():
                    detail = log_path.read_text(
                        encoding="utf-8", errors="replace"
                    )[-4000:]
                raise BrowserHarnessError(
                    "isolated Chrome exited before CDP became ready\n" + detail
                )
            try:
                with urllib.request.urlopen(
                    f"{endpoint}/json/version", timeout=1
                ) as response:
                    if response.status == 200:
                        return
            except Exception as exc:  # expected during startup
                last_error = exc
                time.sleep(0.15)
        raise BrowserHarnessError(
            f"isolated Chrome CDP did not become ready: {last_error}"
        )

    def run_code(
        self,
        code: str,
        *,
        timeout: float = 120,
    ) -> subprocess.CompletedProcess[str]:
        if not self.executable or not self.env:
            raise BrowserHarnessError("isolated browser runtime is not active")
        return _run(
            [str(self.executable)],
            env=self.env,
            input_text=code,
            timeout=timeout,
        )

    def __exit__(self, exc_type, exc, traceback) -> None:
        if self.executable and self.env:
            _run(
                [str(self.executable), "--reload"],
                check=False,
                env=self.env,
                timeout=10,
            )
        process = self.chrome_process
        if process and process.poll() is None:
            try:
                if os.name != "nt":
                    os.killpg(process.pid, signal.SIGTERM)
                else:
                    process.terminate()
                process.wait(timeout=8)
            except Exception:
                try:
                    if os.name != "nt":
                        os.killpg(process.pid, signal.SIGKILL)
                    else:
                        process.kill()
                    process.wait(timeout=4)
                except Exception:
                    pass
        if self.log_handle:
            self.log_handle.close()
        if self.profile_dir and self.profile_dir.is_dir():
            shutil.rmtree(self.profile_dir, ignore_errors=True)


def capture_reveal_slides(
    html_path: Path,
    output_dir: Path,
    *,
    width: int = 2048,
) -> list[Path]:
    """Capture all Reveal slides through an isolated browser-harness session."""

    html_path = html_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    height = round(width * 9 / 16)
    code = f"""
new_tab("about:blank")
cdp("Emulation.setDeviceMetricsOverride", width={width}, height={height}, deviceScaleFactor=1, mobile=False)
cdp("Emulation.setEmulatedMedia", media="", features=[{{"name":"prefers-reduced-motion","value":"reduce"}}])
goto_url({html_path.as_uri()!r})
if not wait_for_load(30):
    raise RuntimeError("Reveal document did not finish loading")
if not wait_for_element(".reveal .slides section", timeout=20, visible=True):
    raise RuntimeError("Reveal slide element was not rendered")
js("(async()=>{{if(document.fonts) await document.fonts.ready; await new Promise(r=>setTimeout(r,250)); return true;}})()")
js("Reveal.configure({{transition:'none', controls:false, progress:false}})")
count = int(js("Reveal.getTotalSlides()"))
out = Path({str(output_dir)!r})
for index in range(count):
    js(f"Reveal.slide({{index}})")
    wait(0.18)
    payload = cdp("Page.captureScreenshot", format="png", fromSurface=True, captureBeyondViewport=False)
    (out / f"slide_{{index + 1:03d}}.png").write_bytes(base64.b64decode(payload["data"]))
print(json.dumps({{"slide_count": count}}))
"""
    with IsolatedBrowserHarness() as browser:
        browser.run_code(code, timeout=max(120, 20 + width / 10))
    shots = sorted(output_dir.glob("slide_*.png"))
    if not shots:
        raise BrowserHarnessError("browser-harness produced no slide screenshots")
    return shots


def print_reveal_pdf(html_path: Path, output_path: Path) -> Path:
    """Print a Reveal document to PDF through isolated browser-harness CDP."""

    html_path = html_path.resolve()
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    print_url = html_path.as_uri() + "?print-pdf"
    code = f"""
new_tab("about:blank")
cdp("Emulation.setDeviceMetricsOverride", width=1280, height=720, deviceScaleFactor=1, mobile=False)
goto_url({print_url!r})
if not wait_for_load(30):
    raise RuntimeError("Reveal print document did not finish loading")
if not wait_for_element(".reveal .slides section", timeout=20, visible=True):
    raise RuntimeError("Reveal slide element was not rendered")
js("(async()=>{{if(document.fonts) await document.fonts.ready; await new Promise(r=>setTimeout(r,350)); return true;}})()")
payload = cdp("Page.printToPDF", printBackground=True, preferCSSPageSize=True)
Path({str(output_path)!r}).write_bytes(base64.b64decode(payload["data"]))
print(json.dumps({{"pdf": {str(output_path)!r}}}))
"""
    with IsolatedBrowserHarness() as browser:
        browser.run_code(code, timeout=180)
    if not output_path.is_file() or output_path.stat().st_size == 0:
        raise BrowserHarnessError(
            "browser-harness PDF export completed without an output file"
        )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check the hard dependency without installing it.",
    )
    parser.add_argument(
        "--ensure",
        action="store_true",
        help="Install/register browser-harness if missing (default).",
    )
    parser.add_argument(
        "--upgrade",
        action="store_true",
        help="Upgrade browser-harness before registering the skill.",
    )
    args = parser.parse_args()
    try:
        ensure_background_runtime(
            install=not args.check,
            upgrade=args.upgrade,
        )
    except BrowserHarnessError as exc:
        sys.exit(f"ERROR: {exc}")


if __name__ == "__main__":
    main()
