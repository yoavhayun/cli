import unittest
from class_cli.cli import CLI
from prompt_toolkit.validation import ValidationError

class StatusBar(unittest.TestCase):

    def setUp(self):
        cli = CLI()

        @cli.Program(verbosity=None)
        class Tester:

            @cli.Operation()
            def oper1(self, val1:int, val2=None): pass

            @cli.Setting()
            def oper2(self, args:range(2), kwargs:{'a':"_a", 'b':"_b"}): pass

            @cli.Validation()
            def delegate(self): 
                if self.CLI.locked: 
                    raise Exception("Locked")

            @cli.Delegate()
            def delegate(self): return self

            @cli.Setting(initial_value=False)
            def locked(self, value:[True, False]):
                return value

        
        self.tester = Tester

    def __format_validation(self, validation):
        return ''.join([part[1] for part in validation])

    def test_type_annotation(self, prefix=''):
        tester = self.tester()
        self.assertEqual(self.__format_validation(tester.CLI._validate(prefix + "oper1")), "val1 val2[=None] ")
        self.assertEqual(self.__format_validation(tester.CLI._validate(prefix + "oper1 0")), "val1 val2[=None]  :  {<class 'int'>}")
        self.assertEqual(self.__format_validation(tester.CLI._validate(prefix + "oper1 0 ")), "val1 val2[=None]  :  {<class 'str'>}")
        self.assertEqual(self.__format_validation(tester.CLI._validate(prefix + "oper1 0 0 ")), "")

        with self.assertRaises(ValidationError): tester.CLI._validate(prefix + "oper1 0 0 0")
        with self.assertRaises(ValidationError): tester.CLI._validate(prefix + "oper1 -")

        self.assertEqual(self.__format_validation(tester.CLI._validate(prefix + "oper2")), "args kwargs ")
        self.assertEqual(self.__format_validation(tester.CLI._validate(prefix + "oper2 ")), "args kwargs  :  {<value from: 0, 1>}")
        self.assertEqual(self.__format_validation(tester.CLI._validate(prefix + "oper2 0 ")), "args kwargs  :  {<value from: a, b>}")
        self.assertEqual(self.__format_validation(tester.CLI._validate(prefix + "oper2 0 ")), "args kwargs  :  {<value from: a, b>}")

        with self.assertRaises(ValidationError): tester.CLI._validate(prefix + "oper2 2")
        with self.assertRaises(ValidationError): tester.CLI._validate(prefix + "oper2 0 1")

    def test_delegation(self):
        prefix = "delegate "
        for i in range(1, 4):
            self.test_type_annotation(prefix * i)

        tester = self.tester()
        tester.locked(True)
        with self.assertRaises(ValidationError): tester.CLI._validate("delegate")
        with self.assertRaises(ValidationError): tester.CLI._validate("delegate oper1")
        tester.locked(False)
        tester.CLI._validate("delegate")
        tester.CLI._validate("delegate oper1")