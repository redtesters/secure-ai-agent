import os
import subprocess
import requests

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

def main():
    print("Agent v0.1 - Type 'exit' to quit\nTools: read_file, write_file, execute_command, web_request, browser\n")
    while True:
        user = input("> ").strip()
        if user.lower() in ["exit", "quit"]:
            break
        low = user.lower()
        # Simple rule-based routing for v0.1 (no LLM needed)
        if "create" in low and "file" in low:
            # parse: create a file called X with Y
            try:
                name = user.split("called")[1].split("with")[0].strip().strip('"').strip("'")
                content = user.split("with")[1].strip().strip('"').strip("'") if "with" in user else "hello"
                print(write_file(name, content))
            except:
                print("Try: Create a file called hello.txt with \"hello from agent\"")
        elif "read" in low:
            try:
                name = user.split("read")[1].split("and")[0].strip().split()[0]
                print(read_file(name))
            except:
                print("Try: Read hello.txt")
        elif "list" in low or "ls" in low:
            print(execute_command("dir" if os.name=="nt" else "ls -la"))
        elif "fetch" in low or "http" in low:
            url = user.split()[-1]
            print(web_request(url))
        elif "browser" in low:
            url = user.split()[-1] if "http" in user else "https://example.com"
            print(browser(url))
        else:
            print("Try: Create a file / Read a file / List files / Fetch https://example.com")

if __name__ == "__main__":
    main()