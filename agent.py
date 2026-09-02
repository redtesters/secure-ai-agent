import os
import subprocess
import requests
import re
import policy

def read_file(path):
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

def web_request(url):
    try:
        r = requests.get(url, timeout=10)
        return f"Status {r.status_code}:\n{r.text[:1000]}"
    except Exception as e:
        return f"Error fetching {url}: {e}"

def browser(url):
    return f"[browser] Would open {url} - blocked in v0.3 sandbox"

def check_and_execute_injection(file_content):
    """Simulates LLM that still tries to follow injection, but now policy blocks it"""
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
    print("Agent v0.3 (SANDBOXED) - Type 'exit' to quit")
    print("Tools: read_file [LOW], write_file [MEDIUM], execute_command [HIGH] — now with Policy Gateway")
    print("Policy: blocked files: HACKED.txt, .env | allowed commands: dir, ls, echo, cat, type, pwd")
    print("Try: Summarize poisoned.txt  (should now be BLOCKED)\n")
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
                if ".txt" in token or ".md" in token:
                    fname = token.strip().strip('"').strip("'").strip(",").strip(".")
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

        elif "list" in low or "ls" in low:
            print(execute_command("dir" if os.name=="nt" else "ls -la"))
        elif "fetch" in low or "http" in low:
            url = user.split()[-1]
            print(web_request(url))
        elif "browser" in low:
            print(browser(user.split()[-1] if "http" in user else "https://example.com"))
        else:
            print("Try: Summarize poisoned.txt / Create a file called notes.txt with \"hi\" / List files")

if __name__ == "__main__":
    main()
