import numpy as np
from collections import Counter


class tapa_field:

    def __init__(self,
                 field: list[list[int]],
                 solution: list[list[bool]] = None
                 ):
        self.field = field
        self.n_rows = len(self.field)
        self.n_cols = len(self.field[0])
        self.solution = solution

    def __str__(self):
        field_str = "+"+"--+"*(self.n_cols)+"\n"

        for i, row in enumerate(self.field):
            line1 = "|"
            line2 = "|"
            for j, cell in enumerate(row):
                num_count = len(cell)
                if num_count == 0:
                    if self.solution is not None and self.solution[i, j]:
                        line1 += "##"
                        line2 += "##"
                    else:
                        line1 += "  "
                        line2 += "  "
                elif num_count == 1:
                    line1 += str(cell[0])+" "
                    line2 += "  "
                elif num_count == 2:
                    line1 += str(cell[0])+" "
                    line2 += " "+str(cell[1])
                elif num_count == 3:
                    line1 += str(cell[0])+str(cell[1])
                    line2 += str(cell[2])+" "
                elif num_count == 4:
                    line1 += str(cell[0])+str(cell[1])
                    line2 += str(cell[2])+str(cell[3])
                else:
                    raise NotImplementedError("No cell with +4 numbers")
                line1 += "|"
                line2 += "|"
            field_str += line1 + "\n"
            field_str += line2 + "\n"
            field_str += "+"+"--+"*(self.n_cols)+"\n"

        return field_str

    def check_solution(self):
        if (
                self.solution is None or
                self.check_number_cell_filled() or
                self.check_2x2_block() or
                self.check_uncontiguous() or
                self.check_number_cell_unfulfilled()
                ):
            return False
        else:
            return True

    def check_solution_and_print_reason(self):
        all_pass = True
        if self.solution is None:
            print("Solution is empty!")
            return False
        if self.check_number_cell_filled():
            print("Number cell is filled")
            all_pass = False
        if self.check_2x2_block():
            print("Solution has 2x2 block")
            all_pass = False
        if self.check_uncontiguous():
            print("Sea is not contiguous")
            all_pass = False
        if self.check_number_cell_unfulfilled():
            print("Number cell has wrong neighborhood")
            all_pass = False
        return all_pass

    def check_number_cell_filled(self):
        for i, row in enumerate(self.field):
            for j, cell in enumerate(row):
                if len(cell) > 0 and self.solution[i, j]:
                    return True
        return False

    def check_2x2_block(self):
        check_field = self.solution.copy()[:-1, :-1]
        check_field &= self.solution[1:, :-1]
        check_field &= self.solution[:-1, 1:]
        check_field &= self.solution[1:, 1:]
        return check_field.any()

    def check_uncontiguous(self):
        # flood-fill with a dfs
        padded_field = np.zeros((self.n_rows+2, self.n_cols+2), dtype=np.bool)
        padded_field[1:-1, 1:-1] = self.solution
        check_field = np.zeros(padded_field.shape, dtype=np.int8)

        nodes = list(zip(*np.where(padded_field)))
        search_stack = [nodes[0]]
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        while search_stack:
            cur_node = search_stack[-1]

            check_field[cur_node] = -1
            has_child = False
            i = 0
            while not has_child and i < len(directions):
                new_node = (cur_node[0] + directions[i][0],
                            cur_node[1] + directions[i][1])
                if check_field[new_node] == 0 and new_node in nodes:
                    search_stack.append(new_node)
                    has_child = True
                i += 1
            if not has_child:
                check_field[cur_node] = 1
                search_stack.pop()

        if np.sum(padded_field) != np.sum(check_field):
            return True
        return False

    def check_number_cell_unfulfilled(self):
        padded_field = np.zeros((self.n_rows+2, self.n_cols+2), dtype=np.bool)
        padded_field[1:-1, 1:-1] = self.solution

        for i, row in enumerate(self.field):
            for j, cell in enumerate(row):
                if len(cell) > 0:  # check cells with numbers
                    # unroll neighborhood
                    directions = [(0, 0), (0, 1), (0, 2), (1, 2),
                                  (2, 2), (2, 1), (2, 0), (1, 0)]
                    unrolled = np.empty((8))
                    for k, direction in enumerate(directions):
                        x, y = direction
                        unrolled[k] = padded_field[i+x, j+y]

                    # counts contiguous section sizes
                    counts = []
                    count = 0
                    k = 0
                    while k < 8:
                        if unrolled[k] == 0 and count > 0:
                            counts.append(count)
                            count = 0
                        elif unrolled[k] == 1:
                            count += 1
                        k += 1
                    if count > 0:
                        if unrolled[0] and count != 8:  # wraps addition
                            counts[0] += count
                        else:
                            counts.append(count)

                    # Compare writen value with counted
                    if Counter(cell) != Counter(counts):
                        return True

        return False


def parse_field(field_str: str):
    field = []
    for line in field_str.split("\n")[:-1]:
        row = []
        for nums in line.split(","):
            row.append([int(num) for num in nums])
        field.append(row)

    return field


def parse_solution(solution_str: str):
    lines = solution_str.split("\n")[:-1]
    n_rows = len(lines)
    n_cols = len(lines[0])
    solution = np.empty((n_rows, n_cols), dtype=np.bool)
    for i, row in enumerate(lines):
        for j, char in enumerate(row):
            solution[i, j] = (char == '1')
    return solution


if __name__ == "__main__":
    field_file = "trivial2x3.txt"
    solve_file = "trivial2x3_sol.txt"
    wrong_file = "trivial2x3_wrong.txt"

    with open(field_file, "rt") as fp:
        raw_field = parse_field(fp.read())
    field = tapa_field(raw_field)
    with open(solve_file, "rt") as fp:
        solution = tapa_field(raw_field, parse_solution(fp.read()))
    with open(wrong_file, "rt") as fp:
        wrong = tapa_field(raw_field, parse_solution(fp.read()))

    print(field)
    print(solution)
    print(wrong)

    print(field.check_solution_and_print_reason())
    print()
    print(solution.check_solution_and_print_reason())
    print()
    print(wrong.check_solution_and_print_reason())
