from src.migration.adapters.exporter import Exporter
from src.migration.model.migration_data import MigrationData


def export_metabase_to_file(host: str, user: str, password: str):
    exporter: Exporter = Exporter(host, user, password)
    exporter.save_data()


def export_metabase_data(host: str, user: str, password: str) -> MigrationData:
    exporter: Exporter = Exporter(host, user, password)
    return exporter.export_data()
