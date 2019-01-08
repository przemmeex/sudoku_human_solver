import re
import copy
from time import time

ALL_STEPS_PRINT = False


class SdkGame(object):
    def __init__(self, numbers, coordinates):
        self.numbers = numbers
        self.coordinates = coordinates
        self.possible_numbers = {}
        self.found_dict = {}
        self.board = [[[[None, None, None] for i in range(3)] for i in range(3)]
                      for i in range(3)]

    def create_board(self):
        """
        build data structure for game status recording - nested list and dictionary(ches board like coordinates for key)
        :return:
        """

        for i, j in zip(self.numbers, self.coordinates):
            split_coordinates = re.search("([a-zA-Z]+)(\d+)", j)
            x_coordinate = ord(split_coordinates.group(1)) - 96
            y_coordinate = int(split_coordinates.group(2))
            self.possible_numbers[j] = {i}
            self.board[(y_coordinate - 1) // 3][(x_coordinate - 1) // 3][
                y_coordinate - 1 - (y_coordinate - 1) // 3 * 3][
                x_coordinate - 1 - (x_coordinate - 1) // 3 * 3] = i
            self.found_dict[j] = i
            # print(board)
            # print(i, j)
        for letter in "abcdefghi":
            for nbr in range(1, 10):
                if not self.possible_numbers.get("{}{}".format(letter, nbr),
                                                 False):
                    self.possible_numbers["{}{}".format(letter, nbr)] = {1, 2,
                                                                         3, 4,
                                                                         5, 6,
                                                                         7, 8,
                                                                         9}


    def check_squares(self):
        """
        validate all possible numbers left in one square
        :return:
        """
        for square_row in range(3):
            for square in range(3):
                numbers_in_square = []
                for row in range(3):
                    for column in range(3):
                        if self.board[square_row][square][row][column]:
                            numbers_in_square.append(
                                self.board[square_row][square][row][column])
                for row in range(3):
                    for column in range(3):
                        dict_addr = "{}{}".format(chr(square * 3 + column + 97),
                                                  str(square_row * 3 + row + 1))
                        self.possible_numbers[dict_addr] -= set(
                            numbers_in_square)

    def check_column_and_row(self, address):
        to_remove = []
        for row in {"a", "b", "c", "d", "e", "f", "g", "h", "i"} - set(
                address[0]):
            if self.found_dict.get(row + address[1], None):
                to_remove.append(self.found_dict[row + address[1]])
        for column in {str(i) for i in range(1, 10)} - set(address[1]):
            if self.found_dict.get(address[0] + column, None):
                to_remove.append(self.found_dict[address[0] + column])

        self.possible_numbers[address] -= set(to_remove)

    def advance_col_check(self, address):
        """need to be tested

        :param address:
        :return:
        """

        sq_1, sq_2 = {1, 2, 3} - {(int(address[1]) - 1) // 3 + 1}
        sq_1 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]][sq_1 - 1]
        sq_2 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]][sq_2 - 1]
        to_remove = []
        for number in self.possible_numbers[address]:
            for square in [sq_1, sq_2]:
                empty, used = self.empty_in_square(address[0] + str(square[0]),
                                                   full=True)
                if number not in used:
                    can_remove = True
                    for i in empty:
                        if number in self.possible_numbers[i] and i[0] != \
                                address[0]:
                            can_remove = False
                    if can_remove:
                        to_remove.append(number)

        self.possible_numbers[address] -= set(to_remove)
        if to_remove:
            return True
        return False

    def advance_row_check(self, address):
        """need to be checked

        :param address:
        :return:
        """

        sq_1, sq_2 = {1, 2, 3} - {(ord(address[0]) - 97) // 3 + 1}
        sq_1 = [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]][sq_1 - 1]
        sq_2 = [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]][sq_2 - 1]
        to_remove = []
        # print(sq_1,sq_2)

        for number in self.possible_numbers[address]:
            for square in [sq_1, sq_2]:
                empty, used = self.empty_in_square(square[0] + address[1],
                                                   full=True)
                if number not in used:
                    can_remove = True
                    for i in empty:
                        if number in self.possible_numbers[i] and i[1] != \
                                address[1]:
                            can_remove = False
                    if can_remove:
                        to_remove.append(number)

        self.possible_numbers[address] -= set(to_remove)
        if to_remove:
            return True
        return False

    def advence_square_check2(self, address):
        """
        check if on 2(or 3 or 4) empty files only 2 (or 3 or 4) numbers are
        possible and those numbers are the same
        if so remove them from any other empty files possible numbers

        :param address:
        :return:
        """

        emp, pos = self.empty_in_square(address, full=True)

        for i in range(2, 5):

            for empty_field in emp:
                cou = 1
                same = [empty_field]
                for j in emp:
                    if self.possible_numbers[empty_field] == \
                            self.possible_numbers[j] and empty_field != j:
                        cou += 1
                        same.append(j)
                if cou == len(self.possible_numbers[empty_field]):
                    for empty_field in emp:
                        if empty_field not in same:
                            self.possible_numbers[empty_field] -= \
                            self.possible_numbers[same[0]]

    def advence_square_check(self, address):
        """
        if some number is possible only on one field in the square, remove other
        possible numbers from that field

        :param address:
        :return:
        """

        emp, pos = self.empty_in_square(address, full=True)
        for nbr in {1, 2, 3, 4, 5, 6, 7, 8, 9} - set(pos):
            possible_in = 0
            for key in emp:
                for possible in self.possible_numbers[key]:
                    if possible == nbr:
                        possible_in += 1
                        pos_nbr = key
            if possible_in == 1:
                self.possible_numbers[pos_nbr] = {nbr}

    def empty_in_square(self, address, full=False):
        """
        return all ampty fields in square to whom address belongs
        :param address:
        :return:
        """
        columns = [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]]
        rows = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        x_ = (ord(address[0]) - 97) // 3
        y_ = (int(address[1]) - 1) // 3

        # print columns[x_], rows[y_]
        nbr_in_sq = []
        to_return = []
        for element in columns[x_]:
            for part in rows[y_]:
                if not self.found_dict.get("{}{}".format(element, part), None):
                    to_return.append("{}{}".format(element, part))
                else:
                    nbr_in_sq.append(
                        self.found_dict["{}{}".format(element, part)])
        if not full:
            return to_return
        return to_return, sorted(nbr_in_sq)

    def number_any_procedure(self, address, square_empty, nbr):
        test_for_nbr = square_empty[:]
        to_remove = []
        columns_to_do = set([["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]][
                                (ord(address[0]) - 97) // 3]) - set(
            [address[0]])
        rows_to_to = set([[1, 2, 3], [4, 5, 6], [7, 8, 9]][
                             (int(address[1]) - 1) // 3]) - set(
            [int(address[1])])

        for i in range(1, 10):
            for j in columns_to_do:
                if self.found_dict.get("{}{}".format(j, i), None):
                    if int(self.found_dict["{}{}".format(j, i)]) == int(nbr):
                        for k in test_for_nbr:
                            if k[0] == j:
                                to_remove.append(k)

        test_for_nbr = set(test_for_nbr) - set(to_remove)
        to_remove = []

        for i in ["a", "b", "c", "d", "e", "f", "g", "h", "i"]:
            for j in rows_to_to:
                if self.found_dict.get("{}{}".format(i, j), None):
                    if int(self.found_dict["{}{}".format(i, j)]) == int(nbr):
                        for k in test_for_nbr:
                            if k[1] == str(j):
                                to_remove.append(k)
        test_for_nbr = set(test_for_nbr) - set(to_remove)
        if len(test_for_nbr) == 1 and test_for_nbr.pop() == address:
            return True
        return False

    def number_anywhere_check(self, address):
        """

        :param address:
        :return:
        """
        places_to_take = self.empty_in_square(address)

        for nbr in self.possible_numbers[address]:
            pass
            if self.number_any_procedure(address, places_to_take, nbr):
                self.possible_numbers[address] = {int(nbr)}
                break


    def write_possible(self):
        """
        if only one number is possible on field write it to data structures (nested list and dict)
        :return:
        """
        for key in self.possible_numbers:
            if len(self.possible_numbers[key]) == 1:

                split_coordinates = re.search("([a-zA-Z]+)(\d+)", key)
                x_coordinate = ord(split_coordinates.group(1).lower()) - 96
                y_coordinate = int(split_coordinates.group(2))
                self.found_dict[key] = self.possible_numbers[key].pop()
                self.board[(y_coordinate - 1) // 3][(x_coordinate - 1) // 3][
                    y_coordinate - 1 - (y_coordinate - 1) // 3 * 3][
                    x_coordinate - 1 - (x_coordinate - 1) // 3 * 3] = \
                self.found_dict[key]
                if ALL_STEPS_PRINT:
                    print(key, self.found_dict[key])
                    self.pretty_print()
                return True
        return False

        # self.possible_numbers[key] = {}

    def convert_to_str(self, nested_list):
        for i in range(len(nested_list)):
            if type(nested_list[i]) == list:
                self.convert_to_str(nested_list[i])
            elif nested_list[i]:
                nested_list[i] = str(nested_list[i])
            else:
                nested_list[i] = " "

    def pretty_print(self):
        copy_to_print = copy.deepcopy(self.board)

        self.convert_to_str(copy_to_print)
        for nbr in range(3):
            print("___________________________________________________")
            for j in range(3):
                print(copy_to_print[nbr][0][j], "|", copy_to_print[nbr][1][j],
                      "|", copy_to_print[nbr][2][j])

    def whole_check(self):
        ts = time()
        self.pretty_print()

        counter = 0
        while True:
            self.check_squares()
            for key in self.possible_numbers:
                self.check_column_and_row(key)
                self.number_anywhere_check(key)

                if self.possible_numbers[key]:
                    self.advance_col_check(key)
                    self.advance_row_check(key)
                    pass

            if not self.write_possible():
                for i in ["a1", "c1", "d1", "a4", "c4", "d4", "a7", "c7", "d7"]:
                    self.advence_square_check(i)
                    self.advence_square_check2(i)
                counter += 1
            else:
                counter = 0
            if counter > 2:
                break

        print("")
        self.pretty_print()
        print(time() - ts)


input_numbers = (
9, 6, 4, 1, 6, 9, 2, 4, 5, 6, 3, 1, 8, 7, 4, 9, 5, 7, 1, 9, 5, 2, 8, 6, 7, 4, 3)
input_coordinates = (
    "a1", "b1", "c1", "e1", "d3", "g3", "h3", "i3", "a4", "g4", "h4", "c5",
    "d5", "e5", "a6", "c6", "f6", "g6", "h6",
    "b7",
    "e7", "g7", "f8", "i8", "c9", "d9", "i9")

input_numbers = (
5, 6, 1, 6, 8, 1, 7, 2, 4, 7, 1, 9, 2, 6, 5, 9, 2, 6, 4, 1, 5, 9, 7, 3, 1)
input_coordinates = (
"c1", "g1", "h1", "b2", "i2", "c3", "f3", "i3", "a4", "b4", "d4", "e4", "b6",
"e6", "f6", "g6", "f7", "h7", "c8", "e8", "i8", "b9", "c9", "d9", "i9")

game_1 = SdkGame(input_numbers, input_coordinates)
game_1.create_board()
game_1.whole_check()





