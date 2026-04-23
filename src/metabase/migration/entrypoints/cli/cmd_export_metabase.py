import click

from metabase.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner
from metabase.migration.services.export_metabase import export_metabase_data_to_file

CMD_NAME = "EXPORT_METABASE"

"""
USAGE:
# export_metabase --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Metabase export CLI tool
    """

    def __init__(self, host, user, password, file):
        super().__init__(name=CMD_NAME)
        self.host = host
        self.user = user
        self.password = password
        self.file = file

    def run_cmd(self):
        error = None
        try:
            export_metabase_data_to_file(self.host, self.user, self.password, self.file, self.get_logger())
        except Exception as e:
            error = e

        return self.run_cmd_result(error)


def run(host, user, password, file):
    """

    :param host:
    :param user:
    :param password:
    :param file:
    :return:
    """

    cmd = CmdRunner(host, user, password, file)
    cmd.run()


@click.command()
@click.argument('host', required=True)
@click.argument('user', required=True)
@click.argument('password', required=True)
@click.argument('file', required=False)
def main(host, user, password, file):
    run(host, user, password, file)


if __name__ == '__main__':
    main()
