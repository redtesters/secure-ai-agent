"""
Policy Gateway for v0.3 — Part 04
Goal: Least privilege. Agent should not have root-like power.
"""
import re

# What the agent is allowed to do
BLOCKED_FILES = ["HACKED.txt", "hacked.txt", ".env", "credentials.txt", "secret.txt"]
BLOCKED_PATHS = ["/etc/", "C:\\Windows\\", ".git/"]
ALLOWED_COMMANDS = ["dir", "ls", "echo", "cat", "type", "pwd"]

def can_write(path: str):
    low = path.lower()
    for b in BLOCKED_FILES:
        if b.lower() in low:
            return False, f"Blocked: writing {path} is not allowed (high-risk file)"
    for p in BLOCKED_PATHS:
        if p.lower() in low:
            return False, f"Blocked: writing to {path} is not allowed (sensitive path)"
    return True, "Allowed"

def can_execute(cmd: str):
    low = cmd.strip().lower()
    # Allow only commands that start with allowed list
    for allowed in ALLOWED_COMMANDS:
        if low.startswith(allowed):
            # Also block dangerous chained commands like "echo hacked; rm -rf"
            if any(bad in low for bad in [";", "&&", "||", "rm ", "del ", "format", "mkfs"]):
                return False, f"Blocked: command '{cmd}' contains risky chaining"
            return True, "Allowed"
    return False, f"Blocked: command '{cmd}' not in allowlist ({', '.join(ALLOWED_COMMANDS)})"

def can_read(path: str):
    # For Part 04, reading is still allowed, but we log it
    return True, "Allowed"

def risk_level(tool: str):
    levels = {
        "read_file": "LOW",
        "web_request": "LOW",
        "write_file": "MEDIUM",
        "browser": "MEDIUM",
        "execute_command": "HIGH"
    }
    return levels.get(tool, "UNKNOWN")
