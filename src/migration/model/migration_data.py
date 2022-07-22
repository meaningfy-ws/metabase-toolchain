from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class MigrationData(BaseModel):
    collections: Optional[List] = []
    dashboards: Optional[List] = []
    dashboard_cards: Optional[List] = []
    databases: Optional[List] = []
    metrics: Optional[List] = []
    segments: Optional[List] = []
    cards: Optional[List] = []
