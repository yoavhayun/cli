import unittest, traceback
from class_cli.cli import CLI
import class_cli._cli_exception as cli_exception

from tests.Test_General import General
from tests.Test_Compilation import Compilation
from tests.Test_Parser import Parser
from tests.Test_Methods import Methods
from tests.Test_Settings import Settings


if __name__ == "__main__":
    unittest.main()