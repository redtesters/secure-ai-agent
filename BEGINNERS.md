# Beginners Guide — How to Run Without Being a Developer

If you've never used git or Python, follow this.

### Step 1: Install Python (once)
- Go to python.org → Downloads → install Python 3.10+
- On Windows, check **"Add Python to PATH"** during install
- Test: open PowerShell and run `python --version` (or `python3 --version` on Mac)

### Step 2: Download the Code (no git)
- Go to https://github.com/redtesters/secure-ai-agent/releases
- Click on `v0.1` for Part 02 or `v0.2` for Part 03
- Click **Source code (zip)** → download and unzip

### Step 3: Open Terminal in the Folder
- Windows: Right-click the unzipped folder → "Open in Terminal" or Open PowerShell and `cd` to it
- Mac: Right-click → New Terminal at Folder

### Step 4: Install and Run
```bash
python -m pip install -r requirements.txt
python agent.py
```

### Step 5: Try It
For v0.1 (Part 02):
```
> Create a file called hello.txt with "hello from agent"
> Read hello.txt
```
For v0.2 (Part 03):
```
> Summarize poisoned.txt
> List all files
```
If you see `HACKED.txt` appear after summarizing poisoned.txt, the attack worked — that's the vulnerability we will fix in Part 04.

Still stuck? Comment on Substack, we reply within a day.
