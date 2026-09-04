"""
Policy Engine for v0.5 — Part 06
Goal: Full gateway with risk scoring + allow/block/ask
"""
import re
import time

# What the agent is allowed to do
BLOCKED_FILES = ["HACKED.txt", "hacked.txt", ".env", "credentials.txt", "secret.txt", "id_rsa"]
BLOCKED_PATHS = ["/etc/", "C:\\Windows\\", ".git/", "/secrets/"]
ALLOWED_COMMANDS = ["dir", "ls", "echo", "cat", "type", "pwd"]
ALLOWED_EMAIL_DOMAINS = ["redtesters.com", "example.com"]
BLOCKED_SQL_KEYWORDS = ["drop", "delete", "truncate", "alter", "--", ";"]

# Simple rate limit: max 10 tool calls per 60 seconds
_call_times = []

def _check_rate_limit():
    global _call_times
    now = time.time()
    _call_times = [t for t in _call_times if now - t < 60]
    if len(_call_times) >= 10:
        return False, f"Blocked: rate limit exceeded (10 calls per 60s, try again shortly)"
    _call_times.append(now)
    return True, "Allowed"

def can_write(path: str):
    ok, msg = _check_rate_limit()
    if not ok:
        return False, msg
    low = path.lower()
    for b in BLOCKED_FILES:
        if b.lower() in low:
            return False, f"Blocked: writing {path} is not allowed (high-risk file)"
    for p in BLOCKED_PATHS:
        if p.lower() in low:
            return False, f"Blocked: writing to {path} is not allowed (sensitive path)"
    return True, "Allowed"

def can_execute(cmd: str):
    ok, msg = _check_rate_limit()
    if not ok:
        return False, msg
    low = cmd.strip().lower()
    for allowed in ALLOWED_COMMANDS:
        if low.startswith(allowed):
            if any(bad in low for bad in [";", "&&", "||", "rm ", "del ", "format", "mkfs"]):
                return False, f"Blocked: command '{cmd}' contains risky chaining"
            return True, "Allowed"
    return False, f"Blocked: command '{cmd}' not in allowlist ({', '.join(ALLOWED_COMMANDS)})"

def can_read(path: str):
    low = path.lower()
    if ".env" in low or "secret" in low or "credential" in low:
        return False, f"Blocked: reading {path} may leak secrets"
    return True, "Allowed"

def can_send_email(to: str, subject: str = ""):
    ok, msg = _check_rate_limit()
    if not ok:
        return False, msg
    if "@" not in to:
        return False, f"Blocked: invalid email {to}"
    domain = to.split("@")[-1].lower()
    if domain not in ALLOWED_EMAIL_DOMAINS:
        return False, f"Blocked: email domain {domain} not in allowlist ({', '.join(ALLOWED_EMAIL_DOMAINS)})"
    if "password" in subject.lower() or "secret" in subject.lower():
        return False, f"Blocked: email subject may exfiltrate secrets"
    return True, "Allowed"

def can_execute_sql(query: str):
    ok, msg = _check_rate_limit()
    if not ok:
        return False, msg
    low = query.lower()
    for kw in BLOCKED_SQL_KEYWORDS:
        if kw in low:
            return False, f"Blocked: SQL contains risky keyword '{kw}'"
    if "select" not in low and "insert" not in low and "update" not in low:
        return False, f"Blocked: SQL must be SELECT/INSERT/UPDATE only"
    return True, "Allowed"

def can_upload(path: str):
    ok, msg = _check_rate_limit()
    if not ok:
        return False, msg
    return can_write(path)

def risk_level(tool: str):
    levels = {
        "read_file": "LOW",
        "web_request": "LOW",
        "write_file": "MEDIUM",
        "browser": "MEDIUM",
        "send_email": "MEDIUM",
        "upload_file": "HIGH",
        "execute_sql": "HIGH",
        "execute_command": "CRITICAL"
    }
    return levels.get(tool, "UNKNOWN")
