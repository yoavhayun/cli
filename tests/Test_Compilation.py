import unittest
from class_cli.cli import CLI
import class_cli._cli_exception as cli_exception
from tests.Test_Methods import Methods

class Compilation(unittest.TestCase):
    
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
        self.assertEqual(tester1._value, 1, Methods.ERROR_FIELD_NOT_MODIFIED)
        self.assertNotEqual(tester1._value, tester2._value, Methods.ERROR_FIELD_MODIFIED)
        tester2._value = 1
        self.assertEqual(tester1._value, tester2._value, Methods.ERROR_FIELD_MODIFIED)
    
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

        # Test for different names
        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self, a): pass
            @cli.Operation()
            def oper(self, b): pass
        with self.assertRaises(cli_exception.InitializationException): 
            Tester()

        # Test for different *args names
        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self, *a): pass
            @cli.Operation()
            def oper(self, *b): pass
        with self.assertRaises(cli_exception.InitializationException): 
            Tester()

        # Test for different **kwargs names
        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self, **a): pass
            @cli.Operation()
            def oper(self, **b): pass
        with self.assertRaises(cli_exception.InitializationException): 
            Tester()

        # Test for missing *args
        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self, *a): pass
            @cli.Operation()
            def oper(self): pass
        with self.assertRaises(cli_exception.InitializationException): 
            Tester()

        # Test for missing *args
        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self): pass
            @cli.Operation()
            def oper(self, *a): pass
        with self.assertRaises(cli_exception.InitializationException): 
            Tester()

        # Test for missing **kwargs
        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self, **a): pass
            @cli.Operation()
            def oper(self): pass
        with self.assertRaises(cli_exception.InitializationException): 
            Tester()

        # Test for missing **kwargs
        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self): pass
            @cli.Operation()
            def oper(self, **a): pass
        with self.assertRaises(cli_exception.InitializationException): 
            Tester()

        # Test for non matching default values
        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self, a=0): pass
            @cli.Operation()
            def oper(self, a): pass
        with self.assertRaises(cli_exception.InitializationException): 
            Tester()

        # Test for non matching default values
        cli = CLI()
        @cli.Program(verbosity=None)
        class Tester:
            @cli.Validation()
            def oper(self, a): pass
            @cli.Operation()
            def oper(self, a=0): pass
        with self.assertRaises(cli_exception.InitializationException): 
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