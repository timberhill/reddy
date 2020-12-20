"""
"""
import os
import uuid
from datetime import datetime
from ..config import Config


class Logger:
    instance = None

    def __init__(self, **args):
        if Logger.instance is not None:
            return

        Logger.instance = Logger.__Logger(**args)

    def __getattr__(self, property_name):
        return getattr(self.instance, property_name)

    class __Logger:
        def __init__(self, identifier=None, logfile=None, stdout=None, debug=None):
            config = Config()
            self._identifier = identifier \
                if identifier is not None else str(uuid.uuid4())[0:5]
            self._logfile = logfile if logfile else config.logfile
            self._stdout = stdout if stdout else config.stdout
            self._debug = debug if debug else config.debug

            self._level_info = "INFO"
            self._level_warn = "WARN"
            self._level_error = "ERROR"
            self._level_debug = "DEBUG"
            self._levels = [
                self._level_info,
                self._level_warn,
                self._level_error,
                self._level_debug
            ]

            if self._logfile is not None:
                # make sure the directory structure exists
                os.makedirs(os.path.dirname(self._logfile), exist_ok=True)

            # log out the config data for this run
            self.info(f"Retrieved config values.")
            for attr in dir(Config.instance):
                if attr.startswith("_"):
                    continue
                elif attr in ["client", "secret"]:
                    self.info(f"Config.{attr} = <REDACTED>")
                else:
                    self.info(
                        f"Config.{attr} = { Config.instance.__dict__[attr]}")

        def log(self, message, level):
            """
            """
            if level not in self._levels:
                self.log(message="", level=self._level_warn)

            if level == self._level_debug and not self._debug:
                return

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[0:23]
            entry = f"[{timestamp}] [{self._identifier}:{level}] {message}"

            if self._stdout:
                print(entry)

            if self._logfile is not None:
                with open(self._logfile, "a+") as log:
                    log.write(f"{entry}\n")

        def info(self, message):
            self.log(message, self._level_info)

        def warn(self, message):
            self.log(message, self._level_warn)

        def error(self, message):
            self.log(message, self._level_error)

        def debug(self, message):
            self.log(message, self._level_debug)
