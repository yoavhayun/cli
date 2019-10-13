"""
This module handles the abstraction of methods for the cli

Author: Hayun, Yoav 
Email: YoavHayun@gmail.com
"""

from collections import OrderedDict, defaultdict
from enum import Enum
import inspect
import class_cli._cli_parser as cli_parser

class Method:
    """
    A class representing a CLI method which links all the different implementation parts of a method
    """

    def __init__(self, name):
        self.__name__ = name
        self._execution = None
        self._validations = []
        self.attributes = {}
    
    def __str__(self):
        return "{}({}): {}".format(self.__name__, len(self._validations), list(self._executions.keys()))
    
    def setExecution(self, execution, type="Method"):
        """
        Sets the execution implementation for this method
        """
        if self._execution is not None:
            compilationException = Exception("A Method can only have 1 execution implementation")
            raise compilationException
        self._execution = execution
        self._type = type

    def addValidation(self, validation):
        """
        Sets an argument validation implementation part for this method
        """
        if validation not in self._validations:
            self._validations.append(validation)

    def __check_preconditions(self, instance):
        """
        Checks that compilation parts are all valid
        Run this before compiling
        """
        compilationException = None
        if self._execution is None:
            compilationException = Exception("{} '{}' has declared validation but did not found an implementation".format(self._type, self.__name__))

        def compare_specs(spec1, spec2, attribute, extractor):
            if getattr(spec1, attribute) is None or getattr(spec2, attribute) is None:
                if getattr(spec1, attribute) is None and getattr(spec2, attribute) is None:
                    return 
                else:
                    return Exception("{} '{}' has validation with '{}' signature not matching its operation".format(self._type, self.__name__, attribute))

            ls1 = extractor(getattr(spec1, attribute))
            ls2 = extractor(getattr(spec2, attribute))
            if len(ls1) != len(ls2):
                return Exception("{} '{}' has validation with '{}' signature not matching its operation".format(self._type, self.__name__, attribute))
            for i, attrib in enumerate(ls1):
                if ls2[i] != attrib:
                    return Exception("{} '{}' has validation with non matching '{}' ({} != {})".format(self._type, self.__name__, attribute, attrib, ls2[i]))

        if compilationException is None:
            spec = self._execution.__spec__ if hasattr(self._execution, "__spec__") else inspect.getfullargspec(self._execution)
            for validation in self._validations:
                validation_spec = validation.__spec__ if hasattr(validation, "__spec__") else inspect.getfullargspec(validation)

                attributes = {
                    "args" : lambda x:x,
                    "defaults" : lambda x:x,
                    "annotations" : lambda x:[x[k] for k in x],
                    "varargs" : lambda x:x,
                    "varkw" : lambda x:x,
                }
                for attribute in attributes:
                    compilationException = compare_specs(spec, validation_spec, attribute, attributes[attribute])
                    if compilationException is not None:
                        break

        if compilationException is not None:
            raise compilationException

    def _compile(self, instance):
        """
        Compiles a method with it's operation and validation
        operation can be a CLI.Operation and CLI.Setting
        """
        self.__check_preconditions(instance)

        this = self
        execution = self._execution

        # Bundle all the implementations together
        @cli_parser.copy_argspec(execution)
        def method(*args, **kwargs):
            for validation in this._validations:
                validation(instance, *args, **kwargs)
            return this._execution(instance, *args, **kwargs)

        # Update the documentation of the method
        if execution.__doc__ is not None:
            method.__doc__ = cli_parser.copy_argspec._format_doc(execution.__doc__)
        else:
            method.__doc__ = "{} '{}'".format(self._type, self.__name__)
        for validation in self._validations:
            if validation.__doc__ is not None:
                method.__doc__ += '\n' + '\n'.join(
                    ['* ' + l for l in cli_parser.copy_argspec._format_doc(validation.__doc__).split('\n') if l != ""])
        method.__doc__ += '\n' + cli_parser.DOC_SEP


        execution = method
        return execution


class CLI_Methods(OrderedDict):
    """
    A Methods dictionary used to gather all implementation parts of a group of methods
    """

    def __init__(self, value=None):
        self.value = None
        self._complied_methods = defaultdict(OrderedDict)
        self._wrapped_methods = defaultdict(OrderedDict)
        self._settings = defaultdict(OrderedDict)


    def __getitem__(self, item):
        if item not in self:
            self[item] = Method(item)
        
        return super(OrderedDict, self).__getitem__(item)

    def compiled(self, instance):
        return self._wrapped_methods[instance]

    def settings(self, instance):
        return self._settings[instance]

    def _compile(self, instance):
        for method in self:
            self._complied_methods[instance][method] = cli_parser.add_method_inspection(self[method]._compile(instance))

            # Handle Settings
            if self[method]._type == "Setting":
                self._settings[instance][method] = self[method].attributes["initial_value"]
                def wrapper():
                    _method = method[:]
                    @cli_parser.copy_argspec(self._complied_methods[instance][_method])
                    def setting(*args, **kwargs):
                        res = self._complied_methods[instance][_method](*args, **kwargs)
                        if self[_method].attributes["updates_value"]:
                            self._settings[instance][_method] = res
                        return res
                    return setting
                self._wrapped_methods[instance][method] = wrapper()
            # Handle Operations
            else:
                def wrapper():
                    _method = method[:]
                    @cli_parser.copy_argspec(self._complied_methods[instance][_method])
                    def operation(*args, **kwargs):
                        return self._complied_methods[instance][_method](*args, **kwargs)
                    return operation
                self._wrapped_methods[instance][method] = wrapper()