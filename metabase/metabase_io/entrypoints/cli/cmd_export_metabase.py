import os
from pathlib import Path

import click
from metabase.metabase_io.adapters import metabase
from metabase.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner

CMD_NAME = "EXPORT_METABASE"

DEFAULT_OUTPUT_DIR = "export"

"""
USAGE:
# export_metabase --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Metabase export CLI tool
    """

    def __init__(self, api_url, user, password, database, output):
        super().__init__(name=CMD_NAME)
        self.api_url = api_url
        self.user = user
        self.password = password

        self.mb = metabase.MetabaseApi(self.api_url, self.user, self.password, cache_session=False)

        self.databases = []
        if database:
            self.databases = [database]
        else:
            self.databases = list(map(lambda x: x['name'], self.mb.get_databases()))

        self.output = output

    @classmethod
    def init_db_folder(cls, folder: str):
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        if os.path.exists(path):
            for filename in os.listdir(path):
                f = os.path.join(path, filename)
                if os.path.isfile(f):
                    os.remove(f)

    def run_cmd(self):
        error = None
        try:
            for db_name in self.databases:
                output = f'{self.output}/databases/{db_name}'
                self.init_db_folder(output)
                self.log(f'Exporting Database({db_name}) to "{output}" ... ')
                self.log('... database')
                self.mb.export_database_to_json(db_name, output)
                self.log('... fields')
                self.mb.export_fields_to_csv(db_name, output)
                self.log('... cards')
                self.mb.export_cards_to_json(db_name, output)
                self.log('... dashboards')
                self.mb.export_dashboards_to_json(db_name, output)
                self.log('... metrics')
                self.mb.export_metrics_to_json(db_name, output)
                self.log('... snippets')
                self.mb.export_snippet_to_json(db_name, output)
        except Exception as e:
            error = e

        return self.run_cmd_result(error)


def run(api_url, user, password, database=None, output=DEFAULT_OUTPUT_DIR):
    """

    :param output:
    :param database:
    :param api_url:
    :param user:
    :param password:
    :return:
    """

    cmd = CmdRunner(api_url, user, password, database, output)
    cmd.run()


@click.command()
@click.argument('api_url', required=True)
@click.argument('user', required=True)
@click.argument('password', required=True)
@click.option('-db', '--database', required=False)
@click.option('-o', '--output', required=False, default=DEFAULT_OUTPUT_DIR, help="Export folder (use with caution)!")
def main(api_url, user, password, database, output):
    run(api_url, user, password, database, output)


if __name__ == '__main__':
    main()
