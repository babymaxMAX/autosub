"""Create admin user script."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.database import AsyncSessionLocal
from db.crud import get_user_by_telegram_id, create_user, update_user_tier
from config.constants import UserTier


async def main():
    """Create admin user."""
    telegram_id = input("Enter Telegram ID: ")
    
    try:
        telegram_id = int(telegram_id)
    except ValueError:
        print("Invalid Telegram ID")
        return
    
    async with AsyncSessionLocal() as db:
        user = await get_user_by_telegram_id(db, telegram_id)
        
        if not user:
            print(f"Creating user with Telegram ID: {telegram_id}")
            user = await create_user(
                db,
                telegram_id=telegram_id,
                username="admin",
                first_name="Admin",
            )
        
        # Upgrade to CREATOR tier
        print(f"Upgrading user to CREATOR tier...")
        await update_user_tier(db, user.id, UserTier.CREATOR, expires_at=None)
        
        print(f"✓ User {telegram_id} is now CREATOR!")


if __name__ == "__main__":
    asyncio.run(main())

