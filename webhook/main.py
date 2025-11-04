"""Webhook server for payment notifications."""
import hashlib
import logging
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from config.settings import settings
from config.constants import UserTier
from db.database import AsyncSessionLocal
from db.crud import (
    get_payment_by_external_id,
    update_payment_status,
    update_user_tier,
    get_user_by_telegram_id,
)


async def verify_payment_signature(
    order_id: str,
    amount: float,
    status: str,
    signature: str,
) -> bool:
    """Verify payment signature from webhook."""
    expected_signature = hashlib.sha256(
        f"{order_id}{amount}{status}{settings.PLATEGA_API_KEY}".encode()
    ).hexdigest()
    return signature == expected_signature

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AutoSub Webhook Server")


class PaymentWebhook(BaseModel):
    """Payment webhook data model."""
    order_id: str
    amount: float
    status: str
    signature: str
    external_id: str = None


@app.post("/webhook/payment")
async def handle_payment_webhook(webhook: PaymentWebhook):
    """Handle payment webhook from Platega."""
    logger.info(f"Received payment webhook: {webhook.dict()}")
    
    try:
        # Verify signature
        is_valid = await verify_payment_signature(
            order_id=webhook.order_id,
            amount=webhook.amount,
            status=webhook.status,
            signature=webhook.signature,
        )
        
        if not is_valid:
            logger.error("Invalid payment signature")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Get payment from database
        async with AsyncSessionLocal() as db:
            payment = await get_payment_by_external_id(db, webhook.external_id or webhook.order_id)
            
            if not payment:
                logger.error(f"Payment not found: {webhook.order_id}")
                raise HTTPException(status_code=404, detail="Payment not found")
            
            # Update payment status
            if webhook.status == "success" or webhook.status == "completed":
                await update_payment_status(db, payment.id, "completed")
                
                # Activate subscription
                if payment.tier:
                    # Calculate expiration date
                    if payment.subscription_period == "monthly":
                        expires_at = datetime.utcnow() + timedelta(days=30)
                    elif payment.subscription_period == "yearly":
                        expires_at = datetime.utcnow() + timedelta(days=365)
                    else:
                        expires_at = None
                    
                    # Update user tier
                    await update_user_tier(
                        db,
                        user_id=payment.user_id,
                        tier=payment.tier,
                        expires_at=expires_at,
                    )
                    
                    logger.info(f"User {payment.user_id} upgraded to {payment.tier}")
                
                # TODO: Send notification to user
                
            elif webhook.status == "failed":
                await update_payment_status(db, payment.id, "failed")
                logger.info(f"Payment {payment.id} failed")
        
        return {"status": "ok"}
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

