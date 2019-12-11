import unittest
from class_cli.cli import CLI
import class_cli._cli_exception as cli_exception

class Mock(unittest.TestCase):

    def setUp(self):
        cli = CLI()

        class Worker:
            def __init__(self): 
                Worker.reset(self)

            def reset(self): self.__value = 0

            def count(self): return self.__value

            def tick(self, value):
                self.__value += value


        @cli.Program(verbosity=None)
        class Counter(Worker):

            @cli.Validation()
            def factor(self, value:int, allow_negative:[True]=False):
                if value < 0 and not allow_negative: raise Exception()

            @cli.Setting(initial_value=1)
            def factor(self, value:int, allow_negative:[True]=False): return value

            @cli.Validation()
            def tick(self, value:int=1):
                if value < 0:
                    raise Exception()

            @cli.Operation()
            def tick(self, value:int=1):
                super().tick(value * self.CLI.factor)
                return super().count()

            @cli.Operation()
            def reset(self): 
                super().reset()
                return super().count()

            @cli.Validation()
            def count(self):
                if super().count() < 0: raise Exception()

            @cli.Operation()
            def count(self): return super().count()

        self.Counter = Counter

    def test_counter(self):
        counter = self.Counter()
        self.assertEqual(counter.CLI.factor, 1)
        self.assertEqual(counter.count(), 0)
        with self.assertRaises(Exception): counter.factor(-1)
        self.assertEqual(counter.tick(), 1)
        counter.factor(-1, True)
        self.assertEqual(counter.tick(), 0)
        self.assertEqual(counter.CLI.run("tick", '2'), -2)
        self.assertEqual(counter.CLI.execute("tick", '2'), -4)
        self.assertEqual(counter.CLI("tick 2"), -6)
        with self.assertRaises(Exception): counter.count()
        counter.reset()
        self.assertEqual(counter.count(), 0)
        counter.factor(5)
        self.assertEqual(counter.tick(), 5)
        self.assertEqual(counter.CLI.run("tick", '2'), 15)
        self.assertEqual(counter.CLI.execute("tick", '2'), 25)
        self.assertEqual(counter.CLI("tick 2"), 35)
        self.assertEqual(counter.count(), 35)