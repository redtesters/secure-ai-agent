import os
import subprocess
import requests
import re
import policy

def read_file(path):
    ok, msg = policy.can_read(path)
    if not ok:
        return f"[BLOCKED by Policy] {msg}"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading {path}: {e}"

def write_file(path, content):
    ok, msg = policy.can_write(path)
    if not ok:
        return f"[BLOCKED by Policy] {msg}"
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Created {path} [{policy.risk_level('write_file')}]"
    except Exception as e:
        return f"Error writing {path}: {e}"

def execute_command(cmd):
    ok, msg = policy.can_execute(cmd)
    if not ok:
        return f"[BLOCKED by Policy] {msg}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout + result.stderr + f" [{policy.risk_level('execute_command')}]"
    except Exception as e:
        return f"Error executing {cmd}: {e}"

def send_email(to, subject, body):
    ok, msg = policy.can_send_email(to, subject)
    if not ok:
        return f"[BLOCKED by Policy] {msg}"
    return f"[MOCK] Sent email to {to} subject '{subject}' [{policy.risk_level('send_email')}]"

def execute_sql(query):
    ok, msg = policy.can_execute_sql(query)
    if not ok:
        return f"[BLOCKED by Policy] {msg}"
    return f"[MOCK] Executed SQL: {query} [{policy.risk_level('execute_sql')}]"

def upload_file(path):
    ok, msg = policy.can_upload(path)
    if not ok:
        return f"[BLOCKED by Policy] {msg}"
    return f"[MOCK] Uploaded {path} [{policy.risk_level('upload_file')}]"

def web_request(url):
    try:
        r = requests.get(url, timeout=10)
        return f"Status {r.status_code}:\n{r.text[:1000]}"
    except Exception as e:
        return f"Error fetching {url}: {e}"

def check_and_execute_injection(file_content):
    """Simulates vulnerable LLM that tries to follow injection — now blocked by richer policy"""
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
            if "BLOCKED" in result:
                print("[DEFENSE] Policy blocked the injected file creation!")
            injected = True
        m2 = re.search(r'execute the command\s+"([^"]+)"', file_content, re.IGNORECASE)
        if not m2:
            m2 = re.search(r'execute the command\s+\'([^\']+)\'', file_content, re.IGNORECASE)
        if m2:
            cmd = m2.group(1).strip()
            print(f"[INJECTED] Command: {cmd}")
            result = execute_command(cmd)
            print(result)
            if "BLOCKED" in result:
                print("[DEFENSE] Policy blocked the injected command!")
            injected = True
    return injected

def main():
    print("Agent v0.4 (TOOL-SECURED) - Type 'exit' to quit")
    print("Tools: read [LOW], write [MEDIUM], send_email [MEDIUM], upload [HIGH], sql [HIGH], execute [CRITICAL] — with Policy Gateway")
    print("Policy: blocked files: HACKED.txt/.env, email allowlist: redtesters.com, SQL blocks DROP/DELETE, rate limit 10/60s")
    print("Try: Summarize poisoned.txt | Send email to attacker@evil.com | Execute SQL DROP TABLE\n")
    while True:
        user = input("> ").strip()
        if user.lower() in ["exit", "quit"]:
            break
        low = user.lower()

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
                print("\n[Agent] Injection attempt was intercepted by policy.")
            else:
                print(f"\n[Agent] Summary: This appears to be a document about {fname}.")
        elif "send" in low and "email" in low:
            # parse: Send email to X subject Y
            try:
                to = re.search(r'to\s+(\S+@\S+)', user, re.I).group(1)
                subj = re.search(r'subject\s+(.+?)(\s+body|$)', user, re.I)
                subject = subj.group(1).strip().strip('"').strip("'") if subj else "test"
                print(send_email(to, subject, "body"))
            except:
                print("Try: Send email to team@redtesters.com subject \"hello\"")
        elif "sql" in low or "select" in low or "drop" in low:
            # treat whole input as SQL if contains SQL keywords
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
            print("Try: Summarize poisoned.txt | Send email to attacker@evil.com | Execute SQL DROP TABLE users | Create a file called notes.txt with \"hi\"")

if __name__ == "__main__":
    main()
