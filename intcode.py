import sys
from typing import List, Tuple

from loguru import logger
#
# logger.remove()
# logger.add(sys.stderr, level="INFO")


class Machine:
    def __init__(self,
                 code: List,
                 provided_input: List = None,
                 print_output: bool = False,
                 interactive_mode: bool = True):
        self.instruction_pointer = 0
        self.code = code
        self.provided_input = provided_input
        self.running = True
        self.print_output = print_output
        self.output = []
        self.interactive_mode = interactive_mode
        self.relative_base = 0
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
        self.ops[self.code[self.instruction_pointer] % 100]()

    def get_value(self, address: int, immediate: bool = False) -> int:
        try:
            if immediate:
                return self.code[address+self.relative_base]
            else:
                return self.code[self.code[address]+self.relative_base]
        except IndexError:
            if immediate:
                self.code.extend([0] * (address - len(self.code) + 10))
            else:
                self.code.extend([0] * (self.code[address] - len(self.code) + 10))
            return self.get_value(address, immediate)

    def set_value(self, address: int, value: int):
        try:
            self.code[address + self.relative_base] = value
        except IndexError:
            length_to_extend = address - len(self.code) + self.relative_base
            self.code.extend([None] * length_to_extend)
            self.code[address + self.relative_base] = value

    @property
    def current_instruction(self):
        return self.code[self.instruction_pointer]

    def _get_two(self) -> Tuple[int, int]:
        op = self.code[self.instruction_pointer]
        a = self.get_value(self.instruction_pointer + 1, bool(op // 100 % 10))
        b = self.get_value(self.instruction_pointer + 2, bool(op // 1000 % 10))
        return a, b

    def _add(self):
        # intcode 1
        a, b = self._get_two()
        logger.debug(f'{self.code[self.instruction_pointer:self.instruction_pointer + 4]} -> {a=} {b=} out={a+b}')
        self.set_value(self.code[self.instruction_pointer + 3], a + b)
        self.instruction_pointer += 4

    def _mul(self):
        # intcode 2
        a, b = self._get_two()
        logger.debug(f'{self.code[self.instruction_pointer:self.instruction_pointer + 4]} -> {a=} {b=} out={a * b}')
        self.set_value(self.code[self.instruction_pointer + 3], a * b)
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
        logger.debug(f'{self.code[self.instruction_pointer:self.instruction_pointer + 2]} -> {in_data=}')
        self.set_value(self.code[self.instruction_pointer+1], in_data)
        self.instruction_pointer += 2

    def _out(self):
        # intcode 4
        op = self.code[self.instruction_pointer]
        a = self.get_value(self.instruction_pointer + 1, op - (op % 100)-100 == 0)
        logger.opt(colors=True).debug(f'<red>{self.code[self.instruction_pointer:self.instruction_pointer + 2]} -> {a=}</red>')
        self.output.append(a)
        if self.print_output:
            print(a)
        self.instruction_pointer += 2

    def _jit(self):
        # intcode 5
        a, b = self._get_two()
        logger.debug(f'{self.code[self.instruction_pointer:self.instruction_pointer + 3]} -> {a=} {b=} out={a != 0}')
        self.instruction_pointer = b if a != 0 else self.instruction_pointer + 3

    def _jif(self):
        # intcode 6
        a, b = self._get_two()
        logger.debug(f'{self.code[self.instruction_pointer:self.instruction_pointer + 3]} -> {a=} {b=} out={a == 0}')
        self.instruction_pointer = b if a == 0 else self.instruction_pointer + 3

    def _lt(self):
        # intcode 7
        a, b = self._get_two()
        logger.debug(f'{self.code[self.instruction_pointer:self.instruction_pointer + 4]} -> {a=} {b=} out={a < b}')
        self.set_value(self.code[self.instruction_pointer+3], 1 if a < b else 0)
        self.instruction_pointer += 4

    def _eq(self):
        # intcode 8
        a, b = self._get_two()
        logger.debug(f'{self.code[self.instruction_pointer:self.instruction_pointer + 4]} -> {a=} {b=} out={a == b}')
        self.set_value(self.code[self.instruction_pointer+3], 1 if a == b else 0)
        self.instruction_pointer += 4

    def _rel(self):
        logger.debug(f'{self.code[self.instruction_pointer:self.instruction_pointer + 2]} -> before'
                     f'={self.relative_base} after={self.relative_base + self.code[self.instruction_pointer + 1]}')
        self.relative_base += self.code[self.instruction_pointer + 1]
        self.instruction_pointer += 2

    def _quit(self):
        # intcode 99
        logger.debug(f'{self.code[self.instruction_pointer:self.instruction_pointer + 1]} -> QUIT')
        self.running = False

