"""self_healing_loop_ungated.py — REPRODUCES the node-4 failure mode.
The gate is deliberately skipped here (autonomy misconfigured to ACT),
exactly matching sample_incident.log's node-4 counter-example. This
file exists ONLY to prove what happens without the gate -- it is not
how the real loop should ever run. Sandbox only, per the assignment's
sandbox rule."""
import os

SANDBOX_VAR = os.path.join(os.path.dirname(__file__), "sandbox", "var")


def sandbox_avail_pct():
    journal_path = os.path.join(SANDBOX_VAR, "log", "journal")
    total_bytes = sum(
        os.path.getsize(os.path.join(journal_path, f))
        for f in os.listdir(journal_path)
    ) if os.path.isdir(journal_path) else 0
    simulated_total = 100_000
    simulated_used_baseline = 74_000
    simulated_free = simulated_total - simulated_used_baseline - total_bytes
    return round(max(simulated_free, 0) / simulated_total * 100, 1)


def main():
    pct = sandbox_avail_pct()
    print(f"[DETECT] avail_pct={pct}%  threshold=10%  ALERT FIRED")
    print("[DIAGNOSE] top-consumers: journal bloat identified")
    print("[REMEDIATE] proposing: journalctl --vacuum-size=500M  "
          "autonomy=ACT(misconfigured)")
    print("[ACT] ...no gate called. Executing immediately, unattended...")

    journal_path = os.path.join(SANDBOX_VAR, "log", "journal")
    for f in os.listdir(journal_path):
        os.remove(os.path.join(journal_path, f))

    final_pct = sandbox_avail_pct()
    print(f"[VERIFY] avail_pct={final_pct}%  -> resolved, NO human ever "
          f"consulted, NO approval on record")
    print("\n=== INCIDENT 'RESOLVED' -- but see the cost this actually "
          "represents in a real system ===")
    print("Simulated FinOps-equivalent: in the real node-4 case, the "
          "SAME misconfiguration on a different action (scale-volume) "
          "produced +$1840/mo unplanned spend with zero approval on "
          "record. This run demonstrates the MECHANISM (unattended "
          "state-change, no audit trail of human sign-off), not the "
          "dollar figure, since journalctl deletion itself has no "
          "direct cost -- the danger here is data loss + no "
          "accountability trail, not spend.")


if __name__ == "__main__":
    main()