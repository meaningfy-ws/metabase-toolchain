from src.migration.adapters.exporter import Exporter
from src.migration.model.migration_data import MigrationData


def export_metabase_data_to_file(host: str, user: str, password: str, file: str = None):
    exporter: Exporter = Exporter(host, user, password)
    exporter.save_data_to_file(file)


def export_metabase_data(host: str, user: str, password: str) -> MigrationData:
    exporter: Exporter = Exporter(host, user, password)
    return exporter.export_data()
