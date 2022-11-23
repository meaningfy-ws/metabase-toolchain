from typing import List, Optional, Dict

from pydantic import BaseModel


class MigrationData(BaseModel):
    collections: Optional[List] = []
    dashboards: Optional[List] = []
    dashboard_cards: Optional[List] = []
    databases: Optional[List] = []
    metrics: Optional[List] = []
    segments: Optional[List] = []
    cards: Optional[List] = []
    permissions_groups: Optional[List] = []
    permissions_memberships: Optional[Dict] = {}
    users: Optional[List] = []
