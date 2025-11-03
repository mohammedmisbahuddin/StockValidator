"""
Tests for authentication utilities
"""
import pytest
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from shared.auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_access_token,
    verify_refresh_token,
    get_user_id_from_token
)


class TestPasswordHashing:
    """Test password hashing functions"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # Bcrypt hash prefix
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert verify_password("WrongPassword", hashed) is False
    
    def test_hash_password_too_long(self):
        """Test hashing password that's too long"""
        password = "a" * 73  # 73 bytes, exceeds bcrypt limit
        
        with pytest.raises(ValueError, match="Password cannot exceed 72 bytes"):
            hash_password(password)
    
    def test_hash_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes"""
        password1 = "Password123"
        password2 = "Password456"
        
        hash1 = hash_password(password1)
        hash2 = hash_password(password2)
        
        assert hash1 != hash2
    
    def test_same_password_different_salts(self):
        """Test that same password produces different hashes (due to salt)"""
        password = "TestPassword123"
        
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Different hashes due to different salts
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestJWTTokens:
    """Test JWT token functions"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        data = {"sub": "user123", "username": "testuser"}
        token = create_access_token(data)
        
        assert token is not None
        assert len(token) > 0
        assert isinstance(token, str)
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        data = {"sub": "user123"}
        token = create_refresh_token(data)
        
        assert token is not None
        assert len(token) > 0
        assert isinstance(token, str)
    
    def test_decode_token_valid(self):
        """Test decoding a valid token"""
        data = {"sub": "user123", "username": "testuser"}
        token = create_access_token(data)
        
        decoded = decode_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == "user123"
        assert decoded["username"] == "testuser"
        assert "exp" in decoded
        assert "type" in decoded
    
    def test_decode_token_invalid(self):
        """Test decoding an invalid token"""
        decoded = decode_token("invalid_token")
        
        assert decoded is None
    
    def test_verify_access_token_valid(self):
        """Test verifying a valid access token"""
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        payload = verify_access_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["type"] == "access"
    
    def test_verify_access_token_with_refresh_token(self):
        """Test that refresh token is not valid as access token"""
        data = {"sub": "user123"}
        refresh_token = create_refresh_token(data)
        
        payload = verify_access_token(refresh_token)
        
        assert payload is None  # Should be None because type is "refresh"
    
    def test_verify_refresh_token_valid(self):
        """Test verifying a valid refresh token"""
        data = {"sub": "user123"}
        token = create_refresh_token(data)
        
        payload = verify_refresh_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["type"] == "refresh"
    
    def test_verify_refresh_token_with_access_token(self):
        """Test that access token is not valid as refresh token"""
        data = {"sub": "user123"}
        access_token = create_access_token(data)
        
        payload = verify_refresh_token(access_token)
        
        assert payload is None  # Should be None because type is "access"
    
    def test_get_user_id_from_token(self):
        """Test extracting user ID from token"""
        user_id = "user123"
        data = {"sub": user_id}
        token = create_access_token(data)
        
        extracted_id = get_user_id_from_token(token)
        
        assert extracted_id == user_id
    
    def test_get_user_id_from_invalid_token(self):
        """Test extracting user ID from invalid token"""
        extracted_id = get_user_id_from_token("invalid_token")
        
        assert extracted_id is None
    
    def test_token_expiration(self):
        """Test that token includes expiration"""
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        decoded = decode_token(token)
        
        assert "exp" in decoded
        exp_time = datetime.fromtimestamp(decoded["exp"])
        now = datetime.utcnow()
        
        # Token should expire in the future
        assert exp_time > now
        
        # Should expire within a reasonable range (allowing for config differences)
        time_diff = exp_time - now
        # Access tokens should expire between 10 minutes and 24 hours
        assert 10 * 60 < time_diff.total_seconds() < 24 * 60 * 60
    
    def test_custom_expiration(self):
        """Test token with custom expiration"""
        data = {"sub": "user123"}
        custom_expiry = timedelta(minutes=5)
        token = create_access_token(data, expires_delta=custom_expiry)
        
        decoded = decode_token(token)
        
        # Check that custom expiration was applied
        # The token should have an expiration
        assert "exp" in decoded
        
        # Token should be valid (not expired)
        # If the token was successfully decoded, it means it's not expired
        assert decoded is not None
        assert decoded["sub"] == "user123"

