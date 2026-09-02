# secure-ai-agent

Hands-on companion to **The Secure AI Automation Series** by RedTesters.
Build an AI agent, break it, then secure it — no API key needed.

## For Beginners — No Git Needed

1. Go to **Releases** on GitHub: https://github.com/redtesters/secure-ai-agent/releases
2. Download the ZIP for the part you want:
   - **Part 02 — Build:** `v0.1` → Source code (zip)
   - **Part 03 — Hack:** `v0.2` → Source code (zip)
   - **Part 04 — Defense:** `v0.3` → Source code (zip)
3. Unzip it
4. Open the folder in Terminal / PowerShell and run:
```powershell
python -m pip install -r requirements.txt
python agent.py
```

## For Developers — With Git

```bash
git clone https://github.com/redtesters/secure-ai-agent
cd secure-ai-agent

# Part 02 — safe agent
git checkout v0.1
python agent.py
> Create a file called hello.txt with "hello from agent"

# Part 03 — vulnerable demo
git checkout v0.2
python agent.py
> Summarize poisoned.txt  # creates HACKED.txt

# Part 04 — sandboxed (attack blocked)
git checkout v0.3
python agent.py
> Summarize poisoned.txt  # now BLOCKED by policy
> Create a file called notes.txt with "hello"  # still works
```

## Troubleshooting

- `pip not found` → use `python -m pip install -r requirements.txt`
- `python not found` → try `python3 agent.py` or `py agent.py` on Windows
- `ModuleNotFoundError: requests` → run pip install again
- `HACKED.txt not found` (Part 03) → make sure you did `git checkout v0.2` and typed `Summarize poisoned.txt` exactly
- `[BLOCKED by Policy]` (Part 04) → that's the defense working!

## Versions

- `v0.1` — Basic Agent (Part 02) — 5 tools, no security
- `v0.2` — Vulnerable Agent (Part 03) — poisoned.txt controls the agent
- `v0.3` — Sandboxed Agent (Part 04) — Policy Gateway blocks high-risk actions

## Need Help?
Open an Issue on GitHub or comment on the Substack article.
