"""Tests for Platega payment signature verification."""
import hmac
import hashlib
import pytest


def sign(payload: bytes, secret: str) -> str:
    """Sign payload with secret using HMAC SHA-256."""
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def test_signature_ok():
    """Test that signature generation works correctly."""
    payload = b'{"event":"payment_succeeded","id":"1"}'
    sig = sign(payload, "secret")
    
    assert isinstance(sig, str)
    assert len(sig) == 64  # SHA-256 hex digest is 64 chars


def test_signature_verification():
    """Test signature verification."""
    payload = b'{"event":"payment_succeeded","order_id":"12345"}'
    secret = "test_secret"
    
    signature = sign(payload, secret)
    
    # Verify signature matches
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert signature == expected


def test_signature_different_secrets():
    """Test that different secrets produce different signatures."""
    payload = b'{"event":"payment_succeeded"}'
    
    sig1 = sign(payload, "secret1")
    sig2 = sign(payload, "secret2")
    
    assert sig1 != sig2
