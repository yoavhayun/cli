import os
import prompt_toolkit as prompt
import traceback
import sys

from class_cli._colors import colors
import class_cli._cli_prompt as cli_prompt
import class_cli._cli_parser as cli_parser

class cli_session:

    def __init__(self, name, description, instance, methods, settings, parser, style):
        self.name = name
        self.description = description
        self._methods = methods
        self._settings = settings
        self._parser = parser
        self._style = style
        self._instance = instance

        self._prompt = self._build_prompt()
        self.isFile = False

    def run(self, *args):
        if len(args) == 0:
            self.__shell()
        else:
            self.runArgs(args)

    def runLine(self, line):
        """
        Parse and execute a single argument line

          @line argument line to parse and execute

        @Return whether or not the execution was successful
        """
        return self.runArgs(cli_prompt.split_input(line))

    def runArgs(self, args):
        """
        Parse and execute a single argument list

          @args list of args to parse and execute

        @Return whether or not the execution was successful
        """
        _input = args
        if len(_input) > 0:
            # Handle file comment commands
            if _input[0].startswith(cli_prompt.FILE_COMMENT):
                toPrint = ' '.join(_input)[1:].strip()
                availableColors = [k for k in vars(colors.fg).items() if not k[0].startswith('_')]
                for code in cli_prompt.FILE_COLORS:
                    if toPrint.lower().startswith(code):
                        toPrint = cli_prompt.FILE_COLORS[code]  + toPrint[len(code):].strip() + colors.reset
                        break
                prompt.print_formatted_text(prompt.ANSI(toPrint))
                return False
            # Handle end session command
            elif _input[0] in cli_prompt.CMD.END:
                return True
            try:
                if len(_input) == 2 and _input[0] in cli_prompt.CMD.SETTING and _input[1] in self._settings:
                    print("={}".format(self._settings[_input[1]]))
                    return False
                else:
                    flags = self._parser.parse_args(_input).__dict__
            except SystemExit: 
                self.isFile = False
                return False
            # Handle read commands from a file
            if _input[0] in cli_prompt.CMD.READ and not self.isFile:
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
            try:
                # Handle user defined methods and settings
                if keyword in self._methods:
                    args = [flags[arg] for arg in self._methods[keyword].__inspection__.args[1:]]
                    varargs = self._methods[keyword].__inspection__.varargs
                    varkw = self._methods[keyword].__inspection__.varkw
                    _args, kwargs = cli_prompt.format_extra_arguments(flags[varargs] if varargs is not None else None,
                                                flags[varkw] if varkw is not None else None)
                    args += _args

                    res = self._methods[keyword](*args, **kwargs)
                    if _input[0] in cli_prompt.CMD.SETTING:
                        print("={}".format(res))
                    elif res is not None:
                        print(res)
                # Handles printing of all settings
                elif keyword in cli_prompt.CMD.SETTING:
                        print('\n'.join(["{}={}".format(k, self._settings[k]) for k in self._settings.keys()]))
            except Exception as e:
                self._error(e)
                self._debug(traceback.format_exc())
                self.isFile = False
            return False
    
    def _error(self, msg):
        try:
            self._instance.CLI.log.error(msg)
        except:
            print("Error:", msg)

    def _debug(self, msg):
        try:
            self._instance.CLI.log.debug(msg)
        except: pass

    def getPrompt(self, parent=[]):
        return self._prompt

    def _build_prompt(self):
        """
        This method creates and returns a prompt method to handel user input
        """
        prefix = [(cli_prompt.STYLE.getStyle(cli_prompt.STYLE.PROMPT), self.name), (cli_prompt.STYLE.getStyle(cli_prompt.STYLE.MARKER), '> ')]

        status = cli_prompt.StatusBar(self._methods, self._settings)
        _prompt_session = prompt.PromptSession(message=prefix, style=self._style,
                                                history=prompt.history.FileHistory("./.history"),
                                                lexer=cli_prompt.CustomLexer(), 
                                                completer=cli_prompt.CustomCompleter(self._methods, self._settings),
                                                rprompt=status.rprompt, 
                                                validator=status, 
                                                bottom_toolbar=status)

        _prompt_session._prompt = _prompt_session.prompt
        def wrappedPrompt():
            """
            resets the prompts displayed information
            """
            input = _prompt_session._prompt()
            status.reset()
            return input

        _prompt_session.prompt = wrappedPrompt
        return _prompt_session

    def __shell(self, inputLines=None):
        """
        Runs the Interface as a shell program

          @parent the name of the parent Interface
          @inputLines a pre set list of input lines

        @Return whether or not the last input line was successful
        """
        if not self.isFile:
            self.printUsage()
        while inputLines is None or len(inputLines) > 0:
            if inputLines is None:
                print()
            try:
                inputLine = inputLines.pop(0) if inputLines is not None else self.getPrompt().prompt()
            except EOFError:
                break
            try:
                lastLine = self.runLine(inputLine)
                if lastLine:
                    break
            except SystemExit:
                if int(str(sys.exc_info()[1])) != 0:
                    raise
            except Exception as e:
                traceback.print_exc()
                print(e)

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