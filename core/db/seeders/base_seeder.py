from typing import List, Dict, Any
from sqlalchemy.orm import Session

class BaseSeeder:
    @classmethod
    def run(cls, db: Session, *args, **kwargs):
        raise NotImplementedError("Seeder must implement run method")