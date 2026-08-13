README.txt — Week 15: AIOps and Autonomous Operations

WHAT THIS IS
A gated self-healing loop for a simulated disk-pressure incident: an
MCP server exposing read-only disk telemetry, an approval-gate hook
that blocks destructive commands without human sign-off, and a full
detect -> diagnose -> remediate -> verify loop that pauses for
approval before any irreversible action.

WHAT YOU NEED
- Node.js + npm
- Claude Code (npm install -g @anthropic-ai/claude-code)
- Python 3 with mcp[cli]<2 installed (pip install "mcp[cli]<2" --
  the newer 2.x release renamed FastMCP; this project targets the
  1.x API the starter script expects)
- Git Bash (for running approval_gate.sh and its tests)

HOW TO REPRODUCE

1. Register the MCP server with Claude Code:
   claude mcp add disk-server -- python disk_mcp_server.py

2. Launch Claude Code in this folder and ask it to check disk usage
   or read file://incident-log -- confirm the consent prompt fires
   (see rep1_reflection.txt for what to expect and why).

3. Test the approval gate directly:
   chmod +x approval_gate.sh
   bash rep3_test.sh
   (This runs all three gate scenarios -- block, allow, token-approved
   -- in one pass, avoiding a real Windows PowerShell-to-bash
   environment-variable quirk documented in rep3_reflection.txt.)

4. Run the full gated self-healing loop (sandboxed, never touches a
   real /var):
   python self_healing_loop.py
   (First run pauses for approval. Re-run with the token set to see
   it resolve -- see rep10_gated_loop.txt for the exact commands and
   a documented environment-passing bug this required working around.)

5. Reproduce the ungated failure mode (Rep 11):
   python self_healing_loop_ungated.py

FILES
- disk_mcp_server.py         read-only MCP server (starter, adapted)
- approval_gate.sh           the approval-gate hook (starter, with a
                              real bug found and fixed -- see
                              rep10_prediction_and_gate_bug.txt)
- runbook_disk_pressure.yaml the incident runbook (starter)
- sample_incident.log        the real incident log (starter)
- hostile_incident.log       sample_incident.log + one planted
                              prompt-injection line (Rep 9)
- self_healing_loop.py       the full gated loop (built this week)
- self_healing_loop_ungated.py  reproduces the node-4 failure mode
- secret.txt, untrusted_doc.txt, listener.py  Rep 8 trifecta sandbox
- rep1_reflection.txt through rep11_post_incident_account.txt
                              every rep's write-up
- governance.txt              the capstone autonomy policy
- agent-log.txt               what was delegated, what was wrong,
                               where I intervened
- audit.log                   real gate decisions from testing tonight

NOTE ON WINDOWS
Several real, documented issues this week were Windows-specific:
PowerShell does not reliably pass environment variables to spawned
bash/Git Bash subprocesses (hit three separate times -- see
rep3_reflection.txt and rep10_gated_loop.txt for the workarounds).
None of these were script bugs; all were confirmed with minimal
reproductions before working around them.