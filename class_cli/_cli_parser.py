"""
This module handles the argument parsing for the cli

Author: Hayun, Yoav 
Email: YoavHayun@gmail.com
"""

import argparse, inspect
from collections.abc import Iterable

import class_cli._cli_prompt as cli_prompt

DOC_SEP = '========================='

class copy_argspec(object):
    """
    copy_argspec is a signature modifying decorator.  Specifically, it copies
    the signature from `source_func` to the wrapper, and the wrapper will call
    the original function (which should be using *args, **kwds).  The argspec,
    docstring, and default values are copied from src_func, and __module__ and
    __dict__ from tgt_func.
    """
    def __init__(self, src_func):
        self.source = src_func
        self.source.__spec__  = src_func.__spec__ if hasattr(src_func, "__spec__") else inspect.getfullargspec(src_func)

    def __call__(self, wrapped, shallow=False):
        wrapped.__name__ = self.source.__name__
        wrapped.__doc__ = copy_argspec._format_doc(self.source.__doc__)
        wrapped.__spec__ = self.source.__spec__
        if not shallow:
            wrapped.__module__ = self.source.__module__
            wrapped.__dict__ = self.source.__dict__
        return wrapped
    
    @staticmethod
    def _format_doc(doc):
        if doc is not None:
            lines = doc.split('\n')
            # remove all starting empty lines
            while lines[0] == "":
                lines = lines[1:]
            # find base indention based on the first line
            indent =  lines[0].find(lines[0].strip()) if len(lines) else 0
            # remove indent from all lines
            doc = '\n'.join([line[indent:] for line in lines])
        return doc

def _fixType(_type):
    """
    Converts an enumerable type into a relevant callable
    """

    if isinstance(_type, Iterable):
        class DictOptions:
            def __init__(self, options={}):
                self.options = options
                self.converts = {str(o): o for o in options}

            def __call__(self, key):
                if key not in [str(o) for o in self.options]:
                    raise Exception("'{}' is not a valid option".format(key))
                return self.options[self.converts[key]]
            
            def __complete__(self, key):
                return [str(k) for k in self.options.keys() if str(k).lower().startswith(key.lower())]
            
            def __str__(self):
                return ', '.join([str(k) for k in self.options.keys()])

        class ListOptions:
            def __init__(self, options=[]):
                self.options = options
                self.converts = {str(o): o for o in options}

            def __call__(self, key):
                if key not in [str(o) for o in self.options]:
                    raise Exception("'{}' is not a valid option".format(key))
                return self.converts[key]
            
            def __complete__(self, key):
                return [str(k) for k in self.options if str(k).lower().startswith(key.lower())]
            
            def __str__(self):
                return ', '.join([str(opt) for opt in self.options])

        if type(_type) is dict:
            _type = DictOptions(_type)
        elif type(_type) in [list, set, type({}.keys()), type(range(0))]:
            _type = ListOptions(_type)

    return _type


def add_method_inspection(method):
    """
    Adds '__inspection__' attribute to the given method, which contains details on it's documentation and signature
    """
    method.__inspection__ = argparse.Namespace()
    # copy existing specs
    spec = method.__spec__
    for arg in spec._fields:
        method.__inspection__.__setattr__(arg, spec.__getattribute__(arg))
    ins = method.__inspection__
    # add default argument values
    if ins.defaults is not None:
        method.__inspection__.defaults = [cli_prompt.NO_DEFAULT() for i in range(len(ins.args) - len(ins.defaults))] + [d for d in ins.defaults]
    else:
        method.__inspection__.defaults = [cli_prompt.NO_DEFAULT() for i in range(len(ins.args))]

    # add type convertions
    method.__inspection__.__setattr__("types", [_fixType(ins.annotations[arg]) if arg in ins.annotations else str for arg in ins.args])

    # format documentation
    method.__inspection__.__setattr__("docs", ["" for i in range(len(ins.args))])
    method.__inspection__.__setattr__("extra_docs", {key : "" for key in [ins.varargs, ins.varkw] if key is not None})
    for line in method.__doc__.split('\n') if method.__doc__ is not None else []:
        for i, arg in enumerate(method.__inspection__.args):
            if line.lower().find('@{}'.format(arg.lower())) >= 0:
                method.__inspection__.docs[i] += ('\n' if len(method.__inspection__.docs[i]) else '') + \
                                                    ' '.join(line.replace('@{}'.format(arg), '').strip().split())
                break
        else:
            for key in method.__inspection__.extra_docs.keys():
                if line.lower().find('@{}'.format(key.lower())) >= 0:
                    method.__inspection__.extra_docs[key] += ('\n' if len(method.__inspection__.extra_docs[key]) else '') + \
                                                                ' '.join(line.replace('@{}'.format(key), '').strip().split()[1:])
                    break
    return method

def _create_method_parser(parser, method):
    """
    Populates an argparse parser from a given method
    """
    # remove self argument
    args = method.__inspection__.args[1:]
    types = method.__inspection__.types[1:]
    defaults = method.__inspection__.defaults[1:]
    docs = method.__inspection__.docs[1:]

    # Add all method arguments to parser
    _started_defaults = False
    first = True
    for arg, type, default, doc in zip(args, types, defaults, docs):
        if first:
            doc = "{}\n{}".format(DOC_SEP, doc)
            first = False
        if _started_defaults or default != cli_prompt.NO_DEFAULT:
            parser.add_argument(arg, nargs='?', type=type, default=default, help="{} (default: {})\n{}".format(doc, default, DOC_SEP))
            _started_defaults = True
        else:
            parser.add_argument(arg, type=type, help="{}\n{}".format(doc, DOC_SEP))
    # Add *args and **kwargs support
    if method.__inspection__.varargs is not None:
        providedHelp = method.__inspection__.extra_docs[method.__inspection__.varargs] if method.__inspection__.varargs is not None else None
        _help = providedHelp if providedHelp != "" else "Additional arguments (A List of values)"
        if len(args) == 0:
            _help = "{}\n{}".format(DOC_SEP, _help)
        parser.add_argument(method.__inspection__.varargs, nargs='*', default=[], help="{}\n{}".format(_help, DOC_SEP))
    if method.__inspection__.varkw is not None:
        providedHelp = method.__inspection__.extra_docs[method.__inspection__.varkw] if method.__inspection__.varkw is not None else None
        _help = providedHelp if providedHelp != "" else "Additional keyword arguments"
        if len(args) == 0 and method.__inspection__.varargs is None:
            _help = "{}\n{}".format(DOC_SEP, _help)
        parser.add_argument(method.__inspection__.varkw, nargs='*', default={}, help="{}\n(list of [key]=[value])\n{}".format(_help, DOC_SEP))
    return parser

def create_parser(name, methods, settings):
    """
    Creates an argparse parser from a list of methods and settings

    Accepts:
        @name       the name of the parser
        @methods    A dictionary of compiled methods and settings with added inspection
        @settings   A list of setting names for the cli settings parser
    """
    parser = argparse.ArgumentParser(name, formatter_class=argparse.RawTextHelpFormatter)

    methods_keys = [k for k in methods.keys() if k not in settings]
    # Defines a subparser for each Operation
    method_parsers = parser.add_subparsers(metavar='{' + ",".join(methods_keys) + '}')
    for idx, method in enumerate(methods_keys):
        if methods[method].__doc__ is not None:
            _description = copy_argspec._format_doc(methods[method].__doc__)
        else:
            _description = "Method {} of Class {}".format(method, name)
        _help = _description if idx > 0 else "{}\n{}".format(DOC_SEP, _description)
        
        method_parser = method_parsers.add_parser(method, description="{}\n{}".format(DOC_SEP, _description), help=_help, formatter_class=argparse.RawTextHelpFormatter)
        method_parser = _create_method_parser(method_parser, methods[method])

    
    # Defines parsers for all user defined settings
    if len(settings):
        for setting_key in cli_prompt.CMD.SETTING:
            settings_parser = method_parsers.add_parser(setting_key, description="Access the program settings", formatter_class=argparse.RawTextHelpFormatter)
            settings_parsers = settings_parser.add_subparsers()
            for idx, setting in enumerate(settings):
                if methods[setting].__doc__ is not None:
                    _description = copy_argspec._format_doc(methods[setting].__doc__)
                else:
                    _description = "Setting {} of Class {}".format(setting, name)
                _help = _description if idx > 0 else "{}\n{}".format(DOC_SEP, _description)
                
                setting_parser = settings_parsers.add_parser(setting, description="{}\n{}".format(DOC_SEP, _description), help=_help, formatter_class=argparse.RawTextHelpFormatter)
                setting_parser = _create_method_parser(setting_parser, methods[setting])
    
    # Defines a parser for read command to read commands from a file
    for read_key in cli_prompt.CMD.READ:
        read_parser = method_parsers.add_parser(read_key, formatter_class=argparse.RawTextHelpFormatter)
        read_parser.add_argument("filepath", help="Path to a file.\n\tuse quotation to enable path autocompletion")

    return parser