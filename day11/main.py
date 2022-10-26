from collections import defaultdict
from typing import NamedTuple
from functools import reduce

from intcode import Machine

puzzle_input = [3, 8, 1005, 8, 299, 1106, 0, 11, 0, 0, 0, 104, 1, 104, 0, 3, 8, 102, -1, 8, 10, 101, 1, 10, 10, 4, 10,
                1008, 8, 0, 10, 4, 10, 1002, 8, 1, 29, 1, 1007, 14, 10, 2, 1106, 8, 10, 3, 8, 1002, 8, -1, 10, 1001, 10,
                1, 10, 4, 10, 108, 1, 8, 10, 4, 10, 1002, 8, 1, 58, 3, 8, 1002, 8, -1, 10, 101, 1, 10, 10, 4, 10, 108,
                0, 8, 10, 4, 10, 1002, 8, 1, 80, 3, 8, 1002, 8, -1, 10, 1001, 10, 1, 10, 4, 10, 1008, 8, 0, 10, 4, 10,
                102, 1, 8, 103, 1, 5, 6, 10, 3, 8, 102, -1, 8, 10, 101, 1, 10, 10, 4, 10, 108, 1, 8, 10, 4, 10, 101, 0,
                8, 128, 1, 106, 18, 10, 1, 7, 20, 10, 1006, 0, 72, 1006, 0, 31, 3, 8, 1002, 8, -1, 10, 1001, 10, 1, 10,
                4, 10, 108, 0, 8, 10, 4, 10, 1002, 8, 1, 164, 3, 8, 1002, 8, -1, 10, 1001, 10, 1, 10, 4, 10, 108, 1, 8,
                10, 4, 10, 102, 1, 8, 186, 1, 1007, 8, 10, 1006, 0, 98, 3, 8, 1002, 8, -1, 10, 1001, 10, 1, 10, 4, 10,
                1008, 8, 0, 10, 4, 10, 101, 0, 8, 216, 2, 102, 8, 10, 1, 1008, 18, 10, 1, 1108, 8, 10, 1006, 0, 68, 3,
                8, 1002, 8, -1, 10, 1001, 10, 1, 10, 4, 10, 1008, 8, 1, 10, 4, 10, 1001, 8, 0, 253, 3, 8, 102, -1, 8,
                10, 1001, 10, 1, 10, 4, 10, 108, 1, 8, 10, 4, 10, 1002, 8, 1, 274, 1, 1105, 7, 10, 101, 1, 9, 9, 1007,
                9, 1060, 10, 1005, 10, 15, 99, 109, 621, 104, 0, 104, 1, 21102, 936995738520, 1, 1, 21102, 316, 1, 0,
                1106, 0, 420, 21101, 0, 936995824276, 1, 21102, 1, 327, 0, 1106, 0, 420, 3, 10, 104, 0, 104, 1, 3, 10,
                104, 0, 104, 0, 3, 10, 104, 0, 104, 1, 3, 10, 104, 0, 104, 1, 3, 10, 104, 0, 104, 0, 3, 10, 104, 0, 104,
                1, 21102, 248129784923, 1, 1, 21102, 1, 374, 0, 1105, 1, 420, 21102, 29015149735, 1, 1, 21101, 385, 0,
                0, 1106, 0, 420, 3, 10, 104, 0, 104, 0, 3, 10, 104, 0, 104, 0, 21101, 983925826304, 0, 1, 21101, 0, 408,
                0, 1105, 1, 420, 21102, 825012036364, 1, 1, 21101, 0, 419, 0, 1105, 1, 420, 99, 109, 2, 22101, 0, -1, 1,
                21101, 0, 40, 2, 21101, 0, 451, 3, 21102, 441, 1, 0, 1105, 1, 484, 109, -2, 2105, 1, 0, 0, 1, 0, 0, 1,
                109, 2, 3, 10, 204, -1, 1001, 446, 447, 462, 4, 0, 1001, 446, 1, 446, 108, 4, 446, 10, 1006, 10, 478,
                1101, 0, 0, 446, 109, -2, 2105, 1, 0, 0, 109, 4, 2102, 1, -1, 483, 1207, -3, 0, 10, 1006, 10, 501,
                21102, 0, 1, -3, 21201, -3, 0, 1, 22102, 1, -2, 2, 21102, 1, 1, 3, 21101, 520, 0, 0, 1106, 0, 525, 109,
                -4, 2105, 1, 0, 109, 5, 1207, -3, 1, 10, 1006, 10, 548, 2207, -4, -2, 10, 1006, 10, 548, 21201, -4, 0,
                -4, 1105, 1, 616, 21201, -4, 0, 1, 21201, -3, -1, 2, 21202, -2, 2, 3, 21102, 1, 567, 0, 1105, 1, 525,
                21202, 1, 1, -4, 21102, 1, 1, -1, 2207, -4, -2, 10, 1006, 10, 586, 21102, 0, 1, -1, 22202, -2, -1, -2,
                2107, 0, -3, 10, 1006, 10, 608, 21201, -1, 0, 1, 21102, 1, 608, 0, 106, 0, 483, 21202, -2, -1, -2,
                22201, -4, -2, -4, 109, -5, 2106, 0, 0]


class Point(NamedTuple):
    x: int
    y: int

    def __add__(self, other: "Point"):
        return Point(self.x + other.x, self.y + other.y)


class Direction:
    up = Point(0, 1)
    down = Point(0, -1)
    left = Point(-1, 0)
    right = Point(1, 0)
    directions = [up, right, down, left]
    direction_pointer = 0

    @property
    def direction(self):
        return self.directions[self.direction_pointer]

    def update_direction(self, mode: int):
        if mode == 0:
            self.direction_pointer -= 1
            if self.direction_pointer < 0:
                self.direction_pointer = 3
        else:
            self.direction_pointer += 1
            if self.direction_pointer > 3:
                self.direction_pointer = 0


part1 = Machine(puzzle_input.copy(), interactive_mode=False)
part1.run()

area = defaultdict(int)
location = Point(0, 0)
pointer = Direction()
while not part1.finished:
    part1.provided_input.append(area[location])
    part1.run()
    area[location] = part1.output.pop(0)
    pointer.update_direction(part1.output.pop(0))
    location += pointer.direction

print(f'Part 1: {len(area)}')

part2 = Machine(puzzle_input.copy(), interactive_mode=False)
part2.run()

area = defaultdict(int)
location = Point(0, 0)
area[location] = 1
pointer = Direction()
while not part2.finished:
    part2.provided_input.append(area[location])
    part2.run()
    area[location] = part2.output.pop(0)
    pointer.update_direction(part2.output.pop(0))
    location += pointer.direction

print(f'Part 2:')
min_x, max_x, min_y, max_y = reduce(lambda x, y: [min(x[0], y.x), max(x[1], y.x), min(x[2], y.y), max(x[3], y.y)], area, [0,0,0,0])

for y in range(max_y+1, min_y-1, -1):
    for x in range(min_x-1, max_x+1):
        print('#' if area[Point(x,y)] else ' ', end='')
    print()