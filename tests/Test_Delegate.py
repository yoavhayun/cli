import unittest
from class_cli import CLI
from class_cli import cli_exceptions

class Delegate(unittest.TestCase):
    def setUp(self):
        cli = CLI()

        @cli.Program(verbosity=None)
        class Tester:

            @cli.Delegate()
            def del_self(self): return self


            @cli.Delegate()
            def del_new(self): return Tester()

            @cli.Delegate(reuse=False)
            def del_discard(self): return Tester()

            @cli.Validation()
            def del_locked(self): 
                if self.CLI.locked: 
                    raise Exception("Cannot delegate while locked") 

            @cli.Delegate()
            def del_locked(self): return Tester()

            @cli.Setting(initial_value=False)
            def locked(self, state:[True, False]): return state

            @cli.Operation()
            def unlock(self):
                self.locked(False)

        self.tester = Tester

    def test_validation(self):
        tester = self.tester()
        self.assertEqual(tester.del_locked().CLI.locked, False)
        tester.del_locked().locked(True)
        tester.locked(True)
        with self.assertRaises(Exception):
            tester.del_locked()
        tester.locked(False)
        self.assertEqual(tester.del_locked().CLI.locked, True)
        with self.assertRaises(Exception):
            tester.del_locked().del_locked()
    
    def test_del_self(self):
        tester = self.tester()
        self.assertEqual(tester.CLI.locked, False)
        self.assertEqual(tester.del_self().CLI.locked, False)

        tester.locked(True)
        self.assertEqual(tester.CLI.locked, True)
        self.assertEqual(tester.del_self().CLI.locked, True)

    def test_del_new(self):
        tester = self.tester()
        self.assertEqual(tester.del_new().CLI.locked, False)

        tester.locked(True)
        self.assertEqual(tester.CLI.locked, True)
        self.assertEqual(tester.del_new().CLI.locked, False)

        tester.CLI.run("del_new", ".setting", "locked", "True")
        self.assertEqual(tester.CLI.locked, True)
        self.assertEqual(tester.del_new().CLI.locked, True)

        tester.unlock()
        self.assertEqual(tester.CLI.locked, False)
        self.assertEqual(tester.del_new().CLI.locked, True)

        tester.CLI.run("del_new", "unlock")
        self.assertEqual(tester.CLI.locked, False)
        self.assertEqual(tester.del_new().CLI.locked, False)

    def test_del_discard(self):
        tester = self.tester()
        self.assertEqual(tester.del_discard().CLI.locked, False)

        tester.locked(True)
        self.assertEqual(tester.CLI.locked, True)
        self.assertEqual(tester.del_discard().CLI.locked, False)

        tester.del_discard().locked(True)
        self.assertEqual(tester.CLI.locked, True)
        self.assertEqual(tester.del_discard().CLI.locked, False)
