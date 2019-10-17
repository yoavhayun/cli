import unittest
from class_cli.cli import CLI
import class_cli._cli_exception as cli_exception

class Methods(unittest.TestCase):
    
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
        self.assertEqual(tester._value, None, Methods.ERROR_INITIAL_VALUE)

        expected = '1'
        self.assertEqual(tester.op_str("1"), expected, Methods.ERROR_INSTANCE_CALL)
        self.assertEqual(tester._value, expected, Methods.ERROR_FIELD_NOT_MODIFIED)
        expected = '2'
        self.assertEqual(tester.CLI.execute("op_str", "2"), expected, Methods.ERROR_CLI_CALL)
        self.assertEqual(tester._value, expected, Methods.ERROR_FIELD_NOT_MODIFIED)

    def test_operation_int(self):
        """
        Test operation of type 'int'
        """
        tester = self.tester()
        self.assertEqual(tester._value, None, Methods.ERROR_INITIAL_VALUE)

        expected = 1
        self.assertEqual(tester.op_int(1), expected, Methods.ERROR_INSTANCE_CALL)
        self.assertEqual(tester._value, expected, Methods.ERROR_FIELD_NOT_MODIFIED)
        expected = 2
        self.assertEqual(tester.CLI.execute("op_int", "2"), expected, Methods.ERROR_CLI_CALL)
        self.assertEqual(tester._value, expected, Methods.ERROR_FIELD_NOT_MODIFIED)

    def test_operation_args(self):
        """
        Test operation that accepts *args
        """
        tester = self.tester()
        self.assertEqual(tester._value, None, Methods.ERROR_INITIAL_VALUE)

        expected = (1, 2, 3, 4)
        self.assertEqual(tester.op_args(1, 2, 3, 4), expected, Methods.ERROR_INSTANCE_CALL)
        self.assertEqual(tester._value, expected, Methods.ERROR_FIELD_NOT_MODIFIED)
        expected = ('1', '2', '3', '4')
        self.assertEqual(tester.CLI.execute("op_args", "1", "2", "3", "4"), expected, Methods.ERROR_CLI_CALL)
        self.assertEqual(tester._value, expected, Methods.ERROR_FIELD_NOT_MODIFIED)

    def test_operation_kwargs(self):
        """
        Test operation that accepts *kwargs
        """
        tester = self.tester()
        self.assertEqual(tester._value, None, Methods.ERROR_INITIAL_VALUE)

        expected = {"_1":1, "_2":2, "_3":3, "_4":4}
        self.assertEqual(tester.op_kwargs(_1=1, _2=2, _3=3, _4=4), expected, Methods.ERROR_INSTANCE_CALL)
        self.assertEqual(tester._value, expected, Methods.ERROR_FIELD_NOT_MODIFIED)

        expected = {"1":"1", "2":"2", "3":"3", "4":"4"}
        self.assertEqual(tester.CLI.execute("op_kwargs", "1=1", "2=2", "3=3", "4=4"), expected, Methods.ERROR_CLI_CALL)
        self.assertEqual(tester._value, expected, Methods.ERROR_FIELD_NOT_MODIFIED)

    def test_operation_dict(self):
        """
        Test operation that accepts values from a dict
        """
        tester = self.tester()
        self.assertEqual(tester._value, None, Methods.ERROR_INITIAL_VALUE)

        self.values["new"] = "New Value"
        for key in self.values:
            expected = self.values[key]
            self.assertEqual(tester.CLI.execute("op_dict", key), expected, Methods.ERROR_CLI_CALL)
            self.assertEqual(tester._value, expected, Methods.ERROR_FIELD_NOT_MODIFIED)

    def test_operation_iterable(self):
        """
        Test operation that accepts values from an iterable
        """
        tester = self.tester()
        self.assertEqual(tester._value, None, Methods.ERROR_INITIAL_VALUE)

        self.values["new"] = "New Value"
        for key in self.values:
            expected = key
            self.assertEqual(tester.CLI.execute("op_iterable", key), expected, Methods.ERROR_CLI_CALL)
            self.assertEqual(tester._value, expected, Methods.ERROR_FIELD_NOT_MODIFIED)
        
        non_existing = '-'

        with self.assertRaises(cli_exception.InputException):
            tester.CLI.execute("op_iterable", non_existing)


    def test_operation_exception(self):
        """
        Test operation that has Validation() attached
        """
        tester = self.tester()
        self.assertEqual(tester._value, None, Methods.ERROR_INITIAL_VALUE)

        with self.assertRaises(Exception):
            tester.op_exception('0')
        self.assertEqual(tester._value, None, Methods.ERROR_FIELD_MODIFIED)

        expected = None
        self.assertEqual(tester.CLI.execute("op_exception", "0"), expected)
        self.assertEqual(tester._value, expected, Methods.ERROR_FIELD_MODIFIED)
        
        tester._silence_exception()
        expected = ''
        self.assertEqual(tester.op_exception(''), expected, Methods.ERROR_INSTANCE_CALL)
        self.assertEqual(tester._value, expected, Methods.ERROR_FIELD_NOT_MODIFIED)

        expected = '0'
        self.assertEqual(tester.CLI.execute("op_exception", "0"), expected, Methods.ERROR_CLI_CALL)
        self.assertEqual(tester._value, expected, Methods.ERROR_FIELD_NOT_MODIFIED)

    def test_assert_operation_isolation(self):
        """
        Test that 2 different instances operate on different methods
        """
        tester1 = self.tester()
        tester2 = self.tester()
        self.assertEqual(tester1._value, tester2._value, "Setup failed to produce the same field value for 2 different instances")
        tester1.op_str("value")
        self.assertEqual(tester1._value, "value", Methods.ERROR_FIELD_NOT_MODIFIED)
        self.assertNotEqual(tester1._value, tester2._value, Methods.ERROR_FIELD_MODIFIED)
        tester2.op_str("value")
        self.assertEqual(tester1._value, tester2._value, Methods.ERROR_FIELD_MODIFIED)