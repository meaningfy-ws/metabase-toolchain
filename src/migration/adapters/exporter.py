from src.migration.model.migration_data import MigrationData
from src.migration.adapters.api import API
import json
from pathlib import Path


class Exporter:
    EXPORT_FILE = "./metabase/data.json"
    api: API

    def __init__(self, host: str, user: str, password: str):
        self.api = API(
            host=host,
            user=user,
            password=password,
        )

    def export_data(self) -> MigrationData:
        data = MigrationData()

        data.collections = self.api.get_collections()
        data.dashboards = self.api.get_dashboards()
        databases = self.api.get_databases()
        if databases and databases['data']:
            data.databases = self.api.get_databases()['data']
        data.metrics = self.api.get_metrics()
        data.segments = self.api.get_segments()
        data.cards = self.api.get_cards()

        for dashboard in data.dashboards:
            dashboard_id = dashboard["id"]
            data.dashboard_cards.append(self.api.get_dashboard_cards(dashboard_id))

        return data

    def save_data(self, file: str = None, data: MigrationData = None):
        if not file:
            file = self.EXPORT_FILE
        filepath = Path(file)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        if not data:
            data = self.export_data()

        with open(filepath, "w+") as f:
            json.dump(data.dict(), f)
            f.close()
