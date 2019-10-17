import unittest
from class_cli.cli import CLI

class General(unittest.TestCase):
    def test_help_behavior(self):
        """
        Test that calling help does not raise an Exception from argparse
        """
        cli = CLI()
        @cli.Program()
        class Tester:
            pass

        Tester().CLI.run("--help")