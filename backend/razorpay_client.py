"""
Thin wrapper around Razorpay's test-mode REST API, called directly via
`requests` (HTTP Basic Auth) instead of the official `razorpay` Python SDK.

Why not the SDK: the official SDK still imports `pkg_resources`, which
recent `setuptools` releases have removed. That makes the SDK unreliable
across Python/setuptools version combinations. Razorpay's API is plain
JSON over HTTPS with HTTP Basic Auth (key_id:key_secret) — no SDK needed,
so calling it directly sidesteps the whole dependency problem.

Deliberately surfaces FOUR distinct, realistic failure modes instead of one
generic try/except, so the agent can react differently to each:

  1. authentication_error -> bad/missing API keys (setup problem)
  2. invalid_request      -> e.g. invalid amount, malformed payload
  3. connection_error     -> Razorpay unreachable / network issue
  4. server_error         -> Razorpay's own servers erroring (5xx)

Requires environment variables:
  RAZORPAY_KEY_ID
  RAZORPAY_KEY_SECRET
(get test-mode keys from https://dashboard.razorpay.com/app/keys after
switching the dashboard to Test Mode)
"""

import os
import requests
from requests.auth import HTTPBasicAuth

from guardrails import log_event

BASE_URL = "https://api.razorpay.com/v1"


class PaymentError(Exception):
    """Base class for our own payment-flow errors, carries a `kind` for the agent to branch on."""
    def __init__(self, kind: str, message: str):
        self.kind = kind
        self.message = message
        super().__init__(message)


def _auth() -> HTTPBasicAuth:
    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")
    if not key_id or not key_secret:
        raise PaymentError(
            "authentication_error",
            "Razorpay API keys are missing. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in .env (test mode keys).",
        )
    return HTTPBasicAuth(key_id, key_secret)


def _post(path: str, payload: dict) -> dict:
    """Shared POST helper — classifies the response into one of our four failure kinds."""
    auth = _auth()
    try:
        response = requests.post(f"{BASE_URL}{path}", json=payload, auth=auth, timeout=10)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        raise PaymentError("connection_error", "Could not reach Razorpay right now. This is usually temporary.")

    if response.status_code == 401:
        raise PaymentError("authentication_error", "Razorpay rejected the API keys. Check RAZORPAY_KEY_ID/SECRET in .env.")
    if response.status_code == 400:
        try:
            detail = response.json().get("error", {}).get("description", "Invalid request.")
        except ValueError:
            detail = "Invalid request."
        raise PaymentError("invalid_request", f"Razorpay rejected the request: {detail}")
    if response.status_code >= 500:
        raise PaymentError("server_error", "Razorpay is having an issue on their end right now.")
    if not response.ok:
        raise PaymentError("invalid_request", f"Razorpay returned an unexpected error (status {response.status_code}).")

    return response.json()


def create_order(amount_rupees: int, receipt: str, notes: dict | None = None) -> dict:
    """
    Creates a Razorpay Order (test mode). Amount must be passed in paise to Razorpay.
    Returns the order dict on success, raises PaymentError with a `.kind` on failure.
    """
    try:
        order = _post("/orders", {
            "amount": amount_rupees * 100,  # paise
            "currency": "INR",
            "receipt": receipt,
            "notes": notes or {},
        })
        log_event("order_created", f"Order created for \u20b9{amount_rupees}", {"order_id": order.get("id")})
        return order
    except PaymentError as e:
        log_event("order_failed", f"{e.kind}: {e.message}", {"amount": amount_rupees})
        raise


def create_payment_link(amount_rupees: int, description: str, customer_name: str = "Test Buyer") -> dict:
    """
    Creates a Razorpay Payment Link (test mode) for the given amount.
    """
    try:
        link = _post("/payment_links", {
            "amount": amount_rupees * 100,
            "currency": "INR",
            "description": description,
            "customer": {"name": customer_name},
            "notify": {"sms": False, "email": False},
        })
        log_event("payment_link_created", f"Payment link created for \u20b9{amount_rupees}", {"link_id": link.get("id"), "short_url": link.get("short_url")})
        return link
    except PaymentError as e:
        log_event("payment_link_failed", f"{e.kind}: {e.message}", {"amount": amount_rupees})
        raise
