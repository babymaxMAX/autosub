"""Database models."""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Enum, 
    ForeignKey, Text, Float, JSON, BigInteger
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from config.constants import UserTier, TaskStatus

Base = declarative_base()


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), default="ru")
    
    # Subscription
    tier = Column(Enum(UserTier), default=UserTier.FREE, nullable=False)
    tier_expires_at = Column(DateTime, nullable=True)
    
    # Usage statistics
    tasks_today = Column(Integer, default=0)
    tasks_total = Column(Integer, default=0)
    last_task_date = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, tier={self.tier})>"


class Task(Base):
    """Video processing task model."""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Task info
    status = Column(Enum(TaskStatus), default=TaskStatus.CREATED, nullable=False, index=True)
    priority = Column(Integer, default=3)
    
    # Input
    input_type = Column(String(50))  # file, youtube, tiktok, instagram
    input_url = Column(Text, nullable=True)
    input_file_id = Column(String(255), nullable=True)
    input_file_path = Column(Text, nullable=True)
    
    # Video metadata
    duration = Column(Float, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    file_size = Column(BigInteger, nullable=True)
    
    # Processing options
    source_language = Column(String(10), default="auto")
    target_language = Column(String(10), nullable=True)
    generate_subtitles = Column(Boolean, default=True)
    translate = Column(Boolean, default=False)
    voiceover = Column(Boolean, default=False)
    vertical_format = Column(Boolean, default=False)
    add_watermark = Column(Boolean, default=True)
    
    # Output
    output_file_path = Column(Text, nullable=True)
    output_file_id = Column(String(255), nullable=True)
    subtitles_file_path = Column(Text, nullable=True)
    
    # Processing info
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)
    worker_id = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task(id={self.id}, user_id={self.user_id}, status={self.status})>"


class Payment(Base):
    """Payment model."""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Payment info
    external_id = Column(String(255), unique=True, nullable=True, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="RUB")
    
    # Subscription info
    tier = Column(Enum(UserTier), nullable=True)
    subscription_period = Column(String(50), nullable=True)  # monthly, yearly
    
    # Payment status
    status = Column(String(50), default="pending")  # pending, completed, failed, refunded
    payment_method = Column(String(50), nullable=True)
    
    # Payment metadata
    payment_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, user_id={self.user_id}, amount={self.amount}, status={self.status})>"


class SystemLog(Base):
    """System logs for monitoring."""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True)
    level = Column(String(20), nullable=False, index=True)  # INFO, WARNING, ERROR, CRITICAL
    message = Column(Text, nullable=False)
    module = Column(String(255), nullable=True)
    user_id = Column(Integer, nullable=True, index=True)
    task_id = Column(Integer, nullable=True, index=True)
    log_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<SystemLog(id={self.id}, level={self.level}, message={self.message[:50]})>"

