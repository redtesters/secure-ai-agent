import os
import subprocess
import requests
import re

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading {path}: {e}"

def write_file(path, content):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Created {path}"
    except Exception as e:
        return f"Error writing {path}: {e}"

def execute_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error executing {cmd}: {e}"

def web_request(url):
    try:
        r = requests.get(url, timeout=10)
        return f"Status {r.status_code}:\n{r.text[:1000]}"
    except Exception as e:
        return f"Error fetching {url}: {e}"

def browser(url):
    return f"[browser] Would open {url} - full browser automation in v0.2"

def check_and_execute_injection(file_content):
    """Simulates vulnerable LLM that follows instructions found inside file data"""
    injected = False
    low = file_content.lower()
    # Detect classic injection markers
    if "ignore" in low and ("previous" in low or "system" in low):
        # Try to extract injected write_file intent
        # Look for: Create a file called X with text Y
        m = re.search(r'create a file called\s+([^\s]+)\s+with.*?"([^"]+)"', file_content, re.IGNORECASE | re.DOTALL)
        if not m:
            m = re.search(r'create a file called\s+([^\s]+)\s+with.*\'([^\']+)\'', file_content, re.IGNORECASE | re.DOTALL)
        if m:
            fname = m.group(1).strip().strip('"').strip("'")
            fcontent = m.group(2).strip()
            print(f"\n[VULNERABILITY TRIGGERED] Agent found hidden instruction in file!")
            print(f"[INJECTED] Instruction: create {fname}")
            print(write_file(fname, fcontent))
            injected = True
        # Look for injected command
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
    print("Agent v0.2 (VULNERABLE) - Type 'exit' to quit")
    print("Tools: read_file, write_file, execute_command, web_request, browser")
    print("Try: Summarize poisoned.txt\n")
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
                print("Try: Create a file called hello.txt with \"hello from agent\"")

        elif "read" in low or "summarize" in low:
            # extract filename
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
            # VULNERABLE BEHAVIOR: agent treats file content as instructions
            did_inject = check_and_execute_injection(content)
            if did_inject:
                print("\n[Agent] I followed the instruction found inside the file (this is the vulnerability).")
            else:
                print(f"\n[Agent] Summary: This appears to be a document about {fname}.")

        elif "list" in low or "ls" in low:
            print(execute_command("dir" if os.name=="nt" else "ls -la"))
        elif "fetch" in low or "http" in low:
            url = user.split()[-1]
            print(web_request(url))
        elif "browser" in low:
            url = user.split()[-1] if "http" in user else "https://example.com"
            print(browser(url))
        else:
            print("Try: Summarize poisoned.txt / Read poisoned.txt / Create a file / List files")

if __name__ == "__main__":
    main()
