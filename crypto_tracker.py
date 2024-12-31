import secrets
from cryptography.fernet import Fernet
import logging
from typing import Dict, Optional
import requests
from utils import validate_input

logger = logging.getLogger(__name__)

class CryptoTracker:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)
        
    def encrypt_data(self, data: str) -> bytes:
        """Encrypt sensitive data."""
        try:
            return self.cipher_suite.encrypt(data.encode())
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise

    def get_crypto_price(self, symbol: str) -> Optional[float]:
        """Get cryptocurrency price with proper error handling and validation."""
        try:
            if not validate_input(symbol, str):
                raise ValueError("Invalid symbol format")

            # Add rate limiting
            response = requests.get(
                f"https://api.example.com/v1/crypto/{symbol}",
                timeout=5  # Add timeout
            )
            response.raise_for_status()
            return response.json()['price']
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting crypto price: {e}")
            return None
