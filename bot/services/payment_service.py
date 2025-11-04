"""Payment service for Platega integration."""
import hashlib
import httpx
from typing import Optional
from config.settings import settings
from config.constants import UserTier
from db.crud import create_payment
from db.database import AsyncSessionLocal


async def create_payment_link(
    user_id: int,
    amount: float,
    description: str,
    tier: Optional[UserTier] = None,
    period: Optional[str] = None,
) -> str:
    """Create payment link via Platega."""
    
    # Create payment in database
    async with AsyncSessionLocal() as db:
        payment = await create_payment(
            db,
            user_id=user_id,
            amount=amount,
            tier=tier,
            subscription_period=period,
            metadata={
                "description": description,
            }
        )
    
    # Generate payment signature
    signature_string = f"{settings.PLATEGA_PROJECT_ID}{amount}{payment.id}{settings.PLATEGA_API_KEY}"
    signature = hashlib.sha256(signature_string.encode()).hexdigest()
    
    # Create payment URL (this is simplified - adjust based on actual Platega API)
    payment_url = (
        f"https://platega.com/payment?"
        f"project_id={settings.PLATEGA_PROJECT_ID}&"
        f"amount={amount}&"
        f"order_id={payment.id}&"
        f"description={description}&"
        f"signature={signature}&"
        f"success_url={settings.PLATEGA_SUCCESS_URL}&"
        f"fail_url={settings.PLATEGA_FAIL_URL}"
    )
    
    return payment_url


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

