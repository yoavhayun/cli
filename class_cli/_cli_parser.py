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
        wrapped.__doc__ = copy_argspec.format_doc(self.source.__doc__)
        wrapped.__spec__ = self.source.__spec__
        if not shallow:
            wrapped.__module__ = self.source.__module__
            wrapped.__dict__ = self.source.__dict__
        return wrapped
    
    @staticmethod
    def format_doc(doc, line_prefix='', line_suffix=''):
        """
        formats a raw document
        fixes all leading whitespaces

        Accepts:
            @line_prefix    will appear at the beggining of each line
            @line_suffix    will appear at the end of each line
        """
        if doc is not None:
            lines = doc.split('\n')
            while len(lines) > 0 and lines[0].strip() == '':
                lines = lines[1:]
            while len(lines) > 0 and lines[-1].strip() == '':
                lines = lines[:-1]
            sep = min([len(line) - len(line.lstrip()) for line in lines if line.strip() != '']) if len(lines) > 0 else 0
            doc = '\n'.join([line_prefix + line[sep:] + line_suffix for line in lines])
        return doc

def _wrap_iterable_types(_type):
    """
    Converts an enumerable type into a relevant callable
    """

    if isinstance(_type, Iterable):
        if type(_type) is dict:
            _type = DictOptions(_type)
        else:
            _type = IterableOptions(_type)

    return _type

class IterableOptions:
    """
    Acts as an annotation for iterables
    """
    def __init__(self, options):
        self.options = options

    def __call__(self, key):
        if key not in [str(o) for o in self.options]:
            raise TypeError("'{}' is not a valid option".format(key))
        return self[key]
    
    def __complete__(self, key):
        return [str(o) for o in self.options if str(o).lower().startswith(key.lower())]

    def find(self, key):
        for option in self.options:
            if str(option) == key:
                return option

    def __getitem__(self, key):
        return self.find(key)

    def __str__(self):
        options = [k for k in self.options]
        if len(options) > 3:
            options = options[:2] + ['...'] + [options[-1]]
        return "<value from: {}>".format(', '.join([str(k) for k in options]))

    def __repr__(self):
        return str(self)

class DictOptions(IterableOptions):
    """
    Acts as an annotation for dictionaries
    """
    def __getitem__(self, key):
        return self.options[self.find(key)]

    def __str__(self):
        return IterableOptions.__str__(self)

    def __repr__(self):
        return str(self)



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
    method.__inspection__.__setattr__("types", [_wrap_iterable_types(ins.annotations[arg]) if arg in ins.annotations else str for arg in ins.args])

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
            doc = "{}\n{}".format(DOC_SEP, doc if len(doc) > 0 else "'{}' argument of method '{}'".format(arg, method.__name__))
            first = False
        if _started_defaults or default != cli_prompt.NO_DEFAULT:
            parser.add_argument(arg, nargs='?', type=type, default=default, help="{} (default: {})\nType:{}\n{}".format(doc, default, type, DOC_SEP))
            _started_defaults = True
        else:
            parser.add_argument(arg, type=type, help="{}\nType: {}\n{}".format(doc, type, DOC_SEP))
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
            _description = copy_argspec.format_doc(methods[method].__doc__)
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
                    _description = copy_argspec.format_doc(methods[setting].__doc__)
                else:
                    _description = "Setting {} of Class {}".format(setting, name)
                _help = _description if idx > 0 else "{}\n{}".format(DOC_SEP, _description)
                
                setting_parser = settings_parsers.add_parser(setting, description="{}\n{}".format(DOC_SEP, _description), help=_help, formatter_class=argparse.RawTextHelpFormatter)
                setting_parser = _create_method_parser(setting_parser, methods[setting])
    
    # Defines a parser for read command to read commands from a file
    for read_key in cli_prompt.CMD.READ:
        read_parser = method_parsers.add_parser(read_key, formatter_class=argparse.RawTextHelpFormatter)
        read_parser.add_argument("filepath", nargs='+', help="Path to a file.\n\tuse quotation to enable path autocompletion")

    return parser