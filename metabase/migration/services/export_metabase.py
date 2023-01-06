from metabase.migration.adapters.exporter import Exporter
from metabase.migration.model.migration_data import MigrationData
import logging


def export_metabase_data_to_file(host: str, user: str, password: str, filename: str = None,
                                 logger: logging.Logger = None):
    exporter: Exporter = Exporter(host, user, password, logger)
    exporter.save_data_to_file(filename)


def export_metabase_data(host: str, user: str, password: str) -> MigrationData:
    exporter: Exporter = Exporter(host, user, password)
    return exporter.export_data()
