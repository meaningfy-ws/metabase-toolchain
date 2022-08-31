from src.migration.adapters.importer import Importer


def import_metabase_data_from_file(host: str, user: str, password: str, file: str):
    importer: Importer = Importer(host, user, password)
    importer.import_data_from_file(file)
