<<<<<<< HEAD
from backend.agent import handle_turn, SESSIONS, CARTS, LAST_PRODUCTS_BY_SESSION, PENDING_CONFIRMATION, PENDING_PRODUCT_SELECTION

def reset(sid):
    SESSIONS.pop(sid, None); CARTS.pop(sid, None); LAST_PRODUCTS_BY_SESSION.pop(sid, None); PENDING_CONFIRMATION.pop(sid, None); PENDING_PRODUCT_SELECTION.pop(sid, None)

def main():
    sid='test_no_cards'
    reset(sid)
    r, *_ = handle_turn('Find trekking poles under ₹1500', sid)
    assert 'Trekking Pole Set (Pair)' in r
    assert 'Recommended for you' not in r
    r, *_ = handle_turn('show me', sid)
    assert 'Trekking Pole Set (Pair)' in r
    r, *_ = handle_turn('I want to purchase a bag', sid)
    assert 'Summit Hiking Backpack 30L' in r
    r, *_ = handle_turn('yes add it', sid)
    assert 'now in your cart' in r or 'is now in your cart' in r
    r, *_ = handle_turn('give me payment link', sid)
    assert 'confirmation' in r.lower() or 'above' in r.lower()
    print('No-chat-cards / text-confirmation tests: PASS')
if __name__=='__main__': main()
=======
import os,sys
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'backend'))
from agent import handle_turn,SESSIONS,CARTS,LAST_PRODUCTS_BY_SESSION,PENDING_CONFIRMATION,PENDING_PRODUCT_SELECTION

def reset(sid):
    for d in (SESSIONS,CARTS,LAST_PRODUCTS_BY_SESSION,PENDING_CONFIRMATION,PENDING_PRODUCT_SELECTION):d.pop(sid,None)
def main():
    sid='test_no_cards';reset(sid)
    r,*_=handle_turn('Find trekking poles under ₹1500',sid);assert 'Trekking Pole Set (Pair)' in r;assert 'Recommended for you' not in r
    r,*_=handle_turn('show me',sid);assert 'Trekking Pole Set (Pair)' in r
    r,*_=handle_turn('I want to purchase a bag',sid);assert 'Summit Hiking Backpack 30L' in r
    r,*_=handle_turn('yes add it',sid);assert 'now in your cart' in r
    r,*_=handle_turn('give me payment link',sid);assert 'confirmation' in r.lower() or 'above' in r.lower()
    print('No-chat-cards / text-confirmation tests: PASS')
if __name__=='__main__':main()
>>>>>>> 7ea5bbcd2494fb94cac256749d427ab19d927daa
