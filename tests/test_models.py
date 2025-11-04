"""Tests for database models."""
import pytest
from datetime import datetime
from db.models import User, Task, Payment
from config.constants import UserTier, TaskStatus


def test_user_model():
    """Test User model."""
    user = User(
        telegram_id=123456789,
        username="testuser",
        first_name="Test",
        tier=UserTier.FREE,
    )
    
    assert user.telegram_id == 123456789
    assert user.username == "testuser"
    assert user.tier == UserTier.FREE


def test_task_model():
    """Test Task model."""
    task = Task(
        user_id=1,
        status=TaskStatus.CREATED,
        input_type="youtube",
        input_url="https://youtube.com/watch?v=123",
    )
    
    assert task.user_id == 1
    assert task.status == TaskStatus.CREATED
    assert task.input_type == "youtube"


def test_payment_model():
    """Test Payment model."""
    payment = Payment(
        user_id=1,
        amount=299.0,
        tier=UserTier.PRO,
        status="pending",
    )
    
    assert payment.user_id == 1
    assert payment.amount == 299.0
    assert payment.tier == UserTier.PRO

