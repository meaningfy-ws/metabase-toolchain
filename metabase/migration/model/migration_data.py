from typing import List, Optional, Dict

from pydantic import BaseModel


class MigrationData(BaseModel):
    collections: Optional[List[Dict]] = []
    collections_graph: Optional[Dict] = []
    dashboards: Optional[List[Dict]] = []
    dashboard_cards: Optional[List[Dict]] = []
    databases: Optional[List[Dict]] = []
    tables: Optional[List[Dict]] = []
    metrics: Optional[List[Dict]] = []
    segments: Optional[List[Dict]] = []
    cards: Optional[List[Dict]] = []
    permissions_groups: Optional[List[Dict]] = []
    users: Optional[List[Dict]] = []
    settings: Optional[List[Dict]] = []
