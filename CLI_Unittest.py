import unittest, traceback
from class_cli.cli import CLI
import class_cli._cli_exception as cli_exception

from tests.Test_General import General
from tests.Test_Compilation import Compilation
from tests.Test_Parser import Parser
from tests.Test_Completer import Completer
from tests.Test_StatusBar import StatusBar
from tests.Test_Methods import Methods
from tests.Test_Settings import Settings
from tests.Test_Delegate import Delegate
from tests.Test_Mock import Mock


if __name__ == "__main__":
    unittest.main()