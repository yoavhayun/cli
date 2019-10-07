"""
This module handles the prompt for the cli

Author: Hayun, Yoav 
Email: YoavHayun@gmail.com
"""

import shlex, platform, enum
import prompt_toolkit as prompt
from cli._colors import colors

# Defines a unique value for arguments with no defaults
class NO_DEFAULT:
    """
    This class represents a value for arguments without a default value
    It is needed since the user can use None as a default value for an argument
    """
    def __eq__(self, other):
        return other.__class__ == self.__class__ or other == self.__class__

# Defines format for textual comments
FILE_COMMENT = '#'
FILE_COLORS = {code + '#': color for code, color in [i for i in vars(colors.fg).items() if not i[0].startswith('_')]}

# Defines known inner commands
class CMD:
    END = ["q", "quit", "exit"]
    READ = [".r", ".read"]
    SETTING = [".set", ".setting"]
    HELP = ["-h", "--help"]

# Defines editable styles
class STYLE(enum.Enum):
    INPUT = "input"
    PROMPT = "prompt"
    MARKER = "marker"
    STATUSBAR = 'bottom-toolbar'

    @staticmethod
    def getStyle(style):
        return "class:{}".format(style.value)

def remove_quotes(string):
    """
    removes the main quatation marks from a given string
    """
    if string.startswith("'") or string.startswith('"'):
        string = string[1:-1]
    return string

def split_input(line):
    """
    Splits an input line given by the user into it's components
    """
    input = shlex.split(line, posix=(platform.system()!='Windows'))

    return [remove_quotes(part) for part in input if part!='']

def format_extra_arguments(varargs, varkw):
    """
    formats *args and **kwargs as tuple([args], {key=value}) 
    """
    extras = []
    if varargs is not None:
        extras += [v for v in varargs if v != ""]
    if varkw is not None:
        extras += varkw
        extras = [e.split('=') for e in extras if e != ""]
    else:
        extras = [[e] for e in extras]

    return [e[0] for e in extras if len(e) == 1], {e[0] : e[1] for e in extras if len(e) == 2 }

def extract_details(doc):
    """
    extracts the main details needed for all classes defined here.
    return keyword, input, word, quote
        keyword = first word of the current line
        input   = the entire input sectioned into it's components
        word    = the last word in the line
        quote   = whether or not the last item is path of quatation
    """
    _quote = False
    try:
        _input = shlex.split(doc.current_line, posix=(platform.system()!='Windows'))
    except:
        try:
            _input = shlex.split(doc.current_line + '"', posix=(platform.system()!='Windows'))
        except:
            _input = shlex.split(doc.current_line + "'", posix=(platform.system()!='Windows'))
        finally:
            _quote = True

    if not _quote and doc.char_before_cursor == ' ':
        _input.append('')
    _word = _input[-1] if len(_input) >= 1 else ""
    _keyword = _input[0] if len(_input) >= 1 else ""
            
    _input = [remove_quotes(part) if not(_quote and i == len(_input)-1) else part for i, part in enumerate(_input) if part not in CMD.HELP]
    return _keyword, _input, _word, _quote

class CustomLexer(prompt.lexers.Lexer):
    """
    This class formats the input line
    """
    def lex_document(self, document):

        def get_line(lineno):
            return [(STYLE.getStyle(STYLE.INPUT), document.lines[lineno])]

        return get_line

class StatusBar(prompt.validation.Validator):
    """
    This class is responsible for the status bar.
    The status bar displays guiding information about the input being entered by the user
    It also performs basic validation of the input entered
    """
    StyleSelected = "#0000FF bg:#FFFF00"
    StyleItem     = "#555555 bg:#FFFF00"
    StyleType     = "#000000 bg:#EEEEEE"
    def __call__(self):
        """
        return the status line to be displayed
        """
        if not hasattr(self, "_msg"): self._msg = ""
        return self._msg

    def __init__(self, methods, settings):
        self.methods = methods
        self.settings = settings

    def reset(self):
        """
        resets the status line
        """
        self._msg = ""
        self._rprompt = ""

    def rprompt(self):
        if not hasattr(self, "_rprompt"): self._rprompt = ""
        return prompt.formatted_text.FormattedText([(self.StyleSelected, str(self._rprompt))])

    def validate(self, document):
        self.reset()
        return self._validate(document)

    def _validate(self, document):
        """
        Main method for controling the status bar
        """
        try:
            shlex.split(document.current_line, posix=(platform.system()!='Windows'))
        except:
            raise prompt.validation.ValidationError(message="Missing closing quotation")

        _keyword, _input, _word, _ = extract_details(document)
        idx = len(_input) - 1

        if _keyword in CMD.READ:
            if len(_input) > 2 and not(len(_input) == 3 and _word==""):

                raise prompt.validation.ValidationError(message="Reading from a file accepts only 1 file. (if the path contains spaces, wrap with quotations)")
        # Handle Setting input
        if _keyword in CMD.SETTING:
            _input = _input[1:]
            _keyword = _input[0] if len(_input) else ""
            idx -= 1
        # Handle Operation input
        if _keyword in self.methods:
            ins = self.methods[_keyword].__inspection__
            args = [a for a in ins.args]
            # Define basic type validator
            def _validate_arg(type, value):
                try:
                    if value not in CMD.HELP:
                        type(value)
                except Exception as e:
                    raise prompt.validation.ValidationError(message=str(e))  
            types = [(t, lambda v, t=t: _validate_arg(t,v)) for t in ins.types]
            defaults = [d for d in ins.defaults]
            extras_name = []
            extras_type = []
            values = _input[len(_input) - max(0, idx - len(args) + 1):]
            _inp = (values, None) if ins.varkw is None else (None, values)
            _args, _kwargs = format_extra_arguments(*_inp)

            # Collect information on *args and **kwargs
            if ins.varargs is not None:
                extras_name.append("*{}".format(ins.varargs))
                extras_type.append("{} [items={}]".format(list, len(_args)))
            if ins.varkw is not None:
                extras_name.append("**{}".format(ins.varkw))
                extras_type.append("{} [items={}]".format(dict, len(_kwargs.keys())))

            # Define basic validaion on *args and **kwargs
            def validate_extras(arg, varargs, varkw):
                if arg not in CMD.HELP:
                    if varargs is None and varkw is not None:
                        if len(arg.split('=')) != 2:
                            raise prompt.validation.ValidationError(message="'{}' must be in the format [key]=[value]".format(arg))

            # Format information on *args and **kwargs
            if len(extras_name) > 0:
                args.append('{' + "{}".format(', '.join(extras_name)) + '}')
                types.append(("{}".format(', '.join(extras_type)), 
                            lambda val, varargs=ins.varargs, varkw=ins.varkw: validate_extras(val, varargs, varkw)))
                defaults.append(None)
            
            # Limit index of current word to the number of expected arguments
            if ins.varargs is not None or ins.varkw is not None:
                idx = min(idx, len(args)-1)
            else:
                # No extra args, validate the length of the input
                idx_test = idx-1 if len([_input]) and _input[-1] == "" else idx
                if idx_test > len(args)-1:
                    self.reset()
                    raise prompt.validation.ValidationError(message="Too many inputs for operation '{}'".format(_keyword))

            try:
                len_normal_args = len(args) - sum([1 for extra in [ins.varargs, ins.varkw] if extra is not None])
                if idx < len(args):
                    def part(idx):
                        return "{}{}".format(
                                        args[idx], 
                                        "[={}]".format(defaults[idx]) if defaults[idx] != NO_DEFAULT and idx < len_normal_args  else ''
                                        )
                    msg = [(self.StyleItem if i != idx else self.StyleSelected, part(i)) for i in range(1, len(args))]
                    msg += [(self.StyleType, ' :  {' + str(types[idx][0]) + '}' if idx != 0 else "")]
                    self._msg = prompt.formatted_text.FormattedText(StatusBar.intersperse(msg, ('', ' ')))

                    return
            finally:
                # Perform basic validation on all input parts
                for i, part in enumerate(_input[1:]):
                    if ins.varargs is not None or ins.varkw is not None:
                        i = min(len(args)-2, i)
                    if i+1 < len(types):
                        validator = types[i+1][1]
                        if validator and part != "":
                            validator(part)
    
    @staticmethod
    def intersperse(lst, item):
        result = [item] * (len(lst) * 2 - 1)
        result[0::2] = lst
        return result
    
class CustomCompleter(prompt.completion.Completer):
    """
    Class for suggesting possible completion keywords
    """
    def __init__(self, methods, settings):
        self.path_completer = prompt.completion.PathCompleter(expanduser=True)
        self.methods = methods
        self.settings = settings

    def get_path_completion(self, document, complete_event, trim_input=0):
        """
        Get relevant complitions from the OS filesystem
        """
        sub_doc = prompt.document.Document(document.text[trim_input:])
        yield from (prompt.completion.Completion(completion.text, completion.start_position, display=completion.display)
                    for completion
                    in self.path_completer.get_completions(sub_doc, complete_event))

    def _get_arg_completions(self, _input, keyword):
        """
        Get relevant complations for the current typed argument
        """
        types = self.methods[keyword].__inspection__.types
        current = len(_input) - 1
        if current < len(types):
            try:
                return types[current].__complete__(_input[-1])
            except:
                pass
        return []

    def get_completions(self, document, complete_event):
        _keyword, _input, _word, _quote = extract_details(document)
        if _quote:
            quote = _input[-1][1:-1]
            for path_starter in ["/", "\\"]:
                if path_starter in quote:
                    yield from self.get_path_completion(document, complete_event, trim_input=document.text.rfind(_input[-1][:-1]) + 1)
                    break
        options = []
        # Complete for file comments
        if _keyword.startswith(FILE_COMMENT) and _word == _keyword:
            options = ["{}{}".format(FILE_COMMENT,k) for k in FILE_COLORS.keys()]
        
        # Complete for Settings
        elif _input and _keyword in CMD.SETTING:
            _input = _input[1:]
            _keyword = _input[0] if len(_input) else ""
            if _keyword == "" or _keyword == _word:
                options = [k for k in self.methods.keys() if k in self.settings]
            
            elif _keyword in self.methods:
                options = self._get_arg_completions(_input, _keyword)
        
        # Complete for read command
        elif _input and _keyword in CMD.READ:
            if len(_input) > 1:
                yield from self.get_path_completion(document, complete_event, trim_input=document.text.find(_keyword)+len(_keyword)+1)

        # Complete for the very first word given 
        elif _keyword == "" or _keyword == _word:
            options = [k for k in self.methods.keys() if k not in self.settings] + [CMD.SETTING[-1], CMD.READ[-1]]
        
        # Complete for current argument
        elif _keyword in self.methods:
            options = self._get_arg_completions(_input, _keyword)

        # Add the help suggestion
        for option in (["--help"] if _word.startswith('-') else []) + options:
            if option.startswith(_word):
                yield prompt.completion.Completion(
                    option if ' ' not in option else "'{}'".format(option),
                    start_position=-len(_word),
                    selected_style='fg:yellow bg:darkgrey')