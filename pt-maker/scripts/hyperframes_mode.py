#!/usr/bin/env python3
"""Pinned HyperFrames runner with foreground and managed background modes.

Render remains gated in either mode: the user must review the preview, the
animation rubric ledger must pass, and the caller must provide --approved.

Background jobs are detached process groups with project-local JSON state and
logs. Use `status` and `stop` rather than relying on shell focus or Ctrl+C.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import qa_animation_guard
import qa_animation_score_gate
from browser_harness_runtime import (
    BrowserHarnessError,
    ensure_background_runtime,
)


HYPERFRAMES_VERSION = "0.7.70"
BASE_COMMAND = ["npx", "--yes", f"hyperframes@{HYPERFRAMES_VERSION}"]
BACKGROUND_ACTIONS = {"lint", "check", "snapshot", "preview", "render"}
MANAGED_ACTIONS = ("lint", "check", "snapshot", "preview", "render")
RUNTIME_DIR_NAME = ".pt-maker-runtime"


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def resolve_project(value: Path) -> Path:
    path = value.resolve()
    candidates = [path, path / "animation"]
    for candidate in candidates:
        if (candidate / "index.html").is_file() and (
            candidate / "hyperframes.json"
        ).is_file():
            return candidate
    raise FileNotFoundError(
        f"HyperFrames project not found at {path} or {path / 'animation'}"
    )


def build_command(args: argparse.Namespace, project: Path) -> list[str]:
    command = BASE_COMMAND.copy()
    if args.action == "doctor":
        return command + ["doctor"]
    if args.action == "lint":
        return command + ["lint"]
    if args.action == "check":
        command.append("check")
        if args.snapshots:
            command.append("--snapshots")
        if args.strict:
            command.append("--strict")
        return command
    if args.action == "snapshot":
        command.append("snapshot")
        if args.samples:
            command.extend(["--frames", str(args.samples)])
        return command
    if args.action == "preview":
        return command + ["preview", "--port", str(args.port)]
    if args.action == "render":
        if args.output:
            output_path = Path(args.output).expanduser()
            if not output_path.is_absolute():
                output_path = (Path.cwd() / output_path).resolve()
        else:
            output_path = project / "renders" / "presentation.mp4"
        return command + [
            "render",
            "--quality",
            args.quality,
            "--fps",
            str(args.fps),
            "--format",
            args.format,
            "-o",
            str(output_path),
        ]
    raise ValueError(f"Unsupported action: {args.action}")


def display(command: list[str], cwd: Path) -> None:
    print(
        json.dumps(
            {"cwd": str(cwd), "command": command},
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )


def run(command: list[str], cwd: Path, dry_run: bool) -> int:
    display(command, cwd)
    if dry_run:
        return 0
    return subprocess.run(command, cwd=cwd, check=False).returncode


def runtime_dir(project: Path) -> Path:
    return project / RUNTIME_DIR_NAME


def state_path_for(project: Path, action: str) -> Path:
    return runtime_dir(project) / f"{action}.json"


def load_state(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".json.tmp")
    temp.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temp.replace(path)


def process_is_running(pid: Any) -> bool:
    if not isinstance(pid, int) or pid <= 1:
        return False
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError):
        return False
    return True


def process_command(pid: int) -> str:
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "command="],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def worker_command(
    args: argparse.Namespace,
    project: Path,
    state_path: Path,
) -> list[str]:
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        args.action,
        str(project),
    ]
    if args.snapshots:
        command.append("--snapshots")
    if args.strict:
        command.append("--strict")
    if args.samples:
        command.extend(["--samples", str(args.samples)])
    if args.action == "preview":
        command.extend(["--port", str(args.port)])
    if args.action == "render":
        command.extend(["--quality", args.quality, "--fps", str(args.fps)])
        command.extend(["--format", args.format])
        if args.output:
            output_path = Path(args.output).expanduser()
            if not output_path.is_absolute():
                output_path = (Path.cwd() / output_path).resolve()
            command.extend(["--output", str(output_path)])
        if args.approved:
            command.append("--approved")
        if args.qa_ledger:
            command.extend(["--qa-ledger", str(args.qa_ledger.resolve())])
    if args.dry_run:
        command.append("--dry-run")
    command.extend(
        [
            "--background-worker",
            "--state-file",
            str(state_path),
        ]
    )
    return command


def spawn_background(args: argparse.Namespace, project: Path) -> int:
    state_path = state_path_for(project, args.action)
    prior = load_state(state_path)
    if prior and process_is_running(prior.get("pid")):
        print(
            f"ERROR: {args.action} is already running "
            f"(pid={prior.get('pid')}, log={prior.get('log')}).",
            file=sys.stderr,
        )
        return 2

    command = worker_command(args, project, state_path)
    if args.dry_run:
        display(command, project)
        return 0

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    logs_dir = runtime_dir(project) / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"{args.action}-{stamp}.log"
    with log_path.open("ab") as log_handle:
        process = subprocess.Popen(
            command,
            cwd=project,
            stdin=subprocess.DEVNULL,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            close_fds=True,
        )
    state = {
        "action": args.action,
        "status": "running",
        "pid": process.pid,
        "cwd": str(project),
        "command": command,
        "log": str(log_path),
        "started_at": utc_now(),
    }
    write_state(state_path, state)
    print(
        json.dumps(
            {
                "background_job": "started",
                "action": args.action,
                "pid": process.pid,
                "log": str(log_path),
                "state": str(state_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def finalize_background(state_path: Path, exit_code: int) -> None:
    for _ in range(40):
        state = load_state(state_path)
        if state is not None:
            break
        time.sleep(0.05)
    else:
        state = {}
    state.update(
        {
            "status": "completed" if exit_code == 0 else "failed",
            "exit_code": exit_code,
            "finished_at": utc_now(),
        }
    )
    write_state(state_path, state)


def status_background(project: Path) -> int:
    folder = runtime_dir(project)
    states: list[dict[str, Any]] = []
    for path in sorted(folder.glob("*.json")) if folder.is_dir() else []:
        state = load_state(path)
        if state is None:
            states.append(
                {
                    "action": path.stem,
                    "status": "invalid-state",
                    "state": str(path),
                }
            )
            continue
        alive = process_is_running(state.get("pid"))
        reported = dict(state)
        reported["alive"] = alive
        if not alive and reported.get("status") == "running":
            reported["status"] = "exited-without-final-state"
        states.append(reported)
    print(
        json.dumps(
            {
                "project": str(project),
                "jobs": states,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def stop_background(project: Path, target: str) -> int:
    targets = MANAGED_ACTIONS if target == "all" else (target,)
    results: list[dict[str, Any]] = []
    exit_code = 0
    for action in targets:
        path = state_path_for(project, action)
        state = load_state(path)
        if state is None:
            results.append({"action": action, "status": "not-found"})
            continue
        pid = state.get("pid")
        if not process_is_running(pid):
            results.append({"action": action, "status": "not-running", "pid": pid})
            continue
        command = process_command(pid)
        if "hyperframes_mode.py" not in command and "hyperframes" not in command:
            results.append(
                {
                    "action": action,
                    "status": "refused-pid-mismatch",
                    "pid": pid,
                    "command": command,
                }
            )
            exit_code = 1
            continue
        try:
            os.killpg(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        for _ in range(50):
            if not process_is_running(pid):
                break
            time.sleep(0.1)
        state.update(
            {
                "status": "stopped",
                "stopped_at": utc_now(),
            }
        )
        write_state(path, state)
        results.append(
            {
                "action": action,
                "status": "stopped" if not process_is_running(pid) else "stopping",
                "pid": pid,
                "log": state.get("log"),
            }
        )
    print(json.dumps({"project": str(project), "jobs": results}, ensure_ascii=False, indent=2))
    return exit_code


def validate_render_gate(args: argparse.Namespace, project: Path) -> int:
    if not args.approved:
        print(
            "ERROR: render requires --approved after the user reviews the preview.",
            file=sys.stderr,
        )
        return 2
    if args.qa_ledger is None:
        print("ERROR: render requires --qa-ledger.", file=sys.stderr)
        return 2
    args.qa_ledger = args.qa_ledger.resolve()
    gate = qa_animation_score_gate.validate(
        project / "index.html",
        args.qa_ledger,
        min_score=90,
    )
    if gate["animation_score_gate"] != "pass":
        print(json.dumps(gate, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    return 0


def execute_foreground(args: argparse.Namespace, project: Path) -> int:
    if args.action == "render":
        check_status = run(
            BASE_COMMAND + ["check", "--snapshots"],
            project,
            args.dry_run,
        )
        if check_status != 0:
            return check_status
        output_command = build_command(args, project)
        output_path = Path(output_command[-1])
        if not args.dry_run:
            output_path.parent.mkdir(parents=True, exist_ok=True)
    return run(build_command(args, project), project, args.dry_run)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=[
            "doctor",
            "lint",
            "check",
            "snapshot",
            "preview",
            "render",
            "status",
            "stop",
        ],
    )
    parser.add_argument("project", type=Path, nargs="?", default=Path("."))
    parser.add_argument("--snapshots", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--samples", type=int)
    parser.add_argument("--port", type=int, default=4567)
    parser.add_argument(
        "--quality",
        choices=["draft", "standard", "high"],
        default="standard",
    )
    parser.add_argument("--fps", choices=[24, 30, 60], type=int, default=30)
    parser.add_argument(
        "--format",
        choices=["mp4", "webm", "mov", "gif", "png-sequence"],
        default="mp4",
    )
    parser.add_argument("-o", "--output")
    parser.add_argument(
        "--approved",
        action="store_true",
        help="Confirms the user reviewed and approved the animation preview.",
    )
    parser.add_argument(
        "--qa-ledger",
        type=Path,
        help="Completed animation_qa_ledger.json required for render.",
    )
    parser.add_argument(
        "--background",
        action="store_true",
        help="Detach the job and store PID/state/logs inside the animation project.",
    )
    parser.add_argument(
        "--target",
        choices=[*MANAGED_ACTIONS, "all"],
        default="preview",
        help="Background action to stop; default is preview.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--background-worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--state-file", type=Path, help=argparse.SUPPRESS)
    return parser


def main() -> int:
    args = build_parser().parse_args()

    def finish(code: int) -> int:
        if args.background_worker and args.state_file:
            finalize_background(args.state_file.resolve(), code)
        return code

    try:
        project = resolve_project(args.project)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return finish(2)

    if args.action == "status":
        return finish(status_background(project))
    if args.action == "stop":
        return finish(stop_background(project, args.target))
    if (
        args.action in {"check", "preview", "render"}
        and not args.background
        and not args.background_worker
    ):
        print(
            f"ERROR: {args.action} must run with --background in Codex.",
            file=sys.stderr,
        )
        return finish(2)
    if args.background and args.action not in BACKGROUND_ACTIONS:
        print(
            f"ERROR: --background is supported for {sorted(BACKGROUND_ACTIONS)}.",
            file=sys.stderr,
        )
        return finish(2)
    if args.action == "preview" and not args.background_worker:
        try:
            ensure_background_runtime()
        except BrowserHarnessError as exc:
            print(
                "ERROR: browser-harness background is required for preview: "
                f"{exc}",
                file=sys.stderr,
            )
            return finish(2)

    guard = qa_animation_guard.run_checks(project / "index.html")
    if guard["animation_guard_result"] != "pass":
        print(json.dumps(guard, ensure_ascii=False, indent=2), file=sys.stderr)
        return finish(1)

    if args.action == "render":
        gate_status = validate_render_gate(args, project)
        if gate_status != 0:
            return finish(gate_status)

    if args.background and not args.background_worker:
        return finish(spawn_background(args, project))

    return finish(execute_foreground(args, project))


if __name__ == "__main__":
    sys.exit(main())
