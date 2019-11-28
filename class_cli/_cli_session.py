"""
This module handles the prompt for the cli

Author: Hayun, Yoav 
Email: YoavHayun@gmail.com
"""

import os, sys
import prompt_toolkit as prompt
from prompt_toolkit.patch_stdout import patch_stdout
import traceback

from class_cli._colors import colors
import class_cli._cli_prompt as cli_prompt
import class_cli._cli_parser as cli_parser
import class_cli._cli_exception as cli_exception

class cli_session:

    def __init__(self, name, description, instance, methods, settings, delegations, parser, style, silent=False):
        self.name = name
        self.description = description
        self._methods = methods
        self._settings = settings
        self._delegations = delegations
        self._parser = parser
        self._style = style
        self._instance = instance
        self._parents = []
        self.setSilent(silent)

        self._completer = cli_prompt.CustomCompleter(self._methods, self._settings, self._delegations)
        self._status_bar = cli_prompt.StatusBar(self._methods, self._settings, self._delegations)

        self.isFile = False

        self._last_result = None

    def isSilent(self):
        """
        Returns whether the session prints to stdout
        """
        return self._silent
    
    def setSilent(self, silent=True):
        """
        Sets whether the session prints to stdout
        """
        self._silent = silent

    def run(self, *args):
        if len(args) == 0:
            self.__shell()
        else:
            self.__runArgs(args)
            return self._last_result

    def runLine(self, line):
        """
        Parse and execute a single argument line

          @line argument line to parse and execute

        @Return whether or not the execution was successful
        """
        return self.__runArgs(cli_prompt.split_input(line))

    def _delegate(self, parents, isSilent, *args):
        parents_state = self._parents
        silent_state = self._silent
        try:
            self._silent = isSilent
            self._parents = parents
            self.__shell(args)
        finally:
            self._parents = parents_state
            self._silent = silent_state

    def __runArgs(self, args):
        """
        Parse and execute a single argument list

          @args list of args to parse and execute

        @Return whether or not the execution was successful
        """
        self._status_bar.reset()
        for arg in args:
            if type(arg) != str:
                raise cli_exception.InputException("'{}'. Can only exectue on string arguments ({}={})".format(cli_prompt.join_input(args), arg, type(arg)))
        _input = args
        if len(_input) > 0:
            self._last_result = None

            # Handle file comment commands
            if _input[0].startswith(cli_prompt.FILE_COMMENT):
                toPrint = ' '.join(_input)[1:].strip()
                availableColors = [k for k in vars(colors.fg).items() if not k[0].startswith('_')]
                for code in cli_prompt.FILE_COLORS:
                    if toPrint.lower().startswith(code):
                        toPrint = cli_prompt.FILE_COLORS[code]  + toPrint[len(code):].strip() + colors.reset
                        break
                if not self.isSilent(): prompt.print_formatted_text(prompt.ANSI(toPrint))
                return False
            # Handle end session command
            elif _input[0] in cli_prompt.CMD.END:
                return True

            # Handle 
            fail = None
            try:
                if len(_input) == 2 and _input[0] in cli_prompt.CMD.SETTING and _input[1] in self._settings:
                    if not self.isSilent(): print("={}".format(self._settings[_input[1]]))
                    return False
                elif _input[0] in self._delegations:
                    delegated_cli = self._methods[_input[0]]()
                    # if len(_input[1:]) == 0:
                    delegated_cli.CLI._delegate(self._parents + [self.name], self.isSilent(), *_input[1:])
                    # else:
                    #     delegated_method = delegated_cli.CLI.execute if self.isSilent() else delegated_cli.CLI.run
                    #     self._last_result = delegated_method(*_input[1:])
                    return False
                else:
                    flags = self._parser.parse_args(_input).__dict__
            except SystemExit as e: 
                self.isFile = False
                if sum([1 if help_key in _input else 0 for help_key in cli_prompt.CMD.HELP]) == 0:
                    fail = cli_exception.InputException(cli_prompt.join_input(_input))
                else:
                    return False

            if fail is not None:
                raise fail
            # Handle read commands from a file
            if _input[0] in cli_prompt.CMD.READ:
                finish = False
                filepath = ' '.join(_input[1:])
                if os.path.isfile(filepath):
                    try:
                        self.isFile = True
                        with open(filepath) as file:
                            for line in file.readlines():
                                if line == "":
                                    continue
                                finish = self.runLine(line)
                                if not self.isFile:
                                    if not finish:
                                        self._error("Execution from file '{}' raised errors and is terminated".format(filepath))
                                    break
                    finally:
                        self.isFile = False
                else:
                    self._error("file '{}' doesn't exist".format(filepath))

                return finish
            
            keyword = _input[1] if _input[0] in cli_prompt.CMD.SETTING and len(_input) > 1 else _input[0]
            # Handle user defined methods and settings
            if keyword in self._methods:
                args = [flags[arg] for arg in self._methods[keyword].__inspection__.args[1:]]
                varargs = self._methods[keyword].__inspection__.varargs
                varkw = self._methods[keyword].__inspection__.varkw
                _args, kwargs = cli_prompt.format_extra_arguments(flags[varargs] if varargs is not None else None,
                                            flags[varkw] if varkw is not None else None)
                args += _args

                if varargs is None and len(_args) > 0:
                    raise cli_exception.InputException("'{}'. Method '{}' does not accept *args".format(_input, keyword))
                if varkw is None and len(kwargs) > 0:
                    raise cli_exception.InputException("'{}'. Method '{}' does not accept **kwargs".format(_input, keyword))

                # Execute the selected method
                try:
                    res = self._methods[keyword](*args, **kwargs)
                except Exception as e:
                    self._error(e)
                    self._debug(traceback.format_exc())
                    self.isFile = False
                else:
                    self._last_result = res
                    if _input[0] in cli_prompt.CMD.SETTING:
                        if not self.isSilent(): print("={}".format(res))
                    elif res is not None:
                        if not self.isSilent(): print(res)

            # Handles printing of all settings
            elif keyword in cli_prompt.CMD.SETTING:
                    if not self.isSilent(): print('\n'.join(["{}={}".format(k, self._settings[k]) for k in self._settings.keys()]))
            return False
    
    def _error(self, msg):
        try:
            self._instance.CLI.log.error(msg)
        except:
            if not self.isSilent(): print("Error:", msg)

    def _debug(self, msg):
        try:
            self._instance.CLI.log.debug(msg)
        except: pass

    def getPrompt(self, parents=[]):
        print()
        try:
            with patch_stdout():
                return self._run_prompt(parents)
        except prompt.output.win32.NoConsoleScreenBufferError:
            return input()
        finally:
            self._status_bar.reset()

    def _run_prompt(self, parents=[]):
        """
        This method creates and returns a prompt method to handel user input
        """
        prompt_args = {
            "message": [(cli_prompt.STYLE.getStyle(cli_prompt.STYLE.PROMPT), '\\'.join(parents + [self.name])), (cli_prompt.STYLE.getStyle(cli_prompt.STYLE.MARKER), '> ')], 
            "style": self._style,
            "history": prompt.history.FileHistory("./.history"),
            "lexer": cli_prompt.CustomLexer(), 
            "completer": self._completer,
            "rprompt": self._status_bar.rprompt, 
            "validator": self._status_bar, 
            "bottom_toolbar": self._status_bar
        }
        return prompt.shortcuts.prompt(**prompt_args)

    def __shell(self, args=None):
        """
        Runs the Interface as a shell program

          @parent the name of the parent Interface
          @inputLines a pre set list of input lines

        @Return whether or not the last input line was successful
        """
        delegated = self.isFile or len(self._parents) > 0 or args is not None
        if not delegated:
            self.printUsage()
        lastLine = False
        while not lastLine:
            try:
                _args = args if args is not None and len(args) > 0 else cli_prompt.split_input(self.getPrompt(self._parents))
            except EOFError:
                break
            try:
                lastLine = self.__runArgs(_args) or (args is not None and len(args) > 0)
            except SystemExit:
                self._debug(traceback.format_exc())
            except Exception as e:
                if not self.isSilent():
                    self._error(e)
                    if delegated: lastLine = True
                else:
                    raise

    def _format_command_options(self, commands):
        return "'" + "' '".join([cmd for cmd in commands]) + "'"

    def getUsage(self):
        prefix_usage = [
            (cli_prompt.STYLE.getStyle(cli_prompt.STYLE.INPUT), '\n{}\n'.format(self.description)),
            ("","\tTo exit, enter one of the following: "),
            ("bold", "{}\n".format(self._format_command_options(cli_prompt.CMD.END))),
            ("","\tTo read commands from a file, enter one of the following: "),
            ("bold", "{}\n".format(self._format_command_options(cli_prompt.CMD.READ))),
        ]

        dynamic_usage = []
        if len(self._settings) > 0:
            dynamic_usage.append(("", "\tTo access the program settings, enter one of the following: "))
            dynamic_usage.append(("bold", "{}\n".format(self._format_command_options(cli_prompt.CMD.SETTING))))

        suffix_usage = [
            ("bold", "\n\tAt any time, add '-h' flag to the command for help.\n")
        ]
        return prompt.formatted_text.FormattedText(prefix_usage + dynamic_usage + suffix_usage)

    def printUsage(self):
        """
        Prints the welcome usage information of the interface
        """
        prompt.print_formatted_text(self.getUsage(), style=self._style)