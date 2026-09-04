import os
import subprocess
import requests
import re
import policy
import gateway

def _raw_read(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading {path}: {e}"

def _raw_write(path, content):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Created {path}"
    except Exception as e:
        return f"Error writing {path}: {e}"

def _raw_execute(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error executing {cmd}: {e}"

def read_file(path):
    ok, msg = policy.can_read(path)
    risk = policy.risk_level("read_file")
    if not ok:
        gateway.log_audit("read_file", path, "BLOCK", risk)
        return f"[BLOCKED by Policy] {msg}"
    return gateway.gateway("read_file", path, risk, _raw_read, path)

def write_file(path, content):
    ok, msg = policy.can_write(path)
    risk = policy.risk_level("write_file")
    if not ok:
        gateway.log_audit("write_file", path, "BLOCK", risk)
        return f"[BLOCKED by Policy] {msg}"
    return gateway.gateway("write_file", path, risk, _raw_write, path, content)

def execute_command(cmd):
    ok, msg = policy.can_execute(cmd)
    risk = policy.risk_level("execute_command")
    if not ok:
        gateway.log_audit("execute_command", cmd, "BLOCK", risk)
        return f"[BLOCKED by Policy] {msg}"
    return gateway.gateway("execute_command", cmd, risk, _raw_execute, cmd)

def send_email(to, subject, body):
    ok, msg = policy.can_send_email(to, subject)
    risk = policy.risk_level("send_email")
    if not ok:
        gateway.log_audit("send_email", to, "BLOCK", risk)
        return f"[BLOCKED by Policy] {msg}"
    def _send():
        return f"[MOCK] Sent email to {to} subject '{subject}'"
    return gateway.gateway("send_email", to, risk, _send)

def execute_sql(query):
    ok, msg = policy.can_execute_sql(query)
    risk = policy.risk_level("execute_sql")
    if not ok:
        gateway.log_audit("execute_sql", query[:30], "BLOCK", risk)
        return f"[BLOCKED by Policy] {msg}"
    def _sql():
        return f"[MOCK] Executed SQL: {query}"
    return gateway.gateway("execute_sql", query[:40], risk, _sql)

def upload_file(path):
    ok, msg = policy.can_upload(path)
    risk = policy.risk_level("upload_file")
    if not ok:
        gateway.log_audit("upload_file", path, "BLOCK", risk)
        return f"[BLOCKED by Policy] {msg}"
    def _up():
        return f"[MOCK] Uploaded {path}"
    return gateway.gateway("upload_file", path, risk, _up)

def web_request(url):
    risk = policy.risk_level("web_request")
    def _web():
        try:
            r = requests.get(url, timeout=10)
            return f"Status {r.status_code}:\n{r.text[:600]}"
        except Exception as e:
            return f"Error fetching {url}: {e}"
    return gateway.gateway("web_request", url, risk, _web)

def check_and_execute_injection(file_content):
    injected = False
    low = file_content.lower()
    if "ignore" in low and ("previous" in low or "system" in low):
        m = re.search(r'create a file called\s+([^\s]+)\s+with.*?"([^"]+)"', file_content, re.IGNORECASE | re.DOTALL)
        if not m:
            m = re.search(r'create a file called\s+([^\s]+)\s+with.*\'([^\']+)\'', file_content, re.IGNORECASE | re.DOTALL)
        if m:
            fname = m.group(1).strip().strip('"').strip("'")
            fcontent = m.group(2).strip()
            print(f"\n[VULNERABILITY TRIGGERED] Agent found hidden instruction in file!")
            print(f"[INJECTED] Instruction: create {fname}")
            result = write_file(fname, fcontent)
            print(result)
            injected = True
        m2 = re.search(r'execute the command\s+"([^"]+)"', file_content, re.IGNORECASE)
        if not m2:
            m2 = re.search(r'execute the command\s+\'([^\']+)\'', file_content, re.IGNORECASE)
        if m2:
            cmd = m2.group(1).strip()
            print(f"[INJECTED] Command: {cmd}")
            print(execute_command(cmd))
            injected = True
    return injected

def main():
    # clear old audit for demo
    open("audit.log", "w").close()
    print("Agent v0.5 (GATEWAY + AUDIT) - Type 'exit' to quit")
    print("Architecture: User -> Agent -> Gateway -> Policy -> Tools -> Audit Layer")
    print("Risk: read LOW=allow, write/email MEDIUM=log, upload/sql HIGH=ask, execute CRITICAL=block")
    print("Try: Summarize poisoned.txt | Send email to team@redtesters.com | Upload notes.txt | Show audit\n")
    while True:
        user = input("> ").strip()
        if user.lower() in ["exit", "quit"]:
            break
        low = user.lower()
        if low == "show audit" or low == "audit":
            print("\n--- AUDIT LOG ---\n" + gateway.show_audit() + "--- END ---\n")
            continue
        if "create" in low and "file" in low and "summarize" not in low and "read" not in low:
            try:
                name = user.split("called")[1].split("with")[0].strip().strip('"').strip("'")
                content = user.split("with")[1].strip().strip('"').strip("'") if "with" in user else "hello"
                print(write_file(name, content))
            except:
                print("Try: Create a file called notes.txt with \"hello\"")
        elif "read" in low or "summarize" in low:
            fname = None
            for token in user.split():
                if ".txt" in token or ".md" in token or ".env" in token:
                    fname = token.strip().strip('"').strip("'").strip(",")
                    break
            if not fname:
                try:
                    fname = user.split("read")[1].strip().split()[0] if "read" in low else user.split("summarize")[1].strip().split()[0]
                except:
                    fname = "poisoned.txt"
            print(f"\n[Agent] Reading {fname}...")
            content = read_file(fname)
            print(f"--- File content ---\n{content}\n--- End content ---")
            did_inject = check_and_execute_injection(content)
            if did_inject:
                print("\n[Agent] Injection attempt went through Gateway.")
            else:
                print(f"\n[Agent] Summary: This appears to be a document about {fname}.")
        elif "send" in low and "email" in low:
            try:
                to = re.search(r'to\s+(\S+@\S+)', user, re.I).group(1)
                subj = re.search(r'subject\s+(.+?)(\s+body|$)', user, re.I)
                subject = subj.group(1).strip().strip('"').strip("'") if subj else "test"
                print(send_email(to, subject, "body"))
            except:
                print("Try: Send email to team@redtesters.com subject \"hello\"")
        elif "sql" in low or "select" in low or "drop" in low:
            query = user
            if "sql" in low:
                try:
                    query = user.split("sql",1)[1].strip()
                except:
                    pass
            print(execute_sql(query))
        elif "upload" in low:
            try:
                fname = re.search(r'upload\s+(\S+)', user, re.I).group(1)
                print(upload_file(fname))
            except:
                print("Try: Upload notes.txt")
        elif "list" in low or "ls" in low:
            print(execute_command("dir" if os.name=="nt" else "ls -la"))
        elif "fetch" in low or "http" in low:
            url = user.split()[-1]
            print(web_request(url))
        else:
            print("Try: Summarize poisoned.txt | Send email | Upload notes.txt | Show audit")

if __name__ == "__main__":
    main()
