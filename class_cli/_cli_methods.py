"""
This module handles the abstraction of methods for the cli

Author: Hayun, Yoav 
Email: YoavHayun@gmail.com
"""

from collections import OrderedDict, defaultdict
from abc import ABC, abstractmethod
from enum import Enum
import inspect
import class_cli._cli_parser as cli_parser
import class_cli._cli_exception as cli_exception

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
            raise cli_exception.CompilationException("A Method can only have 1 execution implementation")
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
        if self._execution is None:
            raise cli_exception.InitializationException("method '{}' has declared validation but did not found an implementation".format(self.__name__))

        def compare_specs(spec1, spec2, attribute, extractor):
            if getattr(spec1, attribute) is None or getattr(spec2, attribute) is None:
                if getattr(spec1, attribute) is None and getattr(spec2, attribute) is None:
                    return 
                else:
                    raise cli_exception.InitializationException("{} '{}' has validation with '{}' signature not matching its operation".format(self._type, self.__name__, attribute))

            ls1 = extractor(getattr(spec1, attribute))
            ls2 = extractor(getattr(spec2, attribute))
            if len(ls1) != len(ls2):
                raise cli_exception.InitializationException("{} '{}' has validation with '{}' signature not matching its operation".format(self._type, self.__name__, attribute))
            for i, attrib in enumerate(ls1):
                if ls2[i] != attrib:
                    raise cli_exception.InitializationException("{} '{}' has validation with non matching '{}' ({} != {})".format(self._type, self.__name__, attribute, attrib, ls2[i]))

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
                compare_specs(spec, validation_spec, attribute, attributes[attribute])

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
                method.__doc__ += '\n\n' + '\n'.join(
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

class MethodDecorator(ABC):
    def __init__(self, methods_dict):
        self._methods_dict = methods_dict
        self.__attributes = {}
    
    @abstractmethod
    def _record_method(self, method): pass

    def __call__(self, method):
        self.__update_attributes(method)
        return self.__wrap_method(method)

    def _record_attributes(self, **attributes):
        for key in attributes:
            self.__attributes[key] = attributes[key]

    def __update_attributes(self, method):
        for key in self.__attributes:
            self._methods_dict[method.__name__].attributes[key] = self.__attributes[key]
        
        self.__attributes = {}

    def __wrap_method(self, method):
        self._record_method(method)

        @cli_parser.copy_argspec(method)
        def redirected(*args, **kwargs):
            linked_methods = self._methods_dict.compiled(args[0])
            if method.__name__ not in linked_methods:
                raise cli_exception.InitializationException("Cannot access CLI operations and settings before an instance is constructed")
            return linked_methods[method.__name__](*(args[1:]), **kwargs)
    
        return redirected

    
class OperationDecorator(MethodDecorator):
    def _record_method(self, method):
        self._methods_dict[method.__name__].setExecution(method, "Operation")

    def __call__(self): return super().__call__

class SettingDecorator(MethodDecorator):
    def _record_method(self, method):
        self._methods_dict[method.__name__].setExecution(method, "Setting")

    def __call__(self, initial_value=None, updates_value=True):
        self._record_attributes(**{"initial_value":initial_value, "updates_value":updates_value})
        return super().__call__

class ValidationDecorator(MethodDecorator):
    def _record_method(self, method):
        self._methods_dict[method.__name__].addValidation(method)

    def __call__(self): return super().__call__

    