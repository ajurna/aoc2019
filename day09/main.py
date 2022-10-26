from intcode import Machine

part1 = Machine([109, 1, 204, -1, 1001, 100, 1, 100, 1008, 100, 16, 101, 1006, 101, 0, 99], print_output=True)
part1.run()
print(part1.output)