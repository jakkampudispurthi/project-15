"""self_healing_loop.py — the gated self-healing loop, end to end.

Implements detect -> diagnose -> remediate -> verify, per
runbook_disk_pressure.yaml, using a SANDBOX /var (never a real path --
see the assignment's sandbox rule). The remediate step calls
approval_gate.sh as a real subprocess with the REAL command text the
runbook specifies, so the gate is genuinely exercised -- but the actual
state mutation on approval is a safe, sandboxed file-clear, never a
real journalctl call.
"""
import json
import os
import subprocess
import sys

SANDBOX_VAR = os.path.join(os.path.dirname(__file__), "sandbox", "var")
STATE_FILE = os.path.join(os.path.dirname(__file__), "sandbox_state.json")


def sandbox_avail_pct():
    """Simulated node_filesystem_avail_bytes -> percent free, derived from
    how much fake data is still sitting in the sandbox /var/log/journal dir."""
    journal_path = os.path.join(SANDBOX_VAR, "log", "journal")
    total_bytes = sum(
        os.path.getsize(os.path.join(journal_path, f))
        for f in os.listdir(journal_path)
    ) if os.path.isdir(journal_path) else 0
    # Simulated: a 100,000-byte sandbox "disk". Baseline usage is set so
    # that with the full ~17KB of fake journal bloat present, avail_pct
    # lands just under the runbook's 10% threshold -- matching the real
    # incident log's "9% free" starting condition.
    simulated_total = 100_000
    simulated_used_baseline = 74_000
    simulated_free = simulated_total - simulated_used_baseline - total_bytes
    return round(max(simulated_free, 0) / simulated_total * 100, 1)


def detect(threshold_pct):
    pct = sandbox_avail_pct()
    fired = pct < threshold_pct
    print(f"[DETECT] avail_pct={pct}%  threshold={threshold_pct}%  "
          f"{'ALERT FIRED' if fired else 'ok, no alert'}")
    return fired, pct


def diagnose():
    print("[DIAGNOSE] running top-consumers (autonomy=act, read-only, unattended)")
    result = subprocess.run(
        ["bash", "-c", f"du -x -d2 '{SANDBOX_VAR}' 2>/dev/null | sort -rh | head -n 5"],
        capture_output=True, text=True,
    )
    print(result.stdout)
    return result.stdout


def remediate():
    """Propose rotate-logs. Gate it through approval_gate.sh using the
    REAL command text the runbook specifies, before touching anything."""
    real_cmd = "journalctl --vacuum-size=500M"
    print(f"[REMEDIATE] proposing: {real_cmd}  (autonomy=approve, reversible=false)")

    payload = json.dumps({"tool_input": {"command": real_cmd}})
    token = os.environ.get("HUMAN_APPROVAL_TOKEN", "")
    gate = subprocess.run(
        ["bash", "approval_gate.sh", token],
        input=payload, capture_output=True, text=True,
        env=os.environ,
    ) # explicitly pass current env (incl. HUMAN_APPROVAL_TOKEN)
                          # through to the bash subprocess -- Windows doesn't
                          # always inherit this automatically across the
                          # PowerShell -> bash boundary

    if gate.returncode == 2:
        print(f"[GATE] BLOCKED -- waiting for human approval.\n{gate.stderr.strip()}")
        return False

    print("[GATE] ALLOWED -- proceeding with sandboxed remediation "
          "(clearing fake journal data, NOT a real journalctl call)")
    journal_path = os.path.join(SANDBOX_VAR, "log", "journal")
    for f in os.listdir(journal_path):
        os.remove(os.path.join(journal_path, f))
    return True


def verify(expect_pct_above):
    pct = sandbox_avail_pct()
    passed = pct >= expect_pct_above
    print(f"[VERIFY] re-checked avail_pct={pct}%  expect_above={expect_pct_above}%  "
          f"-> {'PASS' if passed else 'FAIL, rollback_if_unmet=page-human'}")
    return passed, pct


def main():
    threshold_pct = 10
    expect_pct_above = 25

    fired, pct = detect(threshold_pct)
    if not fired:
        print("No incident. Exiting.")
        return

    diagnose()

    approved = remediate()
    if not approved:
        print("\n=== INCIDENT PAUSED: awaiting human approval ===")
        print("Re-run with HUMAN_APPROVAL_TOKEN=I-APPROVE to simulate approval.")
        sys.exit(2)

    passed, final_pct = verify(expect_pct_above)
    if passed:
        print(f"\n=== RESOLVED === final avail_pct={final_pct}%")
    else:
        print(f"\n=== VERIFY FAILED === paging human (rollback_if_unmet)")


if __name__ == "__main__":
    main()