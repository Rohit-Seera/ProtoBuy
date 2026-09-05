"""
Guardrails: enforces the "bounded and gated" requirement.

- AUTONOMY_LIMIT: max amount (INR) the agent can approve on its own.
  Anything above this requires explicit human confirmation before payment.
- Every guardrail decision and every agent action is written to an audit log
  with a timestamp and a plain-language reason, so nothing the agent does is a black box.
"""

import json
import os
from datetime import datetime, timezone

AUTONOMY_LIMIT = int(os.getenv("AUTONOMY_LIMIT", "2000"))  # INR

# Vercel Functions have ephemeral instances and only /tmp is writable at runtime.
# Local development keeps using backend/audit_log.json.
AUDIT_LOG_PATH = (
    os.path.join("/tmp", "protobuy_audit_log.json")
    if os.getenv("VERCEL")
    else os.path.join(os.path.dirname(__file__), "audit_log.json")
)


def _load_log():
    if not os.path.exists(AUDIT_LOG_PATH):
        return []
    with open(AUDIT_LOG_PATH, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save_log(entries):
    with open(AUDIT_LOG_PATH, "w") as f:
        json.dump(entries, f, indent=2)


def log_event(event_type: str, reason: str, data: dict | None = None):
    """Append a single audit entry. Called at every decision point."""
    entries = _load_log()
    entries.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "reason": reason,
        "data": data or {},
    })
    _save_log(entries)
    return entries[-1]


def get_audit_log():
    return _load_log()


def clear_audit_log():
    """Clear the current runtime audit trail."""
    _save_log([])


def check_spending_limit(amount: int) -> dict:
    """
    Returns a decision dict:
      {"autonomous": bool, "reason": str}
    autonomous=True  -> agent may proceed without asking a human
    autonomous=False -> agent must get explicit human confirmation first
    """
    if amount <= AUTONOMY_LIMIT:
        decision = {
            "autonomous": True,
            "reason": f"Amount ₹{amount} is within the autonomy limit of ₹{AUTONOMY_LIMIT}, proceeding without human confirmation.",
        }
    else:
        decision = {
            "autonomous": False,
            "reason": f"Amount ₹{amount} exceeds the autonomy limit of ₹{AUTONOMY_LIMIT}, human confirmation is required before payment.",
        }
    log_event("guardrail_check", decision["reason"], {"amount": amount, "autonomous": decision["autonomous"]})
    return decision


def detect_injection_attempt(text: str) -> bool:
    """
    Very simple heuristic defense: catalog/product text should never be treated
    as instructions to the agent. If suspicious imperative phrases show up in
    data that is supposed to be descriptive (not conversational), flag it.
    This is intentionally simple for the demo — the real defense is architectural:
    the system prompt tells the agent that catalog content is DATA, never
    INSTRUCTIONS, no matter what it says.
    """
    suspicious_markers = [
        "ignore your", "ignore the", "always approve", "skip confirmation",
        "bypass", "override the limit", "disregard the limit", "as the ai assistant",
    ]
    lowered = text.lower()
    return any(marker in lowered for marker in suspicious_markers)
