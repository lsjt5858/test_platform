"""
Test data generation utilities.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from faker import Faker

from ..base_util.logger import get_logger

logger = get_logger(__name__)


class DataGenerator:
    """Utility for generating test data."""
    
    def __init__(self, seed: Optional[int] = None):
        self.fake = Faker()
        if seed:
            Faker.seed(seed)
            random.seed(seed)
    
    def random_string(self, length: int = 10) -> str:
        """Generate random string."""
        return ''.join(random.choices(string.ascii_letters, k=length))
    
    def random_email(self) -> str:
        """Generate random email."""
        return self.fake.email()
    
    def random_user_data(self) -> Dict[str, Any]:
        """Generate random user data."""
        return {
            'name': self.fake.name(),
            'email': self.fake.email(),
            'phone': self.fake.phone_number(),
            'address': self.fake.address(),
            'birth_date': self.fake.date_of_birth().isoformat()
        }
    
    def random_api_payload(self, schema: Dict[str, str]) -> Dict[str, Any]:
        """Generate API payload based on schema."""
        payload = {}
        
        for field, field_type in schema.items():
            if field_type == 'string':
                payload[field] = self.random_string()
            elif field_type == 'email':
                payload[field] = self.random_email()
            elif field_type == 'int':
                payload[field] = random.randint(1, 1000)
            elif field_type == 'bool':
                payload[field] = random.choice([True, False])
        
        return payload