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

    def test_handling_quotes(self):
        """
        Test that inputs that contain quotes work as expected
        """
        cli = CLI()
        @cli.Program()
        class Tester:
            @cli.Operation()
            def oper(self, value): return value

            @cli.Delegate()
            def delegate(self): return self

        tester = Tester()
        self.assertEqual(tester.CLI.run_line("oper 'oneword'"), "oneword")
        self.assertEqual(tester.CLI.run_line('oper "oneword"'), "oneword")
        self.assertEqual(tester.CLI.run_line("oper 'two words'"), "two words")
        self.assertEqual(tester.CLI.run_line('oper "two words"'), "two words")
        self.assertEqual(tester.CLI.run_line("oper 'two words'"), "two words")
        self.assertEqual(tester.CLI.run_line('oper "prefix \'inner words\' suffix"'), "prefix 'inner words' suffix")
        self.assertEqual(tester.CLI.run_line("oper 'prefix \"inner words\" suffix'"), 'prefix "inner words" suffix')

        self.assertEqual(tester.CLI.run_line("delegate oper 'oneword'"), "oneword")
        self.assertEqual(tester.CLI.run_line('delegate oper "oneword"'), "oneword")
        self.assertEqual(tester.CLI.run_line("delegate oper 'two words'"), "two words")
        self.assertEqual(tester.CLI.run_line('delegate oper "two words"'), "two words")
        self.assertEqual(tester.CLI.run_line('delegate oper "prefix \'inner words\' suffix"'), "prefix 'inner words' suffix")
        self.assertEqual(tester.CLI.run_line("delegate oper 'prefix \"inner words\" suffix'"), 'prefix "inner words" suffix')

        self.assertEqual(tester.CLI.run_line("delegate oper '\"nospace\"'"), '"nospace"')

    def test_cli_access(self):
        """
        Test that methods can access the CLI keyword and calls compiled methods.
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

            @cli.Delegate()
            def delegate(self): return self

        tester = Tester()
        self.assertEqual(tester.CLI.execute("get_set"), tester.CLI.set)
        tester.set('1')
        self.assertEqual(tester.CLI.set, '1')
        self.assertEqual(tester.CLI.execute("get_set"), tester.CLI.set)
        self.assertEqual(tester.CLI.execute("get_set", '2'), tester.CLI.set)
        self.assertEqual(tester.CLI.execute("delegate", "get_set"), tester.CLI.set)
        self.assertEqual(tester.CLI.set, tester.CLI.execute("get_set", '2'))
        self.assertEqual(tester.CLI.set, '2')
        self.assertEqual(tester.delegate().CLI.set, '2')