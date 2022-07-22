from src.migration.adapters.importer import Importer


def import_metabase_data(host: str, user: str, password: str, file: str):
    importer: Importer = Importer(host, user, password)
    importer.import_data(file)
