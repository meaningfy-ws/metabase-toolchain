import click
from pymongo import MongoClient

from metabase.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner
from metabase.migration.resources import DB_SNAPSHOT_FILE_PATH
from metabase.migration.services.database_management import remove_mongodb_snapshot, \
    inject_mongodb_snapshot
from metabase.migration.services.import_metabase import import_metabase_data_from_file
import time
from loadbar import LoadBar


def wait_n_seconds(message: str, number_of_seconds: int):
    print(message)
    bar = LoadBar(max=number_of_seconds)
    bar.start()
    for i in range(number_of_seconds):
        time.sleep(1)
        bar.update(step=i)
    bar.end()


CMD_NAME = "IMPORT_METABASE"

"""
USAGE:
# import_metabase --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Metabase import CLI tool
    """

    def __init__(self, host, user, password, file, db_auth_url, db_name):
        super().__init__(name=CMD_NAME)
        self.host = host
        self.user = user
        self.password = password
        self.file = file
        self.db_auth_url = db_auth_url
        self.db_name = db_name

    def run_cmd(self):
        error = None
        try:
            mongodb_client = MongoClient(self.db_auth_url)
            inject_mongodb_snapshot(database_name=self.db_name,
                                    database_snapshot_path=DB_SNAPSHOT_FILE_PATH,
                                    mongodb_client=mongodb_client)
            wait_n_seconds(message="Prepare environment:", number_of_seconds=1)
            import_metabase_data_from_file(host=self.host, user=self.user, password=self.password,
                                           database_name=self.db_name,
                                           file=self.file,
                                           logger=self.get_logger())
            wait_n_seconds(message="Import metabase data from file:",number_of_seconds=2)
            remove_mongodb_snapshot(database_name=self.db_name, mongodb_client=mongodb_client)
            wait_n_seconds(message="Clean environment:", number_of_seconds=1)
        except Exception as e:
            error = e

        return self.run_cmd_result(error)


def run(host, user, password, file, db_auth_url, db_name):
    """

    :param host:
    :param user:
    :param password:
    :param file:
    :param db_auth_url:
    :param db_name:
    :return:
    """

    cmd = CmdRunner(host, user, password, file, db_auth_url, db_name)
    cmd.run()


@click.command()
# @click.argument('host', required=True)
# @click.argument('user', required=True)
# @click.argument('password', required=True)
@click.argument('file', required=True)
# @click.argument('db_auth_url', required=True)
# @click.argument('db_name', required=True)
def main(host, user, password, file, db_auth_url, db_name):
    run(host, user, password, file, db_auth_url, db_name)


if __name__ == '__main__':
    main()
