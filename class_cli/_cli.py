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

Documentation can be found at https://pypi.org/project/class-cli/


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
from prompt_toolkit import document

from class_cli._colors import colors
import class_cli._cli_prompt as cli_prompt
import class_cli._cli_parser as cli_parser
import class_cli._cli_methods as cli_methods
import class_cli._cli_logger as cli_logger
import class_cli._cli_exception as cli_exceptions
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
            self._cli = cli # must be the first line
            self.__logger = cli.logger
            self.log = self.__logger.get_logger()

            self.name = self._cli.name
            self.__cli_session = self._cli._Compile()

        def run(self, *args):
            """
            Executes the given arguments on the CLI program
            * if not args are given, it will open the CLI program for user input
            """
            self.__logger.enable()
            res = self.__cli_session.run(*args)
            self.__logger.disable()
            return res

        def _complete(self, line):
            return [c.text for c in self.__cli_session._completer.get_completions(document.Document(line, len(line)))]
        
        def _validate(self, line):
            try:
                return self.__cli_session._status_bar._validate(document.Document(line, len(line)))
            finally:
                self.__cli_session._status_bar.reset()

        def main(self):
            """
            A default main execution of the CLI program
            """
            try:
                return self.run(*(sys.argv[1:]))
            except: pass

        def _delegate(self, parents, isSilent, *args):
            return self.__cli_session._delegate(parents, isSilent, *args)
        
        def __call__(self, line=''):
            """
            Executes a single input line on the program
            """
            return self.run(*cli_prompt.split_input(line))

        def execute(self, *args):
            """
            Silently executes the given argument on the CLI program, returning the result.
            
            """
            silent_state = self.__cli_session.isSilent()
            try:
                self.__cli_session.setSilent(True)
                return self.run(*args)
            finally:
                self.__cli_session.setSilent(silent_state)

        def __getattribute__(self, name):
            """
            Accessing compiled settings and methods of the class instance
            order of access is Setting -> Methods -> CLI_Object attributes
            """
            if name in object.__getattribute__(self, "_cli").methods_dict.settings(object.__getattribute__(self, "_cli").instance):
                return object.__getattribute__(self, "_cli").methods_dict.settings(object.__getattribute__(self, "_cli").instance)[name]
            else:
                return object.__getattribute__(self, name)

############
# Decorators
############

    def __define_decorators(self):
        """
        Defines all the method decorators available
        """
        self.__Operation = cli_methods.OperationDecorator(self.methods_dict)
        self.__Setting = cli_methods.SettingDecorator(self.methods_dict)
        self.__Delegate = cli_methods.DelegateDecorator(self.methods_dict)
        self.__Validation = cli_methods.ValidationDecorator(self.methods_dict)
    
    def Operation(self):
        """
        Method Decorator
        Defines a class method as a CLI Operation

        The wrapped method defines the execution of an operation in the CLI
        """
        return self.__Operation()

    def Setting(self, initial_value=None, updates_value=True):
        """
        Method Decorator
        Defines a class method as a CLI Setting

        The wrapped method defines how to set the value of the setting.
        It is expected to return the new value the setting should hold after execution.

        Accepts:
            @initial_value      The initial value the setting will hold after instantiation
            @updates_value      Wether or not calling the method will automatically update the setting value
                                    * When updates value is False, the wrapped method is expected to return a 
                                      string representation of the setting value
        """
        return self.__Setting(initial_value=initial_value, updates_value=updates_value)

    def Delegate(self, reuse=True):
        """
        Method Decorator
        Defines a class method as an access point to another CLI instance.

        The wrapped method should accept only 'self' as an argument and return a CLI instance.

        Accepts:
            @reuse      Whether or not the returned CLI instance should be cached for future calls 
        """
        return self.__Delegate(reuse)

    def Validation(self): 
        """
        Method Decorator
        Defines a class method as a validation part of a CLI Operation, Setting or Delegation
        """
        return self.__Validation()

    def Program(self, name=None, version=None, description=None, log=None, style=None, verbosity=logging.INFO):
        """
        Class Decorator
        Defines the CLI Program using a class

        Accepts:
            name            The name of the Program (default: Name of wrapped class)
            version         The version of the program
            description     A textual description of the program
            style           Change the formatting style of the CLI components
                               Dict of { CLI.STYLE.[component].value : [Format Description] }
            verbosity       The logger verbosity for STDOUT (default: logging.INFO)

        Returns:
            A class decorator
        """

        if self.__linked is not None:
            raise cli_exceptions.CompilationException("Each CLI instance can only wrap a single Class. Already wrapping '{}' Class".format(self.__linked))

        # Defines access to the CLI instance
        parent = self

        # Defines the behavior of the class outsite a CLI environment (As a class instance)
        def cli_decorator(cls):
            class Wrapper(cls):

                def __init__(self, *args, **kwargs):
                    cls.__init__(self, *args, **kwargs)
                    modifiers = {"name":name, "version":version, "description":description, "log":log, "style": style, "verbosity" : verbosity}
                    self.__name__ = cls.__name__
                    self._cli = parent._link_to_instance(self, cls, modifiers, *args, **kwargs)
                    
                    self.__class__.__name__ = type(self._cli.instance).__name__
                    
                    self.CLI = CLI.CLI_Object(self._cli)

            parent.__linked = cls.__name__

            return Wrapper
        

        return cli_decorator

###############
# Setup Methods
###############

    def __init__(self):
        self.wrapped = None
        # Saves all the different implementations of all the methods
        self.methods_dict = cli_methods.CLI_Methods()

        self.__linked = None

        # Define the default style to be used
        self.style = {
            cli_prompt.STYLE.PROMPT.value      : 'bold',
            cli_prompt.STYLE.MARKER.value      : 'bold',
            cli_prompt.STYLE.INPUT.value       : 'yellow',
            cli_prompt.STYLE.STATUSBAR.value   : '#000000 bg:#0000FF'
        }

        # Expose decorators
        self.__define_decorators()
    
    def _link_to_instance(self, wrapped, cls, modifiers, *args, **kwargs):
        """
        Links the CLI to an instance of the wrapped class
        """
        cli = CLI()
        cli.__linked = self.__linked
        cli.methods_dict = self.methods_dict
        
        cli.instance = wrapped#cls(*args, **kwargs)
        cli.instance.__setattr__(CLI.CLI_ACCESS_KEY, wrapped)
        cli.wrapped = wrapped
        cli.name = wrapped.__name__ if modifiers["name"] is None else modifiers["name"]
        cli.version = modifiers["version"]
        cli._class = wrapped.__class__
        cli.description = "{}{}:{}\n".format(cli.name, 
                                            ' v' + cli.version if cli.version else '', 
                                            '\n' + cli_parser.copy_argspec.format_doc(modifiers["description"], '\t') if modifiers["description"] else \
                                            ('\n' + cli_parser.copy_argspec.format_doc(cls.__doc__, '\t') if cls.__doc__ else '')
                                                        
                                            )
        cli.logger = cli_logger.CLI_Logger(modifiers["log"], modifiers["verbosity"])
        
        if modifiers["style"] is not None:
            for key in modifiers["style"]:
                cli.style[key] = modifiers["style"][key]

        return cli

    def _Compile(self):
        """
        Compiles the class as a CLI
        """
        self.methods_dict.compile(self.instance, CLI.CLI_Object)
        _methods = self.methods_dict.compiled(self.instance)
        _settings = self.methods_dict.settings(self.instance)
        _delegations = self.methods_dict.delegations(self.instance)
        _parser = cli_parser.create_parser(self.name, _methods, _settings)
        _style = prompt.styles.Style.from_dict(self.style)
        return cli_session(self.name, self.description, self.instance, _methods, _settings, _delegations, _parser, _style, silent=self.logger.isSilent())

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback): pass