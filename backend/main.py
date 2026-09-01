from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
import os
import razorpay

import models, database, policy

app = FastAPI(title="Razorpay MCP Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Razorpay Client
rzp_key = os.getenv("RAZORPAY_KEY_ID", "")
rzp_secret = os.getenv("RAZORPAY_KEY_SECRET", "")
rzp_client = razorpay.Client(auth=(rzp_key, rzp_secret)) if rzp_key else None

class CartItem(BaseModel):
    product_id: str
    quantity: int

class CheckoutRequest(BaseModel):
    items: list[CartItem]
    agent_reasoning: str

@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=database.engine)
    db = database.SessionLocal()
    
    if db.query(models.Product).count() == 0:
        products = [
            models.Product(id="sku_api_cred", name="API Credits (10k)", price_paise=100000, description="10,000 API calls"),
            models.Product(id="sku_server_xl", name="XL Server Instance", price_paise=800000, description="Monthly XL server lease"),
            models.Product(id="sku_enterprise", name="Enterprise Setup", price_paise=6000000, description="Full enterprise onboarding")
        ]
        db.add_all(products)
        db.commit()
    db.close()

def log_audit(db: Session, action: str, payload: dict, result: dict):
    log = models.AuditLog(action=action, payload=payload, result=result)
    db.add(log)
    db.commit()

@app.get("/api/products")
def list_products(db: Session = Depends(database.get_db)):
    products = db.query(models.Product).all()
    log_audit(db, "list_products", {}, {"count": len(products)})
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price_paise": p.price_paise,
            "stock": p.stock
        }
        for p in products
    ]

@app.post("/api/checkout")
def checkout(req: CheckoutRequest, db: Session = Depends(database.get_db)):
    total_paise = 0
    validated_items = []
    
    for item in req.items:
        prod = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not prod:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        total_paise += (prod.price_paise * item.quantity)
        validated_items.append({"product_id": prod.id, "quantity": item.quantity, "price": prod.price_paise})

    decision = policy.evaluate_order(total_paise, validated_items)
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    
    rzp_order_id = None
    rzp_link = None
    if decision["action"] in ["auto_captured", "pending_approval"]:
        if os.getenv("RAZORPAY_MOCK_MODE") == "true":
            rzp_order_id = f"mock_rzp_{uuid.uuid4().hex[:8]}"
            rzp_link = f"https://mock-razorpay.com/pay/{rzp_order_id}"
        else:
            try:
                payment_link = rzp_client.payment_link.create({
                    "amount": total_paise,
                    "currency": "INR",
                    "accept_partial": False,
                    "description": "AI Agent Automated Purchase",
                    "reference_id": order_id,
                    "notify": {"email": False, "sms": False}
                })
                rzp_order_id = payment_link.get('id')
                rzp_link = payment_link.get('short_url')
            except Exception as e:
                decision["action"] = "blocked"
                decision["reason"] = "Razorpay API Error: Payment link generation failed."
                print(f"Razorpay Exception: {e}")

    new_order = models.Order(
        id=order_id,
        status=decision["action"],
        total_amount_paise=total_paise,
        items=validated_items,
        razorpay_order_id=rzp_order_id,
        razorpay_payment_link=rzp_link,
        policy_reason=decision["reason"]
    )
    db.add(new_order)
    
    log_audit(db, "checkout", req.model_dump(), {
        "order_id": order_id, 
        "decision": decision["action"], 
        "reason": decision["reason"]
    })
    db.commit()
    
    return {
        "order_id": order_id,
        "status": decision["action"],
        "message": decision["reason"],
        "payment_link": rzp_link
    }

@app.get("/api/orders")
def get_orders(db: Session = Depends(database.get_db)):
    return db.query(models.Order).order_by(models.Order.created_at.desc()).all()

@app.get("/api/audit")
def get_audit_logs(db: Session = Depends(database.get_db)):
    return db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).all()

@app.post("/api/orders/{order_id}/approve")
def approve_order(order_id: str, db: Session = Depends(database.get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order and order.status == "pending_approval":
        order.status = "approved"
        log_audit(db, "human_intervention", {"order_id": order_id, "action": "approve"}, {"status": "approved"})
        db.commit()
    return {"status": "success"}

@app.post("/api/orders/{order_id}/reject")
def reject_order(order_id: str, db: Session = Depends(database.get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order and order.status == "pending_approval":
        order.status = "rejected"
        log_audit(db, "human_intervention", {"order_id": order_id, "action": "reject"}, {"status": "rejected"})
        db.commit()
    return {"status": "success"}