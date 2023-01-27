import click
from pymongo import MongoClient

from metabase.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner
from metabase.migration.resources import DB_SNAPSHOT_FILE_PATH
from metabase.migration.services.database_management import create_mongodb_snapshot, inject_mongodb_snapshot, \
    remove_mongodb_snapshot

CMD_NAME = "SNAPSHOT_DB"

"""
USAGE:
# manage_snapshot_db --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Snapshot manager CLI tool
    """

    def __init__(self, db_auth_url: str, db_name: str, update: bool, inject: bool, delete: bool):
        super().__init__(name=CMD_NAME)
        self.db_auth_url = db_auth_url
        self.db_name = db_name
        self.update = update
        self.inject = inject
        self.delete = delete

    def run_cmd(self):
        error = None
        try:
            mongodb_client = MongoClient(self.db_auth_url)
            if self.update:
                create_mongodb_snapshot(database_name=self.db_name,
                                        result_snapshot_path=DB_SNAPSHOT_FILE_PATH,
                                        mongodb_client=mongodb_client)

            if self.inject:
                inject_mongodb_snapshot(database_snapshot_path=DB_SNAPSHOT_FILE_PATH, mongodb_client=mongodb_client,
                                        database_name=self.db_name)
            if self.delete:
                remove_mongodb_snapshot(database_name=self.db_name, mongodb_client=mongodb_client)

        except Exception as e:
            error = e

        return self.run_cmd_result(error)


def run(db_auth_url: str, db_name: str, update: bool, inject: bool, delete: bool):
    """

    :param db_auth_url:
    :param db_name:
    :param update:
    :param inject:
    :param delete:
    :return:
    """

    cmd = CmdRunner(db_auth_url, db_name, update, inject, delete)
    cmd.run()


@click.command()
@click.option('--db_auth_url', required=True, type=str, help="MongoDB Authentication URL.")
@click.option('--db_name', show_default=True, default="tmp_test_database", type=str, help="MongoDB database name.")
@click.option("-u", "update", is_flag=True, show_default=True, default=False, help="Update snapshot cache.")
@click.option("-i", "inject", is_flag=True, show_default=True, default=False,
              help="Inject snapshot cache into database")
@click.option("-d", "delete", is_flag=True, show_default=True, default=False,
              help="Remove injected snapshot from database")
def main(db_auth_url: str, db_name: str, update: bool, inject: bool, delete: bool):
    run(db_auth_url, db_name, update, inject, delete)


if __name__ == '__main__':
    main()
