import click

from metabase.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner
from metabase.metabase_io.adapters import metabase
from metabase.metabase_io.entrypoints.cli.cmd_export_metabase import DEFAULT_OUTPUT_DIR
import os.path
import json
import dotenv

dotenv.load_dotenv(verbose=True, override=True)

CMD_NAME = "IMPORT_METABASE"

MONGO_DB_USER = os.environ.get('MONGO_DB_USER')
MONGO_DB_PASS = os.environ.get('MONGO_DB_PASS')
MONGO_DB_HOST = os.environ.get('MONGO_DB_HOST')
ENV_MONGO_DB_PORT = os.environ.get('MONGO_DB_PORT')
MONGO_DB_PORT = int(ENV_MONGO_DB_PORT) if ENV_MONGO_DB_PORT else None

"""
USAGE:
# import_metabase --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Metabase import CLI tool
    """

    def __init__(self, api_url, user, password, database, output, debug):
        super().__init__(name=CMD_NAME)
        self.api_url = api_url
        self.user = user
        self.password = password
        self.mb = metabase.MetabaseApi(self.api_url, self.user, self.password, debug=debug, cache_session=False)

        self.output = output + "/databases"

        self.databases = []
        if database:
            self.databases = [database]
        else:
            self.databases = [d for d in os.listdir(self.output) if os.path.isdir(os.path.join(self.output, d))]

    def init_db(self, db_name, output):
        f = open(f'{output}/database_{db_name}.json', "r")
        data = json.loads(f.read())
        details = data['details']

        if MONGO_DB_USER:
            details['user'] = MONGO_DB_USER
        if MONGO_DB_PASS:
            details['pass'] = MONGO_DB_PASS
        if MONGO_DB_HOST:
            details['host'] = MONGO_DB_HOST
        if MONGO_DB_PORT:
            details['port'] = MONGO_DB_PORT

        self.mb.create_database(db_name, engine=data['engine'], details=details)

        self.mb.create_user(self.user, db_name)
        self.mb.user_password(self.user, self.password)
        self.mb.membership_add(self.user, db_name)
        # self.mb.permission_set_database(db_name, db_name, True, True)

    def run_cmd(self):
        error = None
        try:
            for db_name in self.databases:
                output = f'{self.output}/{db_name}'
                self.log(f'Importing Database({db_name}) from "{output}" ... ')

                # self.log('... creating database')
                # self.init_db(db_name, output)
                #
                # self.log('... fields')
                # self.mb.import_fields_from_csv(db_name, output)

                self.log('... collection and rights')
                self.mb.create_collection(db_name)
                self.mb.permission_set_collection(db_name, db_name, 'write')

                self.log('... metrics')
                self.mb.import_metrics_from_json(db_name, output)
                self.log('... snippets')
                self.mb.import_snippets_from_json(db_name, output, db_name)
                self.log('... cards')
                self.mb.import_cards_from_json(db_name, output)
                self.log('... dashboards')
                self.mb.import_dashboards_from_json(db_name, output)
        except Exception as e:
            error = e

        return self.run_cmd_result(error)


def run(api_url, user, password, database=None, output=DEFAULT_OUTPUT_DIR, debug=False):
    """

    :param debug:
    :param output:
    :param database:
    :param api_url:
    :param user:
    :param password:
    :return:
    """

    cmd = CmdRunner(api_url, user, password, database, output, debug)
    cmd.run()


@click.command()
@click.argument('api_url', required=True)
@click.argument('user', required=True)
@click.argument('password', required=True)
@click.option('-db', '--database', required=False)
@click.option('-o', '--output', required=False, default=DEFAULT_OUTPUT_DIR, help="Import folder (use with caution)!")
@click.option('--debug', required=False, default=False)
def main(api_url, user, password, database, output, debug):
    run(api_url, user, password, database, output, debug)


if __name__ == '__main__':
    main()
