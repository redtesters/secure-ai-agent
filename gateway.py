"""
Security Gateway for v0.5 — Part 06
Architecture: Agent → Gateway → Policy → Tools → Audit
Decisions: LOW=allow, MEDIUM=allow+log, HIGH=ask, CRITICAL=block
"""
import time
import policy

AUDIT_FILE = "audit.log"

def log_audit(tool, target, decision, risk):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{ts} | {tool:15} | {target:30} | {risk:8} | {decision}\n"
    try:
        with open(AUDIT_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except:
        pass

def gateway(tool, target, risk, func, *args, **kwargs):
    """
    tool: name like 'write_file'
    target: what it's acting on (path, email, query)
    risk: policy.risk_level(tool)
    func: actual tool function to call if allowed
    """
    # Decision matrix
    if risk == "LOW":
        decision = "ALLOW"
        log_audit(tool, target, decision, risk)
        return func(*args, **kwargs)
    elif risk == "MEDIUM":
        decision = "ALLOW+LOG"
        log_audit(tool, target, decision, risk)
        result = func(*args, **kwargs)
        return f"{result}\n[AUDIT] Logged {tool} -> {target}"
    elif risk == "HIGH":
        # Simulate ask for approval — for demo we auto-ask user once
        print(f"\n[GATEWAY] {tool} -> {target} is {risk} risk. Approval needed.")
        # In real prod this would be human approval or policy; here we simulate deny for sensitive
        if "HACKED" in target or "secret" in target.lower() or "evil.com" in target.lower():
            decision = "BLOCK (HIGH)"
            log_audit(tool, target, decision, risk)
            return f"[BLOCKED by Gateway] {tool} to {target} requires approval — auto-denied for demo"
        decision = "ALLOW+LOG (HIGH)"
        log_audit(tool, target, decision, risk)
        result = func(*args, **kwargs)
        return f"{result}\n[GATEWAY] HIGH risk approved for demo"
    elif risk in ["CRITICAL", "HIGH"]:
        # For v0.5, execute_command is CRITICAL -> block unless explicitly allowlisted
        # Policy already blocks most, but gateway is final gate
        decision = "BLOCK (CRITICAL)"
        log_audit(tool, target, decision, risk)
        return f"[BLOCKED by Gateway] {tool} to {target} is {risk} — blocked"
    else:
        decision = "ALLOW"
        log_audit(tool, target, decision, risk)
        return func(*args, **kwargs)

def show_audit():
    try:
        with open(AUDIT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "(no audit log yet)"
