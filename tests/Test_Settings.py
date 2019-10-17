import unittest
from class_cli.cli import CLI
import class_cli._cli_exception as cli_exception

class Settings(unittest.TestCase):
    
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
        self.assertEqual(tester.CLI.set_str, '', Settings.ERROR_INITIAL_VALUE)

        expected = '1'
        self.assertEqual(tester.set_str("1"), expected, Settings.ERROR_INSTANCE_CALL)
        self.assertEqual(tester.CLI.set_str, expected, Settings.ERROR_SETTING_NOT_MODIFIED)
        expected = '2'
        self.assertEqual(tester.CLI.execute(".setting", "set_str", "2"), expected, Settings.ERROR_CLI_CALL)
        self.assertEqual(tester.CLI.set_str, expected, Settings.ERROR_SETTING_NOT_MODIFIED)

    def test_setting_int(self):
        """
        Test setting of type 'int'
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.set_int, 0, Settings.ERROR_INITIAL_VALUE)

        expected = 1
        self.assertEqual(tester.set_int(1), expected, Settings.ERROR_INSTANCE_CALL)
        self.assertEqual(tester.CLI.set_int, expected, Settings.ERROR_SETTING_NOT_MODIFIED)
        expected = 2
        self.assertEqual(tester.CLI.execute(".setting", "set_int", "2"), expected, Settings.ERROR_CLI_CALL)
        self.assertEqual(tester.CLI.set_int, expected, Settings.ERROR_SETTING_NOT_MODIFIED)

    def test_setting_dict(self):
        """
        Test setting that accepts values from a dict
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.set_dict, None, Settings.ERROR_INITIAL_VALUE)

        self.values["new"] = "New Value"
        for key in self.values:
            expected = self.values[key]
            self.assertEqual(tester.CLI.execute(".setting", "set_dict", key), expected, Settings.ERROR_CLI_CALL)
            self.assertEqual(tester.CLI.set_dict, expected, Settings.ERROR_SETTING_NOT_MODIFIED)

    def test_setting_iterable(self):
        """
        Test setting that accepts values from an iterable
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.set_iterable, None, Settings.ERROR_INITIAL_VALUE)

        self.values["new"] = "New Value"
        for key in self.values:
            expected = key
            self.assertEqual(tester.CLI.execute(".setting", "set_iterable", key), expected, Settings.ERROR_CLI_CALL)
            self.assertEqual(tester.CLI.set_iterable, expected, Settings.ERROR_SETTING_NOT_MODIFIED)

        non_existing = '-'

        with self.assertRaises(cli_exception.InputException):
            tester.CLI.execute(".setting", "set_iterable", non_existing)

    def test_setting_constant(self):
        """
        Test setting that has a constant value
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.set_constant, None, Settings.ERROR_INITIAL_VALUE)

        expected_return = ''
        expected_value = None
        self.assertEqual(tester.set_constant(''), expected_return, Settings.ERROR_INSTANCE_CALL)
        self.assertEqual(tester.CLI.set_constant, expected_value, Settings.ERROR_SETTING_MODIFIED)

        self.assertEqual(tester.CLI.execute(".setting", "set_constant" ,''), expected_return, Settings.ERROR_CLI_CALL)
        self.assertEqual(tester.CLI.set_constant, expected_value, Settings.ERROR_SETTING_MODIFIED)


    def test_setting_exception(self):
        """
        Test setting that has Validation() attached
        """
        tester = self.tester()
        self.assertEqual(tester.CLI.set_exception, None, Settings.ERROR_INITIAL_VALUE)

        with self.assertRaises(Exception):
            tester.set_exception('0')
        self.assertEqual(tester.CLI.set_exception, None, Settings.ERROR_SETTING_MODIFIED)

        expected = None
        self.assertEqual(tester.CLI.execute(".setting", "set_exception", "0"), expected)
        self.assertEqual(tester.CLI.set_exception, expected, Settings.ERROR_SETTING_MODIFIED)
        
        tester._silence_exception()
        expected = ''
        self.assertEqual(tester.set_exception(''), expected, Settings.ERROR_INSTANCE_CALL)
        self.assertEqual(tester.CLI.set_exception, expected, Settings.ERROR_SETTING_NOT_MODIFIED)

        expected = '0'
        self.assertEqual(tester.CLI.execute(".setting", "set_exception", "0"), expected, Settings.ERROR_CLI_CALL)
        self.assertEqual(tester.CLI.set_exception, expected, Settings.ERROR_SETTING_NOT_MODIFIED)

    def test_assert_setting_isolation(self):
        """
        Test that 2 different instances operate on different settings
        """
        tester1 = self.tester()
        tester2 = self.tester()
        self.assertEqual(tester1.CLI.set_str, tester2.CLI.set_str, "Setup failed to produce the same setting value for 2 different instances")
        tester1.set_str("value")
        self.assertEqual(tester1.CLI.set_str, "value", Settings.ERROR_SETTING_NOT_MODIFIED)
        self.assertNotEqual(tester1.CLI.set_str, tester2.CLI.set_str, Settings.ERROR_SETTING_MODIFIED)
        tester2.set_str("value")
        self.assertEqual(tester1.CLI.set_str, tester2.CLI.set_str, Settings.ERROR_SETTING_MODIFIED)