import sys
from collections import defaultdict
from typing import List, Tuple, NamedTuple

from loguru import logger
#
logger.remove()
logger.add(sys.stderr, level="INFO")


class Machine:
    def __init__(self,
                 code: List,
                 provided_input: List = None,
                 print_output: bool = False,
                 interactive_mode: bool = True):
        self.instruction_pointer = 0
        self.code = defaultdict(int)
        self.code.update({k: v for k, v in enumerate(code)})
        if not provided_input:
            self.provided_input = []
        else:
            self.provided_input = provided_input
        self.running = True
        self.print_output = print_output
        self.output = []
        self.interactive_mode = interactive_mode
        self.relative_base = 0
        self.finished = False
        self.ops = {
            1: self._add,
            2: self._mul,
            3: self._inp,
            4: self._out,
            5: self._jit,
            6: self._jif,
            7: self._lt,
            8: self._eq,
            9: self._rel,
            99: self._quit
        }

    def run(self):
        self.running = True
        while self.running:
            self.step()

    def step(self):
        logger.debug(f"p={self.instruction_pointer} r={self.relative_base}: {self.code}")
        self.ops[self.code[self.instruction_pointer] % 100]()

    def get_value(self, address: int, mode: int) -> int:
        if mode == 0:
            return self.code[self.code[address]]
        elif mode == 1:
            return self.code[address]
        elif mode == 2:
            return self.code[self.code[address]+self.relative_base]

    def set_value(self, address: int, mode: int, value: int):
        if mode == 2:
            self.code[address+self.relative_base] = value
        else:
            self.code[address] = value

    @property
    def current_instruction(self):
        return self.code[self.instruction_pointer]

    def get_code_slice(self, length: int) -> List[int]:
        return [self.code[x] for x in range(self.instruction_pointer, self.instruction_pointer+length)]

    def _get_two(self) -> Tuple[int, int]:
        op = self.code[self.instruction_pointer]
        a = self.get_value(self.instruction_pointer + 1, op // 100 % 10)
        b = self.get_value(self.instruction_pointer + 2, op // 1000 % 10)
        return a, b

    def _add(self):
        # intcode 1
        a, b = self._get_two()
        logger.debug(f'{self.get_code_slice(4)} -> {a=} {b=} out={a+b}')
        self.set_value(self.code[self.instruction_pointer + 3], self.code[self.instruction_pointer] // 10000 % 10, a + b)
        self.instruction_pointer += 4

    def _mul(self):
        # intcode 2
        a, b = self._get_two()
        logger.debug(f'{self.get_code_slice(4)} -> {a=} {b=} out={a * b}')
        self.set_value(self.code[self.instruction_pointer + 3], self.code[self.instruction_pointer] // 10000 % 10, a * b)
        self.instruction_pointer += 4

    def _inp(self):
        # intcode 3
        if self.provided_input:
            in_data = self.provided_input.pop(0)
        else:
            if self.interactive_mode:
                in_data = int(input('input: '))
            else:
                self.running = False
                return
        logger.debug(f'{self.get_code_slice(2)} -> {in_data=}')
        self.set_value(self.code[self.instruction_pointer+1], self.code[self.instruction_pointer] // 100 % 10, in_data)
        self.instruction_pointer += 2

    def _out(self):
        # intcode 4
        a = self.get_value(self.instruction_pointer + 1, self.code[self.instruction_pointer] // 100 % 10)
        logger.opt(colors=True).debug(f'<red>{self.get_code_slice(2)} -> {a=}</red>')
        self.output.append(a)
        if self.print_output:
            print(a)
        self.instruction_pointer += 2

    def _jit(self):
        # intcode 5
        a, b = self._get_two()
        logger.debug(f'{self.get_code_slice(4)} -> {a=} {b=} out={a != 0}')
        self.instruction_pointer = b if a != 0 else self.instruction_pointer + 3

    def _jif(self):
        # intcode 6
        a, b = self._get_two()
        logger.debug(f'{self.get_code_slice(4)} -> {a=} {b=} out={a == 0}')
        self.instruction_pointer = b if a == 0 else self.instruction_pointer + 3

    def _lt(self):
        # intcode 7
        a, b = self._get_two()
        logger.debug(f'{self.get_code_slice(4)} -> {a=} {b=} out={a < b}')
        self.set_value(self.code[self.instruction_pointer+3], self.code[self.instruction_pointer] // 10000 % 10, 1 if a < b else 0)
        self.instruction_pointer += 4

    def _eq(self):
        # intcode 8
        a, b = self._get_two()
        logger.debug(f'{self.get_code_slice(4)} -> {a=} {b=} out={a == b}')
        self.set_value(self.code[self.instruction_pointer+3], self.code[self.instruction_pointer] // 10000 % 10, 1 if a == b else 0)
        self.instruction_pointer += 4

    def _rel(self):
        # intcode 9
        a = self.get_value(self.instruction_pointer + 1, self.code[self.instruction_pointer] // 100 % 10)
        logger.debug(f'{self.get_code_slice(2)} -> {a=} before={self.relative_base} after={self.relative_base + a}')
        self.relative_base += a
        self.instruction_pointer += 2

    def _quit(self):
        # intcode 99
        logger.debug(f'{self.get_code_slice(1)} -> QUIT')
        self.running = False
        self.finished = True


class Point(NamedTuple):
    x: int
    y: int

    def __add__(self, other: "Point"):
        return Point(self.x + other.x, self.y + other.y)

    def day_17_score(self) -> int:
        return self.x * self.y