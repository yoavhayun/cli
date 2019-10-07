# CLI
A Python module for converting a python class into a CLI program

prompt_toolkit is a dependency of this module

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

                from class_cli.cli import CLI

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
    
    When calling the script with arguments, it will execute them and exit. If not arguments are passed,
    It will start a cli program.

    This provides the following cli behavior:

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
