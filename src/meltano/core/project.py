import os
from pathlib import Path
from typing import Union


class Project:
    """
    Represent the current Meltano project from a file-system 
    perspective.
    """

    def __init__(self, root: Union[Path, str]):
        self.root = Path(root)

    @classmethod
    def find(self, from_dir: Union[Path, str] = ".", chdir=True):
        """
        Recursively search for a `meltano.yml` file. Once found,
        return a `Project` correct dir.
        """
        cwd = os.getcwd()

        while not Project(".").meltanofile.exists():
            if os.getcwd() == "/":
                raise Exception("Cannot find a meltano.yml file in your project")

            os.chdir("..")

        if not chdir:
            os.chdir(cwd)

        return Project(os.getcwd())

    @property
    def meltanofile(self):
        return self.root.joinpath("meltano.yml")

    def meltano_dir(self, *joinpaths):
        return self.root.joinpath(".meltano", *joinpaths)

    def venvs_dir(self, *joinpaths):
        return self.meltano_dir("venvs", *joinpaths)

    def run_dir(self, *joinpaths):
        return self.meltano_dir("run", *joinpaths)
