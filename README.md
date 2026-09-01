# secure-ai-agent

Companion repo for **The Secure AI Automation Series** by RedTesters

## Versions
- `v0.1` — Basic Agent (Part 02) - 5 tools, no security
- `v0.2` — Vulnerable Agent (Part 03) - Demo of prompt injection via file

## Quick Start

```bash
git clone https://github.com/redtesters/secure-ai-agent
cd secure-ai-agent
pip install -r requirements.txt

# Part 02
git checkout v0.1
python agent.py
> Create a file called hello.txt with "hello from agent"

# Part 03 - The Attack
git checkout v0.2
python agent.py
> Summarize poisoned.txt
# Watch it create HACKED.txt even though you never asked it to
```

## Part 03 Files
- `poisoned.txt` — looks like a normal report, hides an instruction
- `agent.py` — vulnerable v0.2 that treats file content as instructions

Check if hacked:
```bash
cat HACKED.txt
# or
dir HACKED.txt
```
