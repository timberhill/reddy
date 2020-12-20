import glob
import os


class SubredditListManager:
    """
    """

    def __init__(self):
        self._sourcedir = os.path.join(
            os.path.dirname(__file__), "subreddit_lists")
        self._extension = ".list"

    def _read_list(self, list_path):
        """
        """
        with open(list_path, "r") as list_file:
            lines = (line.rstrip() for line in list_file)
            return [line for line in lines if line]

    def _write_list(self, list_path, list_contents):
        """
        """
        raise NotImplementedError

    def list_lists(self):
        """
        """
        files = glob.glob(os.path.join(self._sourcedir, f"*{self._extension}"))
        return [
            os.path.basename(path).replace(self._extension, "")
            for path in files
        ]

    def get_list(self, list_name):
        """
        """
        return self._read_list(
            os.path.join(self._sourcedir, f"{list_name}{self._extension}")
        )
