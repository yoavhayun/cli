import unittest
from class_cli.cli import CLI
import class_cli._cli_exception as cli_exception

class Parser(unittest.TestCase):
    
    def setUp(self):
        cli = CLI()

        @cli.Program(verbosity=None)
        class Tester:
            @cli.Operation()
            def oper_args(self, *args):
                return args

            @cli.Operation()
            def oper_kwargs(self, **kwargs):
                return kwargs

            @cli.Operation()
            def oper_both(self, *args, **kwargs):
                return args, kwargs

            @cli.Operation()
            def oper_type(self, value:int):
                return value

            @cli.Operation()
            def oper_all(self, value:int, *args, **kwargs):
                return value, args, kwargs

        self.tester = Tester

    def test_parser_type(self):
        """
        Test for parser type convertions
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.run_line("oper_type 5"), tester.oper_type(5))
        self.assertEqual(tester.CLI.run_line("oper_type -5"), tester.oper_type(-5))
        with self.assertRaises(cli_exception.InputException):
            tester.CLI.run_line("oper_type -")

    def test_parser_args(self):
        """
        Test for parsers handeling of *args
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.run_line("oper_args a"), tester.oper_args('a'))
        self.assertEqual(tester.CLI.run_line("  oper_args  a  "), tester.oper_args('a'))
        self.assertEqual(tester.CLI.run_line("oper_args a   b    c"), tester.oper_args('a', 'b', 'c'))

    def test_parser_kwargs(self):
        """
        Test for parsers handeling of **kwargs
        """
        tester = self.tester()
        with self.assertRaises(cli_exception.InputException):
            tester.CLI.run_line("oper_kwargs a")
        self.assertEqual(tester.CLI.run_line("oper_kwargs a=1"), tester.oper_kwargs(a='1'))
        self.assertEqual(tester.CLI.run_line("oper_kwargs a=1   b=2    c=3"), tester.oper_kwargs(a='1', b='2', c='3'))

    def test_parser_both(self):
        """
        Test for parsers handeling of both *args and **kwargs
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.run_line("oper_both a"), tester.oper_both('a'))
        self.assertEqual(tester.CLI.run_line("oper_both a=1"), tester.oper_both(a='1'))
        self.assertEqual(tester.CLI.run_line("oper_both a b c"), tester.oper_both('a', 'b', 'c'))
        self.assertEqual(tester.CLI.run_line("oper_both a=1 b=2 c=3"), tester.oper_both(a='1', b='2', c='3'))
        self.assertEqual(tester.CLI.run_line("oper_both a b c a=1 b=2 c=3"), tester.oper_both('a', 'b', 'c', a='1', b='2', c='3'))
        self.assertEqual(tester.CLI.run_line("oper_both a=1 a b b=2 c c=3"), tester.oper_both('a', 'b', 'c', a='1', b='2', c='3'))

    def test_parser_all(self):
        """
        Test for parsers handeling of both *args and **kwargs and an expected argument with type convertion
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.run_line("oper_all 5 a=1 a b b=2 c c=3"), tester.oper_all(5, 'a', 'b', 'c', a='1', b='2', c='3'))
        self.assertEqual(tester.CLI.run_line("oper_all 5 a=1 a b b=2 c c=3"), tester.oper_all(5, 'a', 'b', 'c', a='1', b='2', c='3'))
        with self.assertRaises(cli_exception.InputException):
            tester.CLI.run_line("oper_all - a=1 a b b=2 c c=3")