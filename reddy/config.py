import os
import warnings


class Config:
    instance = None

    def __init__(self, **args):
        if Config.instance is not None:
            return

        Config.instance = Config.__Config(**args)

    def __getattr__(self, property_name):
        return getattr(self.instance, property_name)

    class __Config(object):
        def __init__(self, path=None, comment="#"):
            self._default_path = os.path.join(
                os.path.dirname(__file__),
                "../config.ini"
            )
            self.comment = comment

            if path is not None and os.path.isfile(path):
                self.path = path
            else:
                self.path = self._default_path

            self._parse_config_file()

        def _parse_config_file(self):
            with open(self.path, "r") as configfile:
                for line in configfile:
                    # contains comment
                    splitted = line.split(self.comment)
                    line = splitted[0].strip()

                    # line excluding comment is empty
                    if len(line) == 0:
                        continue

                    pair = line.split(":")
                    if len(pair) < 2:  # no ":" I guess?
                        continue

                    key = pair[0].strip()
                    value = ":".join(pair[1:]).strip()

                    if value.lower() in ["true", "1"]:
                        value = True
                    elif value.lower() in ["false", "0"]:
                        value = False

                    setattr(self, key, value)
