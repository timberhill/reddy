import os, warnings


class Config:
    instance = None
    def __init__(self, **args):
        if not Config.instance:
            Config.instance = Config.__Config(**args)
    
    def __getattr__(self, property_name):
        return getattr(self.instance, property_name)


    class __Config(object):
        def __init__(self, comment="#"):
            self._default_path = "../modules/config-default.ini"
            self._custom_path  = "../modules/config.ini"
            self.comment = comment

            if os.path.isfile(self._custom_path):
                self.path = self._custom_path
            else:
                warnings.warn(f"Using default config file.", RuntimeWarning)
                self.path = self._default_path
                if not os.path.isfile(self._default_path):
                    self._generate_default_config()
            
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
                    if len(pair) < 2: # no ":" I guess?
                        continue

                    key = pair[0].strip()
                    value = ":".join(pair[1:]).strip()

                    setattr(self, key, value)



        def _generate_default_config(self):
            config_str = [
                "# database file path",
                "db_path: ../data/reddy.db"
            ]

            with open(self._default_path, "w+") as f:
                f.write("\n".join(config_str))
