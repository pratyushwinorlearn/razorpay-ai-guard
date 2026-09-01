from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price_paise = Column(Integer)
    stock = Column(Integer, default=10)

class Order(Base):
    __tablename__ = "orders"
    id = Column(String, primary_key=True, index=True)
    status = Column(String, default="pending_approval")
    total_amount_paise = Column(Integer)
    items = Column(JSON)
    razorpay_order_id = Column(String, nullable=True)
    razorpay_payment_link = Column(String, nullable=True)
    policy_reason = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, default="groq-buyer-01")
    action = Column(String)
    payload = Column(JSON)
    result = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())