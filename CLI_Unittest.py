import unittest, traceback
from class_cli.cli import CLI
import class_cli._cli_exception as cli_exception

class TestCLI__General(unittest.TestCase):
    def test_help_behavior(self):
        """
        Test that calling help does not raise an Exception from argparse
        """
        cli = CLI()
        @cli.Program()
        class Tester:
            pass

        Tester().CLI.run("--help")

class TestCLI_Compilation(unittest.TestCase):

    def test_missing_implementation(self):
        """
        Test for exception when there is Validation without a Setting or an Operation
        """
        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def foo(self): pass
        with self.assertRaises(cli_exception.InitializationException): Tester()

        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def foo(self): pass
            @cli.Setting()
            def foo(self): pass
        Tester()

        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def foo(self): pass
            @cli.Operation()
            def foo(self): pass
        Tester()
    
    def test_duplicate_names(self):
        """
        Test that a method cannot have multiple executions for the same name
        """
        cli = CLI()

        with self.assertRaises(cli_exception.CompilationException):
            @cli.Program(verbosity=None)
            class Tester:
                @cli.Operation()
                def foo(self): pass
                @cli.Setting()
                def foo(self): pass

        with self.assertRaises(cli_exception.CompilationException):
            @cli.Program(verbosity=None)
            class Tester:
                @cli.Operation()
                def foo(self): pass
                @cli.Operation()
                def foo(self): pass

        with self.assertRaises(cli_exception.CompilationException):
            @cli.Program(verbosity=None)
            class Tester:
                @cli.Setting()
                def foo(self): pass
                @cli.Setting()
                def foo(self): pass


    def test_multiple_instances(self):
        """
        Tests isolation between multiple instances
        """
        cli = CLI()

        @cli.Program(verbosity=None)
        class Tester:
            def __init__(self): self._value=0

        tester1 = Tester()
        tester2 = Tester()
        self.assertEqual(tester1._value, tester2._value, "Setup failed to produce the same field value for 2 different instances")
        tester1._value = 1
        self.assertEqual(tester1._value, 1, TestCLI_Methods.ERROR_FIELD_NOT_MODIFIED)
        self.assertNotEqual(tester1._value, tester2._value, TestCLI_Methods.ERROR_FIELD_MODIFIED)
        tester2._value = 1
        self.assertEqual(tester1._value, tester2._value, TestCLI_Methods.ERROR_FIELD_MODIFIED)
    
    def test_matching_signature(self):
        """
        Tests that matching signatures compiles
        """
        class TMP: pass
        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self, a, _a, b=1, c=[0, ''], *args, **kwargs): pass
            @cli.Operation()
            def oper(self, a, _a, b=1, c=[0, ''], *args, **kwargs): pass
        Tester()

    def test_non_matching_signature(self):
        """
        Tests for exception when defining non-matching method signature
        """

        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self, a): pass
            @cli.Operation()
            def oper(self, b): pass
        with self.assertRaises(cli_exception.InitializationException, None, "Failed on different names"): 
            Tester()

        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self, *a): pass
            @cli.Operation()
            def oper(self, *b): pass
        with self.assertRaises(cli_exception.InitializationException, None, "Failed on different *args names"): 
            Tester()

        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self, **a): pass
            @cli.Operation()
            def oper(self, **b): pass
        with self.assertRaises(cli_exception.InitializationException, None, "Failed on different **kwargs names"): 
            Tester()

        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self, *a): pass
            @cli.Operation()
            def oper(self): pass
        with self.assertRaises(cli_exception.InitializationException, None, "Failed on missing *args"): 
            Tester()

        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self): pass
            @cli.Operation()
            def oper(self, *a): pass
        with self.assertRaises(cli_exception.InitializationException, None, "Failed on missing *args"): 
            Tester()

        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self, **a): pass
            @cli.Operation()
            def oper(self): pass
        with self.assertRaises(cli_exception.InitializationException, None, "Failed on missing **kwargs"): 
            Tester()

        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self): pass
            @cli.Operation()
            def oper(self, **a): pass
        with self.assertRaises(cli_exception.InitializationException, None, "Failed on missing **kwargs"): 
            Tester()

        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self, a=0): pass
            @cli.Operation()
            def oper(self, a): pass
        with self.assertRaises(cli_exception.InitializationException, None, "Failed on non matching default values"): 
            Tester()

        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self, a): pass
            @cli.Operation()
            def oper(self, a=0): pass
        with self.assertRaises(cli_exception.InitializationException, None, "Failed on non matching default values"): 
            Tester()

    def test_constructor_accessability(self):
        """
        Tests for exception when trying to access CLI methods or setting before
        """
        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            def __init__(self):
                self.value("value")
            
            @cli.Setting()
            def value(self, values):
                return value

        with self.assertRaises(cli_exception.InitializationException): Tester()

        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            def __init__(self):
                self.CLI.value
            
            @cli.Setting()
            def value(self, values):
                return value

        with self.assertRaises(AttributeError): Tester()





class TestCLI_Settings(unittest.TestCase):

    def setUp(self):
        cli = CLI()

        values = {"int":0, "str":'', "dict":{}, "list":[]}

        @cli.Program(verbosity=None)
        class Tester: 

            def __init__(self):
                self._silenced = False

            @cli.Setting(initial_value='')
            def set_str(self, value):
                return value

            @cli.Setting(initial_value=0)
            def set_int(self, value:int):
                return value

            @cli.Setting(initial_value=tuple())
            def set_args(self, *values):
                return values

            @cli.Setting(initial_value={})
            def set_kwargs(self, **values):
                return values

            @cli.Setting(initial_value=None)
            def set_dict(self, value:values):
                return value

            @cli.Setting(initial_value=None)
            def set_iterable(self, value:values.keys()):
                return value

            @cli.Setting(initial_value=None, updates_value=False)
            def set_constant(self, value):
                return value

            @cli.Validation()
            def set_exception(self, value):
                if not self._silenced:
                    raise Exception()

            @cli.Setting(initial_value=None)
            def set_exception(self, value):
                return value

            def _silence_exception(self):
                self._silenced = True

        self.tester = Tester
        self.values = values


    ERROR_INITIAL_VALUE = 'Setting initial value was not set correctly'
    ERROR_INSTANCE_CALL = 'Calling setting method directly from instance did not return the expected value.'
    ERROR_CLI_CALL = 'Calling setting method from CLI did not return the expected value.'
    ERROR_SETTING_NOT_MODIFIED = 'Setting value was not modified as expected.'
    ERROR_SETTING_MODIFIED = 'Setting value was modified, although it was not expected to.'

    def test_setting_str(self):
        """
        Test setting of type 'str'
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.set_str, '', TestCLI_Settings.ERROR_INITIAL_VALUE)

        expected = '1'
        self.assertEqual(tester.set_str("1"), expected, TestCLI_Settings.ERROR_INSTANCE_CALL)
        self.assertEqual(tester.CLI.set_str, expected, TestCLI_Settings.ERROR_SETTING_NOT_MODIFIED)
        expected = '2'
        self.assertEqual(tester.CLI.execute(".setting", "set_str", "2"), expected, TestCLI_Settings.ERROR_CLI_CALL)
        self.assertEqual(tester.CLI.set_str, expected, TestCLI_Settings.ERROR_SETTING_NOT_MODIFIED)

    def test_setting_int(self):
        """
        Test setting of type 'int'
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.set_int, 0, TestCLI_Settings.ERROR_INITIAL_VALUE)

        expected = 1
        self.assertEqual(tester.set_int(1), expected, TestCLI_Settings.ERROR_INSTANCE_CALL)
        self.assertEqual(tester.CLI.set_int, expected, TestCLI_Settings.ERROR_SETTING_NOT_MODIFIED)
        expected = 2
        self.assertEqual(tester.CLI.execute(".setting", "set_int", "2"), expected, TestCLI_Settings.ERROR_CLI_CALL)
        self.assertEqual(tester.CLI.set_int, expected, TestCLI_Settings.ERROR_SETTING_NOT_MODIFIED)

    def test_setting_args(self):
        """
        Test setting that accepts *args
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.set_args, tuple(), TestCLI_Settings.ERROR_INITIAL_VALUE)

        expected = (1, 2, 3, 4)
        self.assertEqual(tester.set_args(1, 2, 3, 4), expected, TestCLI_Settings.ERROR_INSTANCE_CALL)
        self.assertEqual(tester.CLI.set_args, expected, TestCLI_Settings.ERROR_SETTING_NOT_MODIFIED)
        expected = ('1', '2', '3', '4')
        self.assertEqual(tester.CLI.execute(".setting", "set_args", "1", "2", "3", "4"), expected, TestCLI_Settings.ERROR_CLI_CALL)
        self.assertEqual(tester.CLI.set_args, expected, TestCLI_Settings.ERROR_SETTING_NOT_MODIFIED)

    def test_setting_kwargs(self):
        """
        Test setting that accepts *kwargs
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.set_kwargs, {}, TestCLI_Settings.ERROR_INITIAL_VALUE)

        expected = {"_1":1, "_2":2, "_3":3, "_4":4}
        self.assertEqual(tester.set_kwargs(_1=1, _2=2, _3=3, _4=4), expected, TestCLI_Settings.ERROR_INSTANCE_CALL)
        self.assertEqual(tester.CLI.set_kwargs, expected, TestCLI_Settings.ERROR_SETTING_NOT_MODIFIED)

        expected = {"1":"1", "2":"2", "3":"3", "4":"4"}
        self.assertEqual(tester.CLI.execute(".setting", "set_kwargs", "1=1", "2=2", "3=3", "4=4"), expected, TestCLI_Settings.ERROR_CLI_CALL)
        self.assertEqual(tester.CLI.set_kwargs, expected, TestCLI_Settings.ERROR_SETTING_NOT_MODIFIED)

    def test_setting_dict(self):
        """
        Test setting that accepts values from a dict
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.set_dict, None, TestCLI_Settings.ERROR_INITIAL_VALUE)

        self.values["new"] = "New Value"
        for key in self.values:
            expected = self.values[key]
            self.assertEqual(tester.CLI.execute(".setting", "set_dict", key), expected, TestCLI_Settings.ERROR_CLI_CALL)
            self.assertEqual(tester.CLI.set_dict, expected, TestCLI_Settings.ERROR_SETTING_NOT_MODIFIED)

    def test_setting_iterable(self):
        """
        Test setting that accepts values from an iterable
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.set_iterable, None, TestCLI_Settings.ERROR_INITIAL_VALUE)

        self.values["new"] = "New Value"
        for key in self.values:
            expected = key
            self.assertEqual(tester.CLI.execute(".setting", "set_iterable", key), expected, TestCLI_Settings.ERROR_CLI_CALL)
            self.assertEqual(tester.CLI.set_iterable, expected, TestCLI_Settings.ERROR_SETTING_NOT_MODIFIED)

        non_existing = '-'

        with self.assertRaises(cli_exception.InputException):
            tester.CLI.execute(".setting", "set_iterable", non_existing)

    def test_setting_constant(self):
        """
        Test setting that has a constant value
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.set_constant, None, TestCLI_Settings.ERROR_INITIAL_VALUE)

        expected_return = ''
        expected_value = None
        self.assertEqual(tester.set_constant(''), expected_return, TestCLI_Settings.ERROR_INSTANCE_CALL)
        self.assertEqual(tester.CLI.set_constant, expected_value, TestCLI_Settings.ERROR_SETTING_MODIFIED)

        self.assertEqual(tester.CLI.execute(".setting", "set_constant" ,''), expected_return, TestCLI_Settings.ERROR_CLI_CALL)
        self.assertEqual(tester.CLI.set_constant, expected_value, TestCLI_Settings.ERROR_SETTING_MODIFIED)


    def test_setting_exception(self):
        """
        Test setting that has Validation() attached
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.set_exception, None, TestCLI_Settings.ERROR_INITIAL_VALUE)

        with self.assertRaises(Exception):
            tester.set_exception('0')
        self.assertEqual(tester.CLI.set_exception, None, TestCLI_Settings.ERROR_SETTING_MODIFIED)

        expected = None
        self.assertEqual(tester.CLI.execute(".setting", "set_exception", "0"), expected)
        self.assertEqual(tester.CLI.set_exception, expected, TestCLI_Settings.ERROR_SETTING_MODIFIED)
        
        tester._silence_exception()
        expected = ''
        self.assertEqual(tester.set_exception(''), expected, TestCLI_Settings.ERROR_INSTANCE_CALL)
        self.assertEqual(tester.CLI.set_exception, expected, TestCLI_Settings.ERROR_SETTING_NOT_MODIFIED)

        expected = '0'
        self.assertEqual(tester.CLI.execute(".setting", "set_exception", "0"), expected, TestCLI_Settings.ERROR_CLI_CALL)
        self.assertEqual(tester.CLI.set_exception, expected, TestCLI_Settings.ERROR_SETTING_NOT_MODIFIED)

    def test_assert_setting_isolation(self):
        """
        Test that 2 different instances operate on different settings
        """
        tester1 = self.tester()
        tester2 = self.tester()
        self.assertEqual(tester1.CLI.set_str, tester2.CLI.set_str, "Setup failed to produce the same setting value for 2 different instances")
        tester1.set_str("value")
        self.assertEqual(tester1.CLI.set_str, "value", TestCLI_Settings.ERROR_SETTING_NOT_MODIFIED)
        self.assertNotEqual(tester1.CLI.set_str, tester2.CLI.set_str, TestCLI_Settings.ERROR_SETTING_MODIFIED)
        tester2.set_str("value")
        self.assertEqual(tester1.CLI.set_str, tester2.CLI.set_str, TestCLI_Settings.ERROR_SETTING_MODIFIED)









class TestCLI_Methods(unittest.TestCase):

    def setUp(self):
        cli = CLI()

        values = {"int":0, "str":'', "dict":{}, "list":[]}

        @cli.Program(verbosity=None)
        class Tester: 

            def __init__(self):
                self._silenced = False
                self._value = None

            @cli.Operation()
            def op_str(self, value):
                self._value = value
                return value

            @cli.Operation()
            def op_int(self, value:int):
                self._value = value
                return value

            @cli.Operation()
            def op_args(self, *values):
                self._value = values
                return values

            @cli.Operation()
            def op_kwargs(self, **values):
                self._value = values
                return values

            @cli.Operation()
            def op_dict(self, value:values):
                self._value = value
                return value

            @cli.Operation()
            def op_iterable(self, value:values.keys()):
                self._value = value
                return value

            @cli.Validation()
            def op_exception(self, value):
                if not self._silenced:
                    raise Exception()

            @cli.Operation()
            def op_exception(self, value):
                self._value = value
                return value

            def _silence_exception(self):
                self._silenced = True

        self.tester = Tester
        self.values = values


    ERROR_INITIAL_VALUE = 'Class initial value was not set correctly'
    ERROR_INSTANCE_CALL = 'Calling operation method directly from instance did not return the expected value.'
    ERROR_CLI_CALL = 'Calling operation method from CLI did not return the expected value.'
    ERROR_FIELD_NOT_MODIFIED = 'Field value was not modified as expected.'
    ERROR_FIELD_MODIFIED = 'Field value was modified, although it was not expected to.'

    def test_operation_str(self):
        """
        Test operation of type 'str'
        """
        tester = self.tester()
        self.assertEqual(tester._value, None, TestCLI_Methods.ERROR_INITIAL_VALUE)

        expected = '1'
        self.assertEqual(tester.op_str("1"), expected, TestCLI_Methods.ERROR_INSTANCE_CALL)
        self.assertEqual(tester._value, expected, TestCLI_Methods.ERROR_FIELD_NOT_MODIFIED)
        expected = '2'
        self.assertEqual(tester.CLI.execute("op_str", "2"), expected, TestCLI_Methods.ERROR_CLI_CALL)
        self.assertEqual(tester._value, expected, TestCLI_Methods.ERROR_FIELD_NOT_MODIFIED)

    def test_operation_int(self):
        """
        Test operation of type 'int'
        """
        tester = self.tester()
        self.assertEqual(tester._value, None, TestCLI_Methods.ERROR_INITIAL_VALUE)

        expected = 1
        self.assertEqual(tester.op_int(1), expected, TestCLI_Methods.ERROR_INSTANCE_CALL)
        self.assertEqual(tester._value, expected, TestCLI_Methods.ERROR_FIELD_NOT_MODIFIED)
        expected = 2
        self.assertEqual(tester.CLI.execute("op_int", "2"), expected, TestCLI_Methods.ERROR_CLI_CALL)
        self.assertEqual(tester._value, expected, TestCLI_Methods.ERROR_FIELD_NOT_MODIFIED)

    def test_operation_args(self):
        """
        Test operation that accepts *args
        """
        tester = self.tester()
        self.assertEqual(tester._value, None, TestCLI_Methods.ERROR_INITIAL_VALUE)

        expected = (1, 2, 3, 4)
        self.assertEqual(tester.op_args(1, 2, 3, 4), expected, TestCLI_Methods.ERROR_INSTANCE_CALL)
        self.assertEqual(tester._value, expected, TestCLI_Methods.ERROR_FIELD_NOT_MODIFIED)
        expected = ('1', '2', '3', '4')
        self.assertEqual(tester.CLI.execute("op_args", "1", "2", "3", "4"), expected, TestCLI_Methods.ERROR_CLI_CALL)
        self.assertEqual(tester._value, expected, TestCLI_Methods.ERROR_FIELD_NOT_MODIFIED)

    def test_operation_kwargs(self):
        """
        Test operation that accepts *kwargs
        """
        tester = self.tester()
        self.assertEqual(tester._value, None, TestCLI_Methods.ERROR_INITIAL_VALUE)

        expected = {"_1":1, "_2":2, "_3":3, "_4":4}
        self.assertEqual(tester.op_kwargs(_1=1, _2=2, _3=3, _4=4), expected, TestCLI_Methods.ERROR_INSTANCE_CALL)
        self.assertEqual(tester._value, expected, TestCLI_Methods.ERROR_FIELD_NOT_MODIFIED)

        expected = {"1":"1", "2":"2", "3":"3", "4":"4"}
        self.assertEqual(tester.CLI.execute("op_kwargs", "1=1", "2=2", "3=3", "4=4"), expected, TestCLI_Methods.ERROR_CLI_CALL)
        self.assertEqual(tester._value, expected, TestCLI_Methods.ERROR_FIELD_NOT_MODIFIED)

    def test_operation_dict(self):
        """
        Test operation that accepts values from a dict
        """
        tester = self.tester()
        self.assertEqual(tester._value, None, TestCLI_Methods.ERROR_INITIAL_VALUE)

        self.values["new"] = "New Value"
        for key in self.values:
            expected = self.values[key]
            self.assertEqual(tester.CLI.execute("op_dict", key), expected, TestCLI_Methods.ERROR_CLI_CALL)
            self.assertEqual(tester._value, expected, TestCLI_Methods.ERROR_FIELD_NOT_MODIFIED)

    def test_operation_iterable(self):
        """
        Test operation that accepts values from an iterable
        """
        tester = self.tester()
        self.assertEqual(tester._value, None, TestCLI_Methods.ERROR_INITIAL_VALUE)

        self.values["new"] = "New Value"
        for key in self.values:
            expected = key
            self.assertEqual(tester.CLI.execute("op_iterable", key), expected, TestCLI_Methods.ERROR_CLI_CALL)
            self.assertEqual(tester._value, expected, TestCLI_Methods.ERROR_FIELD_NOT_MODIFIED)
        
        non_existing = '-'

        with self.assertRaises(cli_exception.InputException):
            tester.CLI.execute("op_iterable", non_existing)


    def test_operation_exception(self):
        """
        Test operation that has Validation() attached
        """
        tester = self.tester()
        self.assertEqual(tester._value, None, TestCLI_Methods.ERROR_INITIAL_VALUE)

        with self.assertRaises(Exception):
            tester.op_exception('0')
        self.assertEqual(tester._value, None, TestCLI_Methods.ERROR_FIELD_MODIFIED)

        expected = None
        self.assertEqual(tester.CLI.execute("op_exception", "0"), expected)
        self.assertEqual(tester._value, expected, TestCLI_Methods.ERROR_FIELD_MODIFIED)
        
        tester._silence_exception()
        expected = ''
        self.assertEqual(tester.op_exception(''), expected, TestCLI_Methods.ERROR_INSTANCE_CALL)
        self.assertEqual(tester._value, expected, TestCLI_Methods.ERROR_FIELD_NOT_MODIFIED)

        expected = '0'
        self.assertEqual(tester.CLI.execute("op_exception", "0"), expected, TestCLI_Methods.ERROR_CLI_CALL)
        self.assertEqual(tester._value, expected, TestCLI_Methods.ERROR_FIELD_NOT_MODIFIED)

    def test_assert_operation_isolation(self):
        """
        Test that 2 different instances operate on different methods
        """
        tester1 = self.tester()
        tester2 = self.tester()
        self.assertEqual(tester1._value, tester2._value, "Setup failed to produce the same field value for 2 different instances")
        tester1.op_str("value")
        self.assertEqual(tester1._value, "value", TestCLI_Methods.ERROR_FIELD_NOT_MODIFIED)
        self.assertNotEqual(tester1._value, tester2._value, TestCLI_Methods.ERROR_FIELD_MODIFIED)
        tester2.op_str("value")
        self.assertEqual(tester1._value, tester2._value, TestCLI_Methods.ERROR_FIELD_MODIFIED)


class TestCLI_Parser(unittest.TestCase):

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
        self.assertEqual(tester.CLI.run("oper_type 5"), tester.oper_type(5))
        self.assertEqual(tester.CLI.run("oper_type -5"), tester.oper_type(-5))
        with self.assertRaises(cli_exception.InputException):
            tester.CLI.run("oper_type -")

    def test_parser_args(self):
        """
        Test for parsers handeling of *args
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.run("oper_args a"), tester.oper_args('a'))
        self.assertEqual(tester.CLI.run("  oper_args  a  "), tester.oper_args('a'))
        self.assertEqual(tester.CLI.run("oper_args a   b    c"), tester.oper_args('a', 'b', 'c'))

    def test_parser_kwargs(self):
        """
        Test for parsers handeling of **kwargs
        """
        tester = self.tester()
        with self.assertRaises(cli_exception.InputException):
            tester.CLI.run("oper_kwargs a")
        self.assertEqual(tester.CLI.run("oper_kwargs a=1"), tester.oper_kwargs(a='1'))
        self.assertEqual(tester.CLI.run("oper_kwargs a=1   b=2    c=3"), tester.oper_kwargs(a='1', b='2', c='3'))

    def test_parser_both(self):
        """
        Test for parsers handeling of both *args and **kwargs
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.run("oper_both a"), tester.oper_both('a'))
        self.assertEqual(tester.CLI.run("oper_both a=1"), tester.oper_both(a='1'))
        self.assertEqual(tester.CLI.run("oper_both a b c"), tester.oper_both('a', 'b', 'c'))
        self.assertEqual(tester.CLI.run("oper_both a=1 b=2 c=3"), tester.oper_both(a='1', b='2', c='3'))
        self.assertEqual(tester.CLI.run("oper_both a b c a=1 b=2 c=3"), tester.oper_both('a', 'b', 'c', a='1', b='2', c='3'))
        self.assertEqual(tester.CLI.run("oper_both a=1 a b b=2 c c=3"), tester.oper_both('a', 'b', 'c', a='1', b='2', c='3'))

    def test_parser_all(self):
        """
        Test for parsers handeling of both *args and **kwargs and an expected argument with type convertion
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.run("oper_all 5 a=1 a b b=2 c c=3"), tester.oper_all(5, 'a', 'b', 'c', a='1', b='2', c='3'))
        self.assertEqual(tester.CLI.run("oper_all 5 a=1 a b b=2 c c=3"), tester.oper_all(5, 'a', 'b', 'c', a='1', b='2', c='3'))
        with self.assertRaises(cli_exception.InputException):
            tester.CLI.run("oper_all - a=1 a b b=2 c c=3")



if __name__ == "__main__":
    unittest.main()