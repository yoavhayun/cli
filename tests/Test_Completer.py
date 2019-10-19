import unittest
from class_cli.cli import CLI

class Completer(unittest.TestCase):

    def setUp(self):
        cli = CLI()

        @cli.Program()
        class Tester:

            @cli.Operation()
            def oper(self, a, b:["aa", "ab", "bb"]): pass

            @cli.Operation()
            def oper_no_args(self): pass

            @cli.Setting()
            def set11(self, a:{11:"", 12:"", 22: ""}, b, *args): pass

            @cli.Setting()
            def set22(self, a:{11:"", 12:"", 22: ""}, b, *args): pass

        self.tester = Tester
    
    def test_complete_builtin(self):
        """
        Test completions for builtin commands
        """
        tester = self.tester()
        self.assertEqual(tester.CLI._complete("."), [".setting", ".read"])

        self.assertEqual(tester.CLI._complete("-"), ["--help"])
        self.assertEqual(tester.CLI._complete("oper -"), ["--help"])
        self.assertEqual(tester.CLI._complete("oper _ -"), ["--help"])
        self.assertEqual(tester.CLI._complete("oper _ aa -"), ["--help"])
        self.assertEqual(tester.CLI._complete("oper _ aa -"), ["--help"])
        self.assertEqual(tester.CLI._complete(".set -"), ["--help"])
        self.assertEqual(tester.CLI._complete(".set set11 -"), ["--help"])
        self.assertEqual(tester.CLI._complete(".set set11 11 -"), ["--help"])
        self.assertEqual(tester.CLI._complete("non existing -"), ["--help"])

        cli = CLI()
        @cli.Program()
        class NoSettings: pass
        self.assertEqual(NoSettings().CLI._complete("."), [".read"])


    def test_complete_method(self):
        """
        Test completions for methods
        """
        tester = self.tester()
        self.assertEqual(tester.CLI._complete("op"), ["oper", "oper_no_args"])
        self.assertEqual(tester.CLI._complete("oper_"), ["oper_no_args"])
    
    def test_complete_setting(self):
        """
        Test completions for settings
        """
        tester = self.tester()
        self.assertEqual(tester.CLI._complete(".s"), [".setting"])
        self.assertEqual(tester.CLI._complete(".set"), [])
        self.assertEqual(tester.CLI._complete(".sett"), [".setting"])
        self.assertEqual(tester.CLI._complete(".set "), ["set11", "set22"])
        self.assertEqual(tester.CLI._complete(".set set"), ["set11", "set22"])
        self.assertEqual(tester.CLI._complete(".set set1"), ["set11"])
        self.assertEqual(tester.CLI._complete(".set set2"), ["set22"])
        self.assertEqual(tester.CLI._complete(".setting "), ["set11", "set22"])
        self.assertEqual(tester.CLI._complete(".setting set"), ["set11", "set22"])
        self.assertEqual(tester.CLI._complete(".setting set1"), ["set11"])
        self.assertEqual(tester.CLI._complete(".setting set2"), ["set22"])
        

    def test_complete_iterable(self):
        """
        Test completions for iterable annotation
        """
        tester = self.tester()
        self.assertEqual(tester.CLI._complete("oper "), [])
        self.assertEqual(tester.CLI._complete("oper _ "), ["aa", "ab", "bb"])
        self.assertEqual(tester.CLI._complete("oper _ a"), ["aa", "ab"])
        self.assertEqual(tester.CLI._complete("oper _ aa"), ["aa"])
        self.assertEqual(tester.CLI._complete("oper _ aa "), [])

    def test_complete_dict(self):
        """
        Test completions for dict annotation
        """
        tester = self.tester()
        self.assertEqual(tester.CLI._complete(".setting set11 "), ["11", "12", "22"])
        self.assertEqual(tester.CLI._complete(".setting set11 1"), ["11", "12"])
        self.assertEqual(tester.CLI._complete(".setting set11 2"), ["22"])
        self.assertEqual(tester.CLI._complete(".setting set11 1 "), [])
        self.assertEqual(tester.CLI._complete(".setting set11 11 "), [])
        self.assertEqual(tester.CLI._complete(".setting set11 11 _ "), [])