import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

AUTO_APPROVE_LIMIT = int(os.getenv("AUTO_APPROVE_LIMIT_PAISE", 500000))
HARD_MAX_LIMIT = int(os.getenv("HARD_MAX_PAISE", 5000000))
ALLOWED_SKUS = os.getenv("ALLOWED_SKUS", "*")

def evaluate_order(total_amount_paise: int, items: list) -> dict:
    # Convert paise to formatted INR strings for the human UI
    total_inr = f"₹{total_amount_paise / 100:,.0f}"
    hard_max_inr = f"₹{HARD_MAX_LIMIT / 100:,.0f}"
    auto_limit_inr = f"₹{AUTO_APPROVE_LIMIT / 100:,.0f}"

    if ALLOWED_SKUS != "*":
        allowed_list = [sku.strip() for sku in ALLOWED_SKUS.split(",")]
        for item in items:
            if item.get("product_id") not in allowed_list:
                return {"action": "blocked", "reason": f"SKU '{item.get('product_id')}' is restricted from AI purchase."}

    if total_amount_paise > HARD_MAX_LIMIT:
        return {"action": "blocked", "reason": f"Order of {total_inr} exceeds absolute maximum budget of {hard_max_inr}."}

    if total_amount_paise > AUTO_APPROVE_LIMIT:
        return {"action": "pending_approval", "reason": f"Order of {total_inr} exceeds {auto_limit_inr} auto-approval limit. Requires human sign-off."}

    return {"action": "auto_captured", "reason": "Order within budget and SKU parameters. Auto-approved."}