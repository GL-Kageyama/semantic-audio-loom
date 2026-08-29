"""Resolve 用の最小 Claude API クライアント（Anthropic 互換 HTTP）。

SDK に依存せず stdlib の urllib で直接 `/v1/messages` を叩く。SDK のメジャー
バージョン差（temperature 引数の廃止など）に左右されず、Anthropic 互換
ゲートウェイならどこでも動く。認証は二系統：

- 通常の Anthropic API: `ANTHROPIC_API_KEY`（x-api-key ヘッダ）
- Claude Code 互換ゲートウェイ（deepseek 等）: `ANTHROPIC_AUTH_TOKEN` + `ANTHROPIC_BASE_URL`
  （Authorization: Bearer）

実ゲートウェイ（api.deepseek.com/anthropic）は連続呼び出しで空応答を返す率が上がるため、
最小リクエスト間隔（既定 2s）と空応答の再試行を入れる。thinking と text が max_tokens を
共有する reasoning モデルでは、予算不足で text が 0 になる「空応答」が起きるので、
Spec（短い JSON）に対して十分な予算（既定 8192）を確保する。
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

DEFAULT_MODEL = "claude-sonnet-4-5"


@dataclass
class ClientConfig:
    api_key: str = ""
    auth_token: str = ""
    base_url: str = ""
    model: str = DEFAULT_MODEL
    max_tokens: int = 8192
    temperature: float = 0.0
    max_retries: int = 4
    min_interval_seconds: float = 2.0


class ClaudeClient:
    def __init__(self, config: ClientConfig | None = None):
        self.config = config or _from_env()
        if not self.config.api_key and not self.config.auth_token:
            raise ValueError("Claude の認証情報がありません（ANTHROPIC_API_KEY か ANTHROPIC_AUTH_TOKEN）")
        base = (self.config.base_url or "https://api.anthropic.com").rstrip("/")
        self._endpoint = base + "/v1/messages"
        self._headers = {"content-type": "application/json", "anthropic-version": "2023-06-01"}
        if self.config.api_key:
            self._headers["x-api-key"] = self.config.api_key
        else:
            self._headers["authorization"] = f"Bearer {self.config.auth_token}"
        self._last_request_at = 0.0

    def complete(self, system: str, user: str) -> str:
        """system + user を送り、テキスト応答を返す。空応答は再試行。"""
        body = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": [{"role": "user", "content": user}],
        }
        if system and system.strip():
            body["system"] = system

        last_err: Exception | None = None
        for attempt in range(self.config.max_retries):
            try:
                self._throttle()
                text = self._post(body)
                if text:
                    return text
                last_err = RuntimeError("空の応答")
                if attempt < self.config.max_retries - 1:
                    time.sleep(2**attempt)
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
                last_err = e
                if attempt < self.config.max_retries - 1:
                    time.sleep(2**attempt)
        raise RuntimeError(f"Claude API 呼び出しに失敗: {last_err}") from last_err

    def complete_json(self, system: str, user: str) -> dict:
        """JSON 応答を要求して dict に解釈する（```json フェンスを剥がす）。"""
        return _parse_json(self.complete(system, user))

    def _post(self, body: dict) -> str:
        req = urllib.request.Request(
            self._endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers=self._headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return "".join(
            b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"
        ).strip()

    def _throttle(self) -> None:
        if self.config.min_interval_seconds <= 0:
            return
        now = time.monotonic()
        wait = self.config.min_interval_seconds - (now - self._last_request_at)
        if wait > 0:
            time.sleep(wait)
        self._last_request_at = time.monotonic()


def _parse_json(text: str) -> dict:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.startswith("json"):
            stripped = stripped[4:]
        stripped = stripped.strip()
    # 先頭の { から末尾の } までを切り出す（前後に説明文が付いても耐える）。
    start, end = stripped.find("{"), stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        stripped = stripped[start : end + 1]
    return json.loads(stripped)


def _from_env() -> ClientConfig:
    return ClientConfig(
        api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        auth_token=os.environ.get("ANTHROPIC_AUTH_TOKEN", ""),
        base_url=os.environ.get("ANTHROPIC_BASE_URL", ""),
        model=os.environ.get("SAL_RESOLVE_MODEL", DEFAULT_MODEL),
        max_tokens=int(os.environ.get("SAL_RESOLVE_MAX_TOKENS", "8192")),
        max_retries=int(os.environ.get("SAL_RESOLVE_MAX_RETRIES", "4")),
        min_interval_seconds=float(os.environ.get("CLAUDE_MIN_INTERVAL_SECONDS", "2.0")),
    )
