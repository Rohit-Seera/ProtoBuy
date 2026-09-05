import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

<<<<<<< HEAD
from agent import (
    CARTS,
    LAST_PRODUCTS_BY_SESSION,
    SESSIONS,
    handle_turn,
    load_catalog,
    _tool_add_to_cart,
    _tool_checkout_cart,
    _tool_remove_from_cart,
)
from guardrails import get_audit_log, log_event

app = FastAPI(title="ProtoBuy Agent API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

=======
from agent import CARTS, LAST_PRODUCTS_BY_SESSION, SESSIONS, handle_turn, load_catalog, _tool_add_to_cart, _tool_checkout_cart, _tool_remove_from_cart
from guardrails import get_audit_log, log_event

app = FastAPI(title="ProtoBuy Agent API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
>>>>>>> 7ea5bbcd2494fb94cac256749d427ab19d927daa

class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1, max_length=2000)
<<<<<<< HEAD


=======
>>>>>>> 7ea5bbcd2494fb94cac256749d427ab19d927daa
class CartAddRequest(BaseModel):
    session_id: str
    sku: str
    quantity: int = Field(default=1, ge=1, le=20)
    size: str = "one_size"
<<<<<<< HEAD


class CartRemoveRequest(BaseModel):
    session_id: str
    index: int = Field(ge=0)


=======
class CartRemoveRequest(BaseModel):
    session_id: str
    index: int = Field(ge=0)
>>>>>>> 7ea5bbcd2494fb94cac256749d427ab19d927daa
class CheckoutRequest(BaseModel):
    session_id: str
    confirmed: bool = False
    raw_message: str = ""
<<<<<<< HEAD

=======
>>>>>>> 7ea5bbcd2494fb94cac256749d427ab19d927daa

@app.get("/health")
def health(): return {"status":"ok"}
@app.get("/catalog")
<<<<<<< HEAD
def catalog():
    return load_catalog()


=======
def catalog(): return load_catalog()
>>>>>>> 7ea5bbcd2494fb94cac256749d427ab19d927daa
@app.post("/chat")
def chat(req: ChatRequest):
    try:
        reply, conversation, payment, growth = handle_turn(req.message, req.session_id)
<<<<<<< HEAD
        products = LAST_PRODUCTS_BY_SESSION.get(req.session_id, [])
        return {"reply": reply, "products": products, "payment": payment, "growth": growth}
    except Exception as exc:
        log_event("chat_error", "Unexpected error while handling chat turn.", {"error_type": type(exc).__name__})
        raise HTTPException(status_code=500, detail="The agent could not complete this request. Please try again.")


@app.get("/cart")
def cart(session_id: str):
    items = CARTS.get(session_id, [])
    total = sum(i["price"] * i["quantity"] for i in items)
    return {"items": items, "total": total}


@app.post("/cart/add")
def cart_add(req: CartAddRequest):
    result = _tool_add_to_cart(req.sku, req.size, req.quantity, req.session_id)
    if not result.get("success"):
        raise HTTPException(status_code=409, detail=result.get("message") or "Unable to add item")
    return result


@app.post("/cart/remove")
def cart_remove(req: CartRemoveRequest):
    items = CARTS.get(req.session_id, [])
    if req.index >= len(items):
        raise HTTPException(status_code=404, detail="Cart item not found")
    item = items[req.index]
    return _tool_remove_from_cart(item["product_id"], item["size"], req.session_id)


@app.post("/cart/clear")
def cart_clear(session_id: str):
    CARTS[session_id] = []
    return {"success": True, "items": [], "total": 0}


@app.post("/checkout")
def checkout(req: CheckoutRequest):
    return _tool_checkout_cart(req.confirmed, req.session_id, req.raw_message)


@app.post("/audit-log/clear")
def audit_log_clear():
    path = os.path.join(os.path.dirname(__file__), "audit_log.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write("[]")
    return {"success": True, "entries": []}


@app.get("/history")
def history(session_id: str):
    messages = [m for m in SESSIONS.get(session_id, []) if m.get("role") in ("user", "assistant")]
    return {"messages": messages}


@app.get("/audit-log")
def audit_log():
    return {"entries": get_audit_log()}
=======
        return {"reply":reply,"products":LAST_PRODUCTS_BY_SESSION.get(req.session_id,[]),"payment":payment,"growth":growth}
    except Exception as exc:
        log_event("chat_error","Unexpected error while handling chat turn.",{"error_type":type(exc).__name__})
        raise HTTPException(status_code=500, detail="The agent could not complete this request. Please try again.")
@app.get("/cart")
def cart(session_id: str):
    items=CARTS.get(session_id,[]); return {"items":items,"total":sum(i["price"]*i["quantity"] for i in items)}
@app.post("/cart/add")
def cart_add(req: CartAddRequest):
    result=_tool_add_to_cart(req.sku,req.size,req.quantity,req.session_id)
    if not result.get("success"): raise HTTPException(status_code=409,detail=result.get("message") or "Unable to add item")
    return result
@app.post("/cart/remove")
def cart_remove(req: CartRemoveRequest):
    items=CARTS.get(req.session_id,[])
    if req.index>=len(items): raise HTTPException(status_code=404,detail="Cart item not found")
    item=items[req.index]; return _tool_remove_from_cart(item["product_id"],item["size"],req.session_id)
@app.post("/cart/clear")
def cart_clear(session_id: str):
    CARTS[session_id]=[]; return {"success":True,"items":[],"total":0}
@app.post("/checkout")
def checkout(req: CheckoutRequest): return _tool_checkout_cart(req.confirmed,req.session_id,req.raw_message)
@app.post("/audit-log/clear")
def audit_log_clear():
    path=os.path.join(os.path.dirname(__file__),"audit_log.json")
    with open(path,"w",encoding="utf-8") as f:f.write("[]")
    return {"success":True,"entries":[]}
@app.get("/history")
def history(session_id: str):
    return {"messages":[m for m in SESSIONS.get(session_id,[]) if m.get("role") in ("user","assistant")]}
@app.get("/audit-log")
def audit_log(): return {"entries":get_audit_log()}
>>>>>>> 7ea5bbcd2494fb94cac256749d427ab19d927daa
