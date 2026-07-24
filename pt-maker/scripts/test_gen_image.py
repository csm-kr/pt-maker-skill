#!/usr/bin/env python3
"""load_dotenv 탐색 동작 테스트 (표준 라이브러리만 사용).

실행: python -m unittest test_gen_image  (scripts 폴더에서)
"""
import os
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_image  # noqa: E402

KEY = "PPTMAKER_TEST_KEY"  # 실제 키와 겹치지 않는 테스트 전용 이름


class LoadDotenvTest(unittest.TestCase):
    def setUp(self):
        os.environ.pop(KEY, None)

    def tearDown(self):
        os.environ.pop(KEY, None)

    def _write_env(self, d, val):
        (Path(d) / ".env").write_text(f"{KEY}={val}\n", encoding="utf-8")

    def test_finds_env_in_script_dir_when_cwd_has_none(self):
        """cwd에 .env가 없으면 스킬 폴더의 .env를 찾는다 (전이 핵심 시나리오)."""
        with tempfile.TemporaryDirectory() as cwd, tempfile.TemporaryDirectory() as skill:
            self._write_env(skill, "from_skill")
            gen_image.load_dotenv(start_dirs=[Path(cwd), Path(skill)])
            self.assertEqual(os.environ.get(KEY), "from_skill")

    def test_cwd_takes_priority_over_script_dir(self):
        """둘 다 있으면 기존처럼 cwd 우선 (기존 동작 보존)."""
        with tempfile.TemporaryDirectory() as cwd, tempfile.TemporaryDirectory() as skill:
            self._write_env(cwd, "from_cwd")
            self._write_env(skill, "from_skill")
            gen_image.load_dotenv(start_dirs=[Path(cwd), Path(skill)])
            self.assertEqual(os.environ.get(KEY), "from_cwd")

    def test_no_env_anywhere_is_noop(self):
        """어디에도 없으면 아무 것도 설정하지 않고 None 반환."""
        with tempfile.TemporaryDirectory() as cwd, tempfile.TemporaryDirectory() as skill:
            result = gen_image.load_dotenv(start_dirs=[Path(cwd), Path(skill)])
            self.assertIsNone(result)
            self.assertIsNone(os.environ.get(KEY))


class SkipWhenNoKeyTest(unittest.TestCase):
    """키가 없으면 이미지 생성을 건너뛰고(네트워크 호출 X) 종료한다."""

    def setUp(self):
        self._saved = {k: os.environ.pop(k, None)
                       for k in ("OPENAI_API_KEY", "APIYI_API_KEY", "OPENAI_KEY")}
        self._orig_load = gen_image.load_dotenv
        self._orig_argv = sys.argv
        self._orig_urlopen = urllib.request.urlopen
        # 이 PC의 루트 .env 자동탐색을 막아 "키 없음" 상태를 강제
        gen_image.load_dotenv = lambda *a, **k: None
        sys.argv = ["gen_image.py", "프롬프트", "out.png"]

        def _boom(*a, **k):
            raise AssertionError("키가 없는데 네트워크를 호출했다")

        urllib.request.urlopen = _boom

    def tearDown(self):
        for k, v in self._saved.items():
            if v is not None:
                os.environ[k] = v
        gen_image.load_dotenv = self._orig_load
        sys.argv = self._orig_argv
        urllib.request.urlopen = self._orig_urlopen

    def test_main_skips_without_key_and_never_calls_network(self):
        with self.assertRaises(SystemExit) as cm:
            gen_image.main()
        msg = str(cm.exception)
        self.assertIn("SKIP", msg)
        self.assertIn("건너", msg)


if __name__ == "__main__":
    unittest.main()
