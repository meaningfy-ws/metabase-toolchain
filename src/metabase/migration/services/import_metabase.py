from metabase.migration.adapters.importer import Importer
import logging


def import_metabase_data_from_file(host: str, user: str, password: str, file: str, database_name: str,
                                   logger: logging.Logger):
    importer: Importer = Importer(host, user, password, logger)
    importer.sync_database_by_name(database_name=database_name)
    importer.import_data_from_file(file)
