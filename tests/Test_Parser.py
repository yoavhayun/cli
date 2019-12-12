import unittest
from class_cli import CLI
from class_cli import cli_exceptions

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

            @cli.Delegate()
            def delegate(self):
                return self

        self.tester = Tester

    def __prefix(self, prefix): return prefix + ' ' * min(len(prefix), 1)

    def test_parser_type(self, command_prefix=''): 
        """
        Test for parser type convertions
        """
        tester = self.tester()
        with self.assertRaises(cli_exceptions.InputException): tester.CLI.run(self.__prefix(command_prefix), "oper_type" ,5)
        self.assertEqual(tester.CLI(self.__prefix(command_prefix) + "oper_type 5"), tester.oper_type(5))
        self.assertEqual(tester.CLI(self.__prefix(command_prefix) + "oper_type -5"), tester.oper_type(-5))
        with self.assertRaises(cli_exceptions.InputException):
            tester.CLI(self.__prefix(command_prefix) + "oper_type -")

    def test_parser_args(self, command_prefix=''):
        """
        Test for parsers handeling of *args
        """
        tester = self.tester()
        self.assertEqual(tester.CLI(self.__prefix(command_prefix) + "oper_args a"), tester.oper_args('a'))
        self.assertEqual(tester.CLI(self.__prefix(command_prefix) + "  oper_args  a  "), tester.oper_args('a'))
        self.assertEqual(tester.CLI(self.__prefix(command_prefix) + "oper_args a   b    c"), tester.oper_args('a', 'b', 'c'))

    def test_parser_kwargs(self, command_prefix=''):
        """
        Test for parsers handeling of **kwargs
        """
        tester = self.tester()
        with self.assertRaises(cli_exceptions.InputException):
            tester.CLI(self.__prefix(command_prefix) + "oper_kwargs a")
        self.assertEqual(tester.CLI(self.__prefix(command_prefix) + "oper_kwargs a=1"), tester.oper_kwargs(a='1'))
        self.assertEqual(tester.CLI(self.__prefix(command_prefix) + "oper_kwargs a=1   b=2    c=3"), tester.oper_kwargs(a='1', b='2', c='3'))

    def test_parser_both(self, command_prefix=''):
        """
        Test for parsers handeling of both *args and **kwargs
        """
        tester = self.tester()
        self.assertEqual(tester.CLI(self.__prefix(command_prefix) + "oper_both a"), tester.oper_both('a'))
        self.assertEqual(tester.CLI(self.__prefix(command_prefix) + "oper_both a=1"), tester.oper_both(a='1'))
        self.assertEqual(tester.CLI(self.__prefix(command_prefix) + "oper_both a b c"), tester.oper_both('a', 'b', 'c'))
        self.assertEqual(tester.CLI(self.__prefix(command_prefix) + "oper_both a=1 b=2 c=3"), tester.oper_both(a='1', b='2', c='3'))
        self.assertEqual(tester.CLI(self.__prefix(command_prefix) + "oper_both a b c a=1 b=2 c=3"), tester.oper_both('a', 'b', 'c', a='1', b='2', c='3'))
        self.assertEqual(tester.CLI(self.__prefix(command_prefix) + "oper_both a=1 a b b=2 c c=3"), tester.oper_both('a', 'b', 'c', a='1', b='2', c='3'))

    def test_parser_all(self, command_prefix=''):
        """
        Test for parsers handeling of both *args and **kwargs and an expected argument with type convertion
        """
        tester = self.tester()
        self.assertEqual(tester.CLI(self.__prefix(command_prefix) + "oper_all 5 a=1 a b b=2 c c=3"), tester.oper_all(5, 'a', 'b', 'c', a='1', b='2', c='3'))
        self.assertEqual(tester.CLI(self.__prefix(command_prefix) + "oper_all 5 a=1 a b b=2 c c=3"), tester.oper_all(5, 'a', 'b', 'c', a='1', b='2', c='3'))
        with self.assertRaises(cli_exceptions.InputException):
            tester.CLI(self.__prefix(command_prefix) + "oper_all a=1 a b b=2 c c=3 5s")
        with self.assertRaises(cli_exceptions.InputException):
            tester.CLI(self.__prefix(command_prefix) + "oper_all - a=1 a b b=2 c c=3")

    def test_parser_delegate(self):
        self.test_parser_type("delegate")
        self.test_parser_args("delegate")
        self.test_parser_kwargs("delegate")
        self.test_parser_both("delegate")
        self.test_parser_all("delegate")
