from metabase.migration.adapters.importer import Importer
import logging


def import_metabase_data_from_file(host: str, user: str, password: str, file: str, logger: logging.Logger):
    importer: Importer = Importer(host, user, password, logger)
    importer.import_data_from_file(file)
