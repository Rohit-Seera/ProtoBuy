<<<<<<< HEAD
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'backend'))
import agent


def reset():
    for d in [agent.CARTS, agent.SESSIONS, agent.LAST_PRODUCTS_BY_SESSION, agent.PENDING_CONFIRMATION, agent.PENDING_PRODUCT_SELECTION]:
        d.clear()


def turn(msg, sid='test'):
    return agent.handle_turn(msg, sid)[0]


def assert_contains(text, needle):
    assert needle.lower() in text.lower(), (needle, text)


def main():
    reset()
    sid = 'critical'

    # Natural-language discovery -> exact single product -> add.
    r = turn('I want to buy a bag', sid)
    assert agent.LAST_PRODUCTS_BY_SESSION[sid][0]['name'] == 'Summit Hiking Backpack 30L'
    r = turn('yes add it', sid)
    assert_contains(r, 'now in your cart')
    assert agent.CARTS[sid][0]['product_id'] == 'sku_003'

    # Checkout confirmation state must never fall through to search.
    r = turn('give me a payment link', sid)
    assert_contains(r, 'above the **₹2,000** autonomous limit')
    r = turn('yes', sid)
    # Credentials may be intentionally absent in a test environment, but the request
    # must reach the payment integration rather than becoming a product search.
    assert 'payment' in r.lower() or 'razorpay' in r.lower() or 'api keys' in r.lower()

    reset()
    sid = 'products'
    for msg, expected in [
        ('add Trekking Pole Set (Pair) to my cart', 'Trekking Pole Set (Pair)'),
        ('add Insulated Steel Water Bottle 1L to my cart', 'Insulated Steel Water Bottle 1L'),
        ('add Compact Camping Tent (2-person) to my cart', 'Compact Camping Tent (2-person)'),
    ]:
        r = turn(msg, sid)
        assert_contains(r, 'now in your cart')
    assert len(agent.CARTS[sid]) == 3

    reset()
    sid = 'sized'
    r = turn('add Alpine Fleece Jacket to my cart', sid)
    assert_contains(r, 'which size')
    r = turn('M size', sid)
    assert_contains(r, 'now in your cart')
    assert agent.CARTS[sid][0]['size'] == 'M'
    r = turn('what is in my cart?', sid)
    assert_contains(r, 'Alpine Fleece Jacket')

    reset()
    sid = 'search'
    r = turn('Find trekking poles under ₹1500', sid)
    assert_contains(r, 'Trekking Pole Set (Pair)')
    assert len(agent.LAST_PRODUCTS_BY_SESSION[sid]) == 1
    r = turn('show me', sid)
    assert_contains(r, '1')
    assert agent.LAST_PRODUCTS_BY_SESSION[sid][0]['id'] == 'sku_007'

    catalog = json.loads((ROOT / 'backend' / 'catalog.json').read_text())['products']
    assert len(catalog) == 16
    print('Critical conversation and catalog tests: PASS')


if __name__ == '__main__':
    main()
=======
import json, os, sys
from pathlib import Path
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'backend'))
import agent

def reset():
    for d in [agent.CARTS,agent.SESSIONS,agent.LAST_PRODUCTS_BY_SESSION,agent.PENDING_CONFIRMATION,agent.PENDING_PRODUCT_SELECTION]: d.clear()
def turn(msg,sid='test'): return agent.handle_turn(msg,sid)[0]
def contains(text,needle): assert needle.lower() in text.lower(),(needle,text)
def main():
    reset(); sid='critical'
    r=turn('I want to buy a bag',sid); assert agent.LAST_PRODUCTS_BY_SESSION[sid][0]['name']=='Summit Hiking Backpack 30L'
    r=turn('yes add it',sid); contains(r,'now in your cart')
    assert agent.CARTS[sid][0]['product_id']=='sku_003'
    r=turn('give me a payment link',sid); contains(r,'above the **₹2,000** autonomous limit')
    r=turn('yes',sid); assert 'payment' in r.lower() or 'razorpay' in r.lower() or 'api keys' in r.lower()
    reset(); sid='products'
    for msg in ['add Trekking Pole Set (Pair) to my cart','add Insulated Steel Water Bottle 1L to my cart','add Compact Camping Tent (2-person) to my cart']:
        contains(turn(msg,sid),'now in your cart')
    assert len(agent.CARTS[sid])==3
    reset(); sid='sized'; contains(turn('add Alpine Fleece Jacket to my cart',sid),'which size'); contains(turn('M size',sid),'now in your cart'); assert agent.CARTS[sid][0]['size']=='M'; contains(turn('what is in my cart?',sid),'Alpine Fleece Jacket')
    reset(); sid='search'; contains(turn('Find trekking poles under ₹1500',sid),'Trekking Pole Set (Pair)'); assert len(agent.LAST_PRODUCTS_BY_SESSION[sid])==1; contains(turn('show me',sid),'1'); assert agent.LAST_PRODUCTS_BY_SESSION[sid][0]['id']=='sku_007'
    catalog=json.loads((ROOT/'backend'/'catalog.json').read_text())['products']; assert len(catalog)==16
    print('Critical conversation and catalog tests: PASS')
if __name__=='__main__': main()
>>>>>>> 7ea5bbcd2494fb94cac256749d427ab19d927daa
