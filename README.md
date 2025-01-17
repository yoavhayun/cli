# Class CLI

A Python module for converting a Python class into a CLI program.

Using the module encourages for well documented code while not demanding it.
It allows for separation in implementation between method execution and it's argument validations.

## Capabilities

* Full command and argument auto-completion and suggestions
* Basic type validation for entered arguments while typing
* Full input line validation
* Useful help messages for all methods and arguments 
* Can combine CLI Class Objects together into a single Program
* Logging support
* Command history
* Execution of commands from a text file, line by line

******************
******************

## API

The module exposes an API in the form of decorators.

First import the CLI class

    from class_cli import CLI

create an instance and wrap a class with decorators the it exposes

    cli = CLI()

    @cli.Program()
    class MyClass:

        @cli.Operation()
        def show(self):
            return "I'm a CLI Program!"

Run the main method of the CLI

    if __name__ == "__main__":
        MyClass().CLI.main()

When running the script without arguments, It will open the CLI for user input:

> **MyClass>** show\
> I'm a CLI Program!
>
> **MyClass>** |

******************

## These are the available decorators

### **@Program**

    Program(name=None, version=None, description=None, log=None, style=None, verbosity=logging.INFO)

        a class decorator that defines the CLI program.
        Instantiation of the wrapped user class can be used as normal python code, accessing all it's attributes.
        It also exposes the CLI interface with an added attribute named 'CLI'

        * Only a single Program can be declared for every CLI instance

        @name           The name of the CLI program.                                                (Default is the class name)
        @version        The version of the CLI program.                                             (Default is a CLI without versioning)
        @description    The description of the CLI program.                                         (Default is the class documentation)
        @log            A path to a log file.                                                       (Default is no log file)
        @style          A dictionary that overrides the styling of the CLI for the given keys       (Keys: CLI.STYLE)
        @verbosity      Determines the verbosity level on the logger. Use None to silence STDOUT    (Keys: logging module)

### **@Operation**

    Operation()

        a method decorator that defines the execution code of an operation in the CLI

### **@Setting**

    Setting(initial_value, updates_value=True)
   
        a method decorator that creates a setting value for the CLI with name equals to the method name.
        It defines the execution code for setting the value into the created setting.

        @initial_value      An initial value that the setting will hold after class initialization
        @updates_value      Whether or not calling this method automatically updates the inner setting value

### **@Delegate**

    Delegate(reuse=True)
   
        a method decorator that delegates control to another CLI Object instance by exposing an access point. 
        The wrapped method does not accept any arguments and returns the CLI Object instance to delegate control to.
        * This allows for easy integration and combination of CLI Objects into a single CLI Program

        @reuse      Whether or not the returned CLI Object should be reused for later calls

### **@Validation**

    Validation()

        A method decorator that defines a validation to be performed on an execution (Operation / Setting / Delegation)
        Holds the same signature as the execution it is validating and raises an exception for invalid arguments.
        * A single execution can have multiple Validations

******************

## API Example

In this example, we are wrapping a class, that holds a Setting named **value**, and exposes a method called **show** that prints it to the screen.

    from class_cli import CLI

    cli = CLI()
    @cli.Program()
    class MyClass:
    
        @cli.Operation()
        def show(self): 
            if self.CLI.name is None:
                return "I'm a CLI Program!"
            else:
                return "My name is {}!".format(self.CLI.name)
            
        @cli.Setting()
        def name(self, str):
            return str
    
    if __name__ == "__main__":
        MyClass().CLI.main()

 In the main method we called **MyClass().CLI.main()** which checks for sys.argv for input and executes the commands using the instance.

> $> **python3 MyClass.py show**\
> I'm a CLI Program!

 If we execute the script without arguments, it will open the CLI for user input:

> $> **python3 MyClass.py**\
> **MyClass**\
> &emsp;&emsp;&emsp;&emsp;To exit, enter one of the following: **'q'** **'quit'** **'exit'**\
> &emsp;&emsp;&emsp;&emsp;To read commands from a file, enter one of the following: **'.r'** **'.read'**\
> &emsp;&emsp;&emsp;&emsp;To access the program settings, enter one of the following: **'.set'** **'.setting'**\
>
> &emsp;&emsp;&emsp;&emsp;**At any time, add '-h' flag to the command for help.**\
> \
> **MyClass>** show\
> I'm a CLI Program!
>
> **MyClass>** .setting name John\
> =John
>
> **MyClass>** show\
> My name is John!
>
> **MyClass>** |

 You can also open the CLI directly by calling **run(\*args)** instead of **main**

     if __name__ == "__main__":
         MyClass().CLI.run()

Other commands:

**run_line(line)** which executes a single line of String

**execute(\*args)** which executes the same as **run**, but does not print out log outputs.

## Instance API

You can call the methods of a CLI Object directly without opening a CLI session:

    >>> instance = MyClass()

    >>> instance.show()
    'I'm a CLI Program!'

    >>> instance.name("Bob")
    'Bob'

    >> instance.show()
    'My name is Bob!'

******************
******************

## Delegation

The library treats Class CLIs as building blocks that can integrate into a larger program.
This encourages for code separation between the components of a program.

This is done by wrapping a class method with the @Delegate decorator.

    cli = CLI()
    @cli.Program()
    class Main:
        @cli.Operation()
        def show(self): return "Main CLI"

        @cli.Delegate()
        def inner(self):
            inner_cli = CLI()
            @cli.Program()
            class Inner:
                @cli.Operation()
                def show(self): return "Inner CLI"
            return Inner()

    if __name__ == "__main__":
        Main().CLI.main()

You can access the inner CLI by calling the inner method:

    >>> Main()
    <__main__.Main object at 0x03DBF5D0>
    
    >>> Main().inner()
    <__main__.Main.inner.<locals>.Inner object at 0x03B6D750>

From the CLI, you can pass commands to it by prefixing with the **inner** method, or open it directly for commands

> **Main>** show\
> Main CLI
>
> **Main>** inner show\
> Inner CLI
>
> **Main>** inner
>
> **Main\\Inner>** show\
> Inner CLI
>
> **Main\\Inner>** q
>
> **Main>** |

******************
******************

## Logging

 To log messages, the cli holds a Logger instance. to access it, use the **CLI.log** keyword

    def method(self):
        self.CLI.log.info("This is an information Line")
        self.CLI.log.warning("This is a Warning")
        self.CLI.log.error("This is an Error")
        self.CLI.log.debug("This line is shown only when Program decorator is called with 'debug=True'"")

> **MyClass>** method\
> This is an information Line\
> [WARNING] This is a Warning\
> `2019-10-10 17:51:21,807`\
> `[ERROR] This is an Error`\
> 2019-10-10 17:51:21,808\
> [DEBUG][test:12] This line is shown only when Program decorator is called with 'debug=True'
>
> **MyClass>** |

You can see documentation for the Logger object [here](https://docs.python.org/3/library/logging.html)

******************
******************

## Help Messages

The CLI makes use of user code documentation in order to provide help messages to the user providing the **--help**/**-h** flag in the input.
Using the **--help** flag will display a message relevant to the user input.
Using it alone will display a usage message for the entire program while adding it after an Operation or Setting name will display usage information for that Operation or Setting.

    @cli.Operation()
    def method(self):
        """
        A description of the method
        """
        pass

> **CLI>** method -h\
> usage: CLI method [-h]
>
> =========================\
> A description of the method
>
> =========================\
> optional arguments:\
> -h, --help  show this help message and exit\
>
> **CLI>**|

Any Validations for the method will be added to the description

    @cli.Validation()
    def method(self, arg):
        """
        cannot perform operation when disabled
        """
        if self.disabled:
            raise Exception("Cannot perform operations when disabled")

> **CLI>** method -h\
> usage: CLI method [-h]
>
> =========================\
> A description of the method\
> \* cannot perform operation when disabled\
> \=========================
>
> optional arguments:\
> -h, --help  show this help message and exit\
>
> **CLI>**|

If there are arguments for the method, you can add descriptions for them inside the method documentation with a **@** prefix as demonstrated below.

    @cli.Operation()
    def method(self, arg):
        """
        A description of the method

        Accepts:
            @arg    arg description
            @arg    another line of the description
        """
        pass

> **CLI>** method -h\
> usage: CLI method [-h] arg
>
> =========================\
> A description of the method
>
> Accepts:\
> &emsp;&emsp;@arg    arg description\
> &emsp;&emsp;@arg    another line of the description
>
> &emsp;&emsp;* cannot perform operation when disabled
>
> =========================\
> positional arguments:\
> &emsp;arg&emsp;&emsp;&emsp;&emsp;=========================\
> &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp;arg description\
> &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp;another line of the description\
> &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp;Type: \<class 'str'>\
> &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp;=========================\
> optional arguments:\
> -h, --help  show this help message and exit
>
> **CLI>**|

******************
******************

## Type Annotations

Pythons type annotations are used by the CLI in order to use type validation and conversion.

### Type Conversion

Since the user input is a String, by default the arguments passed to a method are String

**Default Behavior**:

    @cli.Operation()
    def method(self, arg):
        print(type(arg), ';', arg)

> **CLI>** method value\
> \<class 'str'> ; value
>
> **CLI>**|

**Basic Annotation**:
Using annotations, we can provide a type to tell the CLI what is expected, and use it to convert the String into its proper type.
The CLI accepts annotations which are a Python Callable that receive a String and returns it converted to the desired type.

    @cli.Operation()
    def method(self, arg:int):
        print(type(arg), ';', arg)

> **CLI>** method 17\
> \<class 'int'> ; 17
>
> **CLI>**|

**Iterable Annotation**:
You can also use an Iterable as an annotation to specify a set of options.

    @cli.Operation()
    def method(self, value:[1, "value", (0,0)]):
        print(type(value), ';', value)

> **CLI>** method 1\
> \<class 'int'> ; 1
>
> **CLI>** method value\
> \<class 'str'> ; value
>
> **CLI>** method '(0, 0)'\
> \<class 'tuple'> ; (0, 0)
>
> **CLI>**|

* *Since the string representation of the items in the List are used to select the value from it, The String representations of the Items need to be unique.*

### Type Validation

During typing of input, The CLI will tip the user for the expected inputs, as well as block the user from entering invalid types into a command.

    @cli.Operation()
    def method(self, arg1, arg2:int=0, arg3:[1, -1]=1, **extras):
        pass
> **CLI>** method value number|\
> \
> \
> `invalid literal for int() with base 10: 'number'`\
> arg1 **arg2[=0]** arg3[=1] {*\*extras}  :  **{\<class 'int'>}**
\
> **CLI>** method value 0 2|\
> \
> \
> `'2' is not a valid option`\
> arg1 arg2[=0] **arg3[=1]** {*\*extras}  :  **{\<value from: 1, -1>}**
\
> **CLI>** method value 0 -1 arg|\
> \
> \
> `'arg' must be in the format [key]=[value]`\
> arg1 arg2[=0] arg3[=1] **{\*\*extras}**  :  **{\<class 'dict'> [items=0]}**
\
> **CLI>** method value 0 -1 arg=val|\
> \
> \
> \
> arg1 arg2[=0] arg3[=1] **{\*\*extras}**  :  **{\<class 'dict'> [items=1]}**

******************

## Auto Completion

The CLI can auto-complete command names, file paths and argument values.

    @cli.Operation()
    def method(self, arg1, arg2:int=0, arg3:[1, -1]=None, *extras):
        pass
    
    @cli.Setting()
    def name(self, arg1):
        return arg1

Pressing 'TAB' will open up all available suggestions
> **CLI>** |\
> &emsp;&emsp;&ensp;| method |\
> &emsp;&emsp;&ensp;| .setting&nbsp; |\
> &emsp;&emsp;&ensp;| &ensp;.read&ensp;&nbsp; |  
\
> **CLI>** .setting |\
> &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;| name |

When browsing suggestions, you can see the expected arguments at the bottom:

> **CLI>** method|\
> &emsp;&emsp;&ensp;**| method |**\
> &emsp;&emsp;&ensp;| &ensp;.setting&nbsp; |\
> &emsp;&emsp;&ensp;| &emsp;.read&ensp;&nbsp; |\
> \
> **arg1 arg2[=0] arg3[=None] {\*extras}**

When the expected argument is an Iterable, the CLI will suggest all the Iterable items

> **CLI>** method value 0 |\
> &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp;| &nbsp;1 |\
> &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp;| -1 |\
> \
> arg1 arg2[=0] **arg3[=None]** {*extras}  :  **{1, -1}**

If you are providing your own Callable for annotation, you can make use of the auto complete mechanism by implementing **\__complete__(self, keyword)**

******************

## Implementing a Custom Annotation

You can use any callable(str) as a type annotation for the CLI.

### Representation

The CLI displays the callable to the user as its String representation. To set the description, override the **\__str__(self)** method

    def __str__(self):
        return "A Custom Type"

### Callable

The annotation must be a callable that accepts a string and returns a list of strings.
The callable returns all the suggestions relevant to the given keyword

    def __call__(self, key):
        if key in self.options_dict:
            return self.options_dict[key]

### Validation

If the given string is not a valid option, you can throw an exception inside the **\__call__** method

    def __call__(self, str):
        if key in self.options_dict:
            return self.options_dict[key]
        throw Exception("'{}'' is not a valid option".format(str))

This will block the user from entering a non existing key

### Autocomplete Suggestion

To make use of the auto complete mechanism, implement the **\__complete__(self, keyword)** method

    def __complete__(self, str):
        return [s for s in self.suggestions if s.startswith(str)]

# Dynamic Iterable Annotation

We've seen that you can use an iterable as an annotation for a variable

    @cli.Program()
    class MyClass:
        @cli.Operation()
        def oper(self, value:[True, False]):
            print("You have selected", value)

In this example, we are using a list to specify that only boolean values are accepted.

What if we want to use a list that is dynamic and can change throughout the run of the program.
To do that, we need to define the list outside the class scope in order to access it in method signature

    values = [1, 2, 3]

    @cli.Program()
    class MyClass:
        @cli.Operation()
        def oper(self, value:values):
            print("You have selected", value)

        @cli.Operation()
        def add_value(self, value:int):
            values.append(value)

The **oper** operation will now accept values in [1, 2, 3].
We can also use the **add_value** operation in order to add more options to be selected

For better code structure, we can use the **with** statement with the CLI object

    with CLI() as cli:
        values = [1, 2, 3]

        @cli.Program()
        class MyClass:
            @cli.Operation()
            def oper(self, value:values):
                print("You have selected", value)

            @cli.Operation()
            def add_value(self, value:int):
                values.append(value)

This will make it clear that the **values** variable is associated with the CLI.
