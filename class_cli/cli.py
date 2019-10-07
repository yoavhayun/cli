'''
A module for creating CLI from Python classes
Using the module encourages for well documented code while not demanding it.
It allows for separation in implementation between method execution and it's argument validations.

The CLI has the following capabilities:
    * Full command and argument auto-completion and suggestions
    * Basic type validation for entered arguments while typing
    * Full input line validation
    * Useful help messages for all methods and arguments 
    * Logging support
    * Command history
    * Execution of commands from a text file, line by line

The module exposes an API in the form of decorators. These are the available decorators:
    Program(name=None, version=None, description=None, log=None, style:dict=None, debug:bool=False)
        a class decorator that defines the CLI program.
        Instantiation of the wrapped user class can be used as normal python code, accessing all it's attributes.
        It also exposes the CLI interface with an added attribute named 'CLI'

        @name           The name of the CLI program.                                                (Default is the class name)
        @version        The version of the CLI program.                                             (Default is a CLI without versioning)
        @description    The description of the CLI program.                                         (Default is the class documentation)
        @log            A path to a log file.                                                       (Default is no log file)
        @style          A dictionary that overrides the styling of the CLI for the given keys       (Keys: CLI.STYLE)
        @debug          A boolean that defines if CLI method calling information should be logged   (Default is False)


    Operation
        a method decorator that defines the execution code of a method in the CLI

    Setting(initial_value, updates_value:bool=True)
        a method decorator that creates a setting value for the CLI with name equals to the method name.
        It defines the execution code for setting the value into the created setting.

        @initial_value      An initial value that the setting will hold after class initialization
        @updates_value      Whether or not calling this method automatically updates the inner setting value

    Validation
        A method decorator that defines a validation to be performed on an execution (Operation / Setting)
        Holds the same signature as the execution it is validating and raises an exception for invalid arguments.
        * An Operation or a Setting can have multiple Validations


Basic Example:
    This is a simple code that controls an integer via the Setting decorator
    It can only set/return it's value or add another integer to it.

                from cli.cli import CLI

                cli = CLI()

                @cli.Program()
                class IntegerController:
                    "CLI program description"

                    @cli.Setting(initial_value=None)
                    # Telling the CLI 'value' is of type int will perform automatic type validation and conversion
                    def value(self, value:int):
                        """
                        Setting Description

                            @value  Argument description 
                        """
                        return value

                    @cli.Validation
                    def add(self, value:int):
                        """
                        Validation Description 1
                        """
                        # Accessing a 'Setting' value is done via the CLI attribute
                        if self.CLI.value is None:
                            raise Exception("Must initialize setting 'value' before performing operations")
                    
                    @cli.Validation
                    def add(self, value:int):
                        """
                        Validation Description 2
                        """
                        # Accessing a 'Setting' value is done via the CLI attribute
                        if value == 0:
                            raise Exception("Adding 0 will do nothing to the Integer")
                    
                    @cli.Operation
                    def add(self, value:int):
                        """
                        Method Description

                            @value  Argument description 
                        """
                        self.value(self.CLI.value + value)
                        return self.CLI.value
                
                if __name__ == "__main__":
                    IntegerController().CLI.main()

    This provides the following interface behavior:

                IntegerController> .setting value
                value=None

                IntegerController> add 2
                2019-08-24 17:12:18,759
                [ERROR] Must initialize setting 'value' before performing operations

                IntegerController> .setting value 5
                value=5

                IntegerController> add 2
                7

                IntegerController> add 0
                2019-08-24 17:12:19,800
                [ERROR] Adding 0 will do nothing to the Integer

                IntegerController> .setting value
                value=7

    Initially the value was None, so trying to add 2 to it returned an error.
    After changing it to a valid value (5), adding 2 was possible. 
    Trying to add 0 also throws exceptions so the ending value was 7.
        * Because value was defined as int, the user could not have entered a non int input


    This could be solved by changing the main a bit and calling the method to set the value outside:
                if __name__ == "__main__":
                    ic = IntegerController()
                    ic.value(0)
                    ic.add(2)
                    ic.CLI.run()
                    print(ic.value())

    That has the following interface behavior:

                IntegerController> .setting value
                value=2

                IntegerController> add 2
                4

                IntegerController> .setting value
                value=4

    Information can be shown by adding '--help' or '-h' for short:

        For the entire CLI:

                usage: IntegerController [-h] {add} ...

                positional arguments:
                {add}
                    add       =========================
                            Method Description

                                @value  Argument description

                            * Validation Description 1
                            * Validation Description 2
                            =========================

                optional arguments:
                -h, --help  show this help message and exit

        For the add method:

                IntegerController> add -h
                usage: IntegerController add [-h] value

                =========================
                Method Description

                    @value  Argument description

                * Validation Description 1
                * Validation Description 2
                =========================

                positional arguments:
                value       =========================
                            Argument description
                            =========================

                optional arguments:
                -h, --help  show this help message and exit

        For the settings:

                IntegerController> .setting -h
                usage: IntegerController .setting [-h] {value} ...

                Access the program settings

                positional arguments:
                {value}
                    value     =========================
                            Setting Description

                                @value  Argument description

                            =========================

                optional arguments:
                -h, --help  show this help message and exit


Author: Hayun, Yoav 
Email: YoavHayun@gmail.com
'''

import logging
import sys
import os
import traceback
from collections import OrderedDict, defaultdict
from enum import Enum

import prompt_toolkit as prompt
from prompt_toolkit.patch_stdout import patch_stdout

from class_cli._colors import colors
import class_cli._cli_prompt as cli_prompt
import class_cli._cli_parser as cli_parser
import class_cli._cli_methods as cli_methods
import class_cli._cli_logger as cli_logger
from class_cli._cli_session import cli_session

class CLI():
    """
    Class for creating command line interfaces
    """

####################
# Exposure Class
####################

    # Defines how the user can access cli components (cli methods, user defined settings, ...)
    CLI_ACCESS_KEY = 'CLI'
    STYLE = cli_prompt.STYLE

    class CLI_Object:
        """
        This class defines an API exposed to the user useing the CLI_ACCESS_KEY String value.
        the access is done as follows (If CLI_ACCESS_KEY='CLI'):
            instance.CLI.[attribute]

        For Example
            Running the cli program:
                instance.CLI.run()
            Accessing the logger:
                instance.CLI.log
        """
        def __init__(self, cli):
            self.log = cli.logger

            self._cli = cli
            self.__cli_session = self._cli._Compile()

        def main(self):
            "A Default main execution of the CLI program"
            self.run(*(sys.argv[1:]))
        
        def run(self, *args):
            """
            starts the CLI program
            """
            self.__cli_session.run(*args)

        def __getattribute__(self, name):
            """
            Accessing compiled settings and methods of the class instance
            order of access is Setting -> Methods -> CLI_Object attributes
            """
            if name in object.__getattribute__(self, "_cli")._settings:
                return object.__getattribute__(self, "_cli")._settings[name]
            elif name in object.__getattribute__(self, "_cli")._methods:
                return object.__getattribute__(self, "_cli")._methods[name]
            else:
                return object.__getattribute__(self, name)

############
# Decorators
############

    def Operation(self, func):
        """
        Method Decorator
        Records a funcion as a CLI operation
        """
        self.methods_dict[func.__name__].setExecution(func)
        return self._redirection(func)
    
    def Setting(self, initial_value, updatesValue:bool=True):
        """
        Method Decorator
        Records a funcion as a CLI Setting
        Accepts:
            initial_value       the initial value of the setting on initialization
        To access the setting use : self.CLI.[setting]{=value}
        """
        def wrapper(func):
            self._settings[func.__name__] = initial_value
            @cli_parser.copy_argspec(func)
            def wrapped(*args, **kwargs):
                res = func(*args, **kwargs)
                if updatesValue:
                    self._settings[func.__name__] = res
                return res
            self.methods_dict[func.__name__].setExecution(wrapped)
            return self._redirection(wrapped)
        return wrapper

    def Validation(self, func):
        """
        Method Decorator
        Records a funcion as a CLI operation
        Accepts:
            func           The function should raise an exception if the operation is not to be executed
        """
        self.methods_dict[func.__name__].addValidation(func)
        return self._redirection(func)

    def Program(self, name=None, version=None, description=None, log=None, style:dict=None, debug:bool=False):
        """
        Class Decorator
        Defines the CLI Program using a class

        Accepts:
            name            The name of the Program (default: Name of wrapped class)
            version         The version of the program
            description     A textual description of the program
            style           Change the formatting style of the CLI components
                               Dict of { CLI.STYLE.[component].value : [Format Description] }
            debug           Whether to run the cli in DEBUG mode (default: False)

        Returns:
            A class decorator
        """

        # Defines access to the CLI instance
        parent = self

        # Override default style
        if style is not None:
            for key in style:
                self.style[key] = style[key]
        self._style = prompt.styles.Style.from_dict(self.style)

        # Defines the behavior of the class outsite a CLI environment (As a class instance)
        def cli_decorator(cls):
            class Wrapper:
                def __init__(self, *args, **kwargs):
                    modifiers = {"name":name, "version":version, "description":description, "log":log, "debug" : debug}
                    self._cli = parent._link_to_instance(self, cls, modifiers, *args, **kwargs)
                    # self.version = version
                    self.__name__ = type(self._cli.instance).__name__
                    self.__class__.__name__ = type(self._cli.instance).__name__
                    
                    self._cli.instance.CLI = CLI.CLI_Object(self._cli)

                def __getattribute__(self, name):
                    """
                    handels direct access to the wrapped instance attribute
                    """

                    # Check if requested access to CLI_Object defined attributes
                    if name == CLI.CLI_ACCESS_KEY:
                        return object.__getattribute__(self, "_cli").instance.CLI

                    try:
                        return object.__getattribute__(self, name)
                    except AttributeError as e:
                        return object.__getattribute__(object.__getattribute__(self, "_cli").instance, name)

            return Wrapper
        return cli_decorator

###############
# Setup Methods
###############

    def __init__(self):
        self.wrapped = None
        # Saves all the different implementations of all the methods
        self.methods_dict = cli_methods.CLI_Methods()
        # Saves all the setting values
        self._settings = OrderedDict()
        self._methods = OrderedDict()
        self._cli_access = False
        self._parser = None
        self.description = None

        # Define the default style to be used
        self.style = {
            cli_prompt.STYLE.PROMPT.value      : 'bold',
            cli_prompt.STYLE.MARKER.value      : 'bold',
            cli_prompt.STYLE.INPUT.value       : 'yellow',
            cli_prompt.STYLE.STATUSBAR.value   : '#000000 bg:#0000FF'
        }
    
    def _link_to_instance(self, wrapped, cls, modifiers, *args, **kwargs):
        """
        Links the CLI to an instance of the wrapped class
        """
        self.instance = cls(*args, **kwargs)
        self.instance.__setattr__(CLI.CLI_ACCESS_KEY, wrapped)
        self.wrapped = wrapped
        self.name = type(self.instance).__name__ if modifiers["name"] is None else modifiers["name"]
        self.version = modifiers["version"]
        self._class = wrapped.__class__
        self.description = "{}{}{}".format(self.name, 
                                            ' v' + self.version if self.version else '', 
                                            ': ' + modifiers["description"] if modifiers["description"] else '')
        self.logger = cli_logger.CLI_Logger(modifiers["log"], logging.DEBUG if modifiers["debug"] else logging.INFO).get_logger()
        return self

    def _redirection(self, func):
        """
        funcion Decorator to redirect the execution to it's compiled one
        """
        def redirected(*args, **kwargs):
            return self._methods[func.__name__](*(args[1:]), **kwargs)
        
        return cli_parser.copy_argspec(func)(redirected)

    def _Compile(self):
        """
        Compiles the class as a CLI
        """

        for method in self.methods_dict:
            self._methods[method] = cli_parser.add_method_inspection(self.methods_dict[method]._compile(self.instance))

        self._parser = cli_parser.create_parser(self.name, self._methods, self._settings)
        return cli_session(self.name, self.description, self.instance, self._methods, self._settings, self._parser, self._style)