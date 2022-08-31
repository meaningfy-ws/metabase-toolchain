import datetime
import logging
import sys

DEFAULT_LOGGER_LOG_FORMAT = "[%(asctime)s] - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOGGER_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOGGER_LEVEL = logging.DEBUG


class CmdRunner:
    def __init__(self, name=__name__, logger: logging.Logger = None):
        self.name = name
        self.begin_time = None
        self.end_time = None

        if logger is None:
            logger = logging.getLogger(name)

        self.logger = logger

        self._init_logger()

    def _init_logger(self):
        self.logger.setLevel(DEFAULT_LOGGER_LEVEL)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(DEFAULT_LOGGER_LEVEL)
        fmt = DEFAULT_LOGGER_LOG_FORMAT
        date_fmt = DEFAULT_LOGGER_LOG_DATE_FORMAT
        formatter = logging.Formatter(fmt, date_fmt)
        handler.setFormatter(formatter)

        self.logger.handlers.clear()
        self.logger.addHandler(handler)
        self.logger.propagate = False

    def get_logger(self) -> logging.Logger:
        return self.logger

    @staticmethod
    def _now() -> str:
        return str(datetime.datetime.now())

    def log(self, message: str, level: int = logging.INFO):
        self.logger.log(level, message)

    def log_failed_error(self, error: Exception):
        self.log("FAILED" + ' :: ' + type(error).__name__ + ' :: ' + str(error))

    def log_failed_msg(self, msg: str = None):
        self.log('FAILED :: ' + msg if msg is not None else "")

    def log_success_msg(self, msg: str = None):
        self.log('SUCCESS' + (' :: ' + msg if msg is not None else ""))

    def on_begin(self):
        self.begin_time = datetime.datetime.now()
        self.log("CMD :: BEGIN :: {now}".format(now=self._now()))

    def run(self):
        self.on_begin()
        self.run_cmd()
        self.on_end()

    def run_cmd(self):
        pass

    def run_cmd_result(self, error: Exception = None, msg: str = None, errmsg: str = None) -> bool:
        if error:
            self.log_failed_error(error)
            if errmsg is not None:
                self.log_failed_msg(errmsg)
            return False
        else:
            self.log_success_msg(msg)
            return True

    def on_end(self):
        self.end_time = datetime.datetime.now()
        self.log("CMD :: END :: {now} :: [{time}]".format(
            now=str(self.end_time),
            time=self.end_time - self.begin_time
        ))
