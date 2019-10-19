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

    def test_cli_access(self):
        """
        Test that calling help does not raise an Exception from argparse
        """
        cli = CLI()
        @cli.Program()
        class Tester:
            @cli.Setting()
            def set(self, value): return value

            @cli.Operation()
            def get_set(self, value=None): 
                if value is not None:
                    self.set(value)
                return self.CLI.set

        tester = Tester()
        self.assertEqual(tester.CLI.execute("get_set"), tester.CLI.set)
        tester.set('1')
        self.assertEqual(tester.CLI.set, '1')
        self.assertEqual(tester.CLI.execute("get_set"), tester.CLI.set)
        self.assertEqual(tester.CLI.execute("get_set", '2'), tester.CLI.set)
        self.assertEqual(tester.CLI.set, tester.CLI.execute("get_set", '2'))
        self.assertEqual(tester.CLI.set, '2')