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

from class_cli._cli import CLI
import class_cli._cli_exception as cli_exceptions