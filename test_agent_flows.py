<<<<<<< HEAD
"""End-to-end regression tests for ProtoBuy's rebuilt intent-first agent.

These tests do not call Groq or Razorpay. The LLM and payment layer are replaced with
small fakes so the application's behavior can be verified deterministically.
"""

import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
import agent


class FakeLLM:
    def __init__(self):
        self.calls = 0

    def parse(self, text):
        self.calls += 1
        t = text.lower()
        if t == "hi":
            intent = "greeting"
        elif "payment link" in t:
            intent = "checkout"
        elif "buy" in t and "bag" in t:
            intent = "search"
        else:
            intent = "search"
        return {
            "intent": intent,
            "query": text,
            "product_hint": "",
            "size": "",
            "quantity": 1,
            "budget": None,
            "confidence": 0.99,
        }

    @property
    def chat(self):
        fake = self

        class Completions:
            @staticmethod
            def create(**kwargs):
                text = kwargs["messages"][-1]["content"].split("Parse this latest buyer message:", 1)[-1].strip()
                payload = fake.parse(text)
                return SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(content=__import__("json").dumps(payload)))]
                )

        return SimpleNamespace(completions=Completions())


def reset():
    agent.CARTS.clear()
    agent.SESSIONS.clear()
    agent.LAST_PRODUCTS_BY_SESSION.clear()
    agent.PENDING_CONFIRMATION.clear()
    agent.LAST_SEARCH_RESULTS.clear()
    agent.LAST_CHECKOUT_RESULT.clear()
    agent.LAST_GROWTH_SIGNAL.clear()


def main():
    # Use the actual application fallback for search/product matching, and a fake LLM
    # only to prove that structured intent parsing integrates cleanly.
    reset()
    original_client = agent.client
    original_order = agent.create_order
    original_link = agent.create_payment_link
    agent.client = FakeLLM()
    agent.create_order = lambda total, receipt, notes=None: {"id": "order_test"}
    agent.create_payment_link = lambda total, description="": {"short_url": "https://rzp.io/i/test"}

    sid = "flow-test"
    r, *_ = agent.handle_turn("hi", sid)
    assert "ProtoBuy" in r

    r, *_ = agent.handle_turn("i want to purchase a bag", sid)
    assert [p["name"] for p in agent.LAST_PRODUCTS_BY_SESSION[sid]] == ["Summit Hiking Backpack 30L"]

    r, *_ = agent.handle_turn("yes add it", sid)
    assert agent.CARTS[sid][0]["product_id"] == "sku_003"

    r, *_ = agent.handle_turn("give me payment link", sid)
    assert sid in agent.PENDING_CONFIRMATION
    assert "confirmation" in r.lower()

    r, *_rest = agent.handle_turn("yes", sid)
    assert "checkout" in r.lower()
    assert not agent.CARTS[sid]

    # Specific search should return the exact product, not generic accessories.
    reset()
    r, *_ = agent.handle_turn("find trekking poles under ₹1500", "pole-test")
    assert [p["name"] for p in agent.LAST_PRODUCTS_BY_SESSION["pole-test"]] == ["Trekking Pole Set (Pair)"]

    # Follow-up stays anchored to the previous results.
    r, *_ = agent.handle_turn("show me", "pole-test")
    assert agent.LAST_PRODUCTS_BY_SESSION["pole-test"][0]["id"] == "sku_007"

    # Ambiguous assent after multiple products never invents a selection.
    reset()
    sid = "multi-test"
    agent.handle_turn("what can I get under ₹2000?", sid)
    r, *_ = agent.handle_turn("yes add it", sid)
    assert "won’t guess" in r.lower()
    assert not agent.CARTS.get(sid)

    agent.client = original_client
    agent.create_order = original_order
    agent.create_payment_link = original_link
    print("ProtoBuy agent flow tests: PASS")


if __name__ == "__main__":
    main()
=======
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),'backend'))
import agent

def reset():
    agent.CARTS.clear(); agent.SESSIONS.clear(); agent.LAST_PRODUCTS_BY_SESSION.clear(); agent.PENDING_CONFIRMATION.clear(); agent.LAST_SEARCH_RESULTS.clear(); agent.LAST_CHECKOUT_RESULT.clear(); agent.LAST_GROWTH_SIGNAL.clear(); agent.PENDING_PRODUCT_SELECTION.clear()
def main():
    reset(); sid='flow-test'
    r,*_=agent.handle_turn('hi',sid); assert 'ProtoBuy' in r
    r,*_=agent.handle_turn('i want to purchase a bag',sid); assert [p['name'] for p in agent.LAST_PRODUCTS_BY_SESSION[sid]]==['Summit Hiking Backpack 30L']
    r,*_=agent.handle_turn('yes add it',sid); assert agent.CARTS[sid][0]['product_id']=='sku_003'
    r,*_=agent.handle_turn('give me payment link',sid); assert sid in agent.PENDING_CONFIRMATION and 'confirmation' in r.lower()
    original_order,original_link=agent.create_order,agent.create_payment_link
    agent.create_order=lambda total,receipt,notes=None:{'id':'order_test'}
    agent.create_payment_link=lambda total,description='':{'short_url':'https://rzp.io/i/test'}
    r,*_=agent.handle_turn('yes',sid); assert 'checkout' in r.lower() and not agent.CARTS[sid]
    agent.create_order,agent.create_payment_link=original_order,original_link
    reset(); r,*_=agent.handle_turn('find trekking poles under ₹1500','pole-test'); assert [p['name'] for p in agent.LAST_PRODUCTS_BY_SESSION['pole-test']]==['Trekking Pole Set (Pair)']; r,*_=agent.handle_turn('show me','pole-test'); assert agent.LAST_PRODUCTS_BY_SESSION['pole-test'][0]['id']=='sku_007'
    print('ProtoBuy agent flow tests: PASS')
if __name__=='__main__': main()
>>>>>>> 7ea5bbcd2494fb94cac256749d427ab19d927daa
