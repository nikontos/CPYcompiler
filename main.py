import argparse
import os.path
import string
from icecream import ic


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

class Token:
    def __init__(self, recognised_string, family, line_number):
        self.recognised_string = recognised_string
        self.family = family
        self.line_number = line_number

    # def __init__(self):
    #    pass

    # def __str__(self):
    #     print_at_line = "at line"
    #     print(
    #         f"{self.recognised_string : <30} {self.family :<25} {print_at_line: <7} {self.line_number: >4}"
    #     )
    #     pass

    ##############################################################
    #                                                            #
    #                            Lex                             #
    #                                                            #
    ##############################################################


class Lex:
    state = ""
    recognised_string = ""
    position = 0
    char = ""

    # This is the alphabet of allowed symbols and words
    digits = string.digits
    keywords = [
        "main",
        "def",
        "#def",
        "#int",
        "global",
        "if",
        "elif",
        "else",
        "while",
        "print",
        "return",
        "input",
        "int",
        "and",
        "or",
        "not",
    ]
    alphabet = string.ascii_letters + "_"
    grouping_symbols = ["(", ")", "#{", "#}", "[", "]",'{', '}']
    num_op = ["+", "-", "*", "//", '%']
    relation_op = ["<", ">", "!=", "<=", ">=", "=="]
    delimiter_op = [";", ",", ":"]

    def __init__(self, file_name):
        self.current_line = 1
        self.file_name = file_name
        self.file = open(self.file_name, "r")

    def __del__(self):
        return

    def token_sneak_peak(self):
        """@return: A token type object, the next token without actually consuming it"""
        tmp_line = self.current_line
        tmp_pos = self.file.tell()
        tmp_tk = self.next_token()
        print(
            "############# After sneak peak"
            + str(self.position)
            + "#######################"
        )
        self.file.seek(tmp_pos)
        self.current_line = tmp_line
        return tmp_tk
    
    # This is the state machine
    def next_token(self):
        """Returns the next token in the file"""
        if not os.path.isfile(self.file_name):
            print("Wrong file path")
            return
        self.state = "start"
        while self.state == "start":
            self.recognised_string = ""
            # ic(self.char)
            self.char = self.file.read(1)
            self.position = self.file.tell()
            if self.char == "":
                print("EOF")
                exit()
            elif self.char == "\n":
                self.current_line += 1
                continue
            elif self.char == " ":
                continue
            elif self.digits.count(self.char) and self.state == "start":
                return self.digit_token()
            elif self.char in self.alphabet and self.state == "start":
                return self.keyword_token()
            elif self.char in self.grouping_symbols and self.state == "start":
                return self.grouping_symbol_token()
            elif self.char == "#" and self.state == "start":
                return self.rem()
            elif self.char in self.delimiter_op and self.state == "start":
                return self.delimeter_token()
            elif (
                self.char in self.relation_op or self.char == "!"
            ) and self.state == "start":
                return self.relation_op_token()
            elif self.char == "=" and self.state == "start":
                return self.assign_token()
            elif self.char in self.num_op or self.char == "/" and self.state == "start":
                return self.num_op_token()

    def __error(self):
        print(
            "There was an error at "
            + self.file_name
            + " @Line : "
            + str(self.current_line)
            + " recognised_string: " + self.recognised_string
            + " state: " + self.state
        )
        exit()

    def error(self, output):
        print(
            bcolors.YELLOW
            + "[ERROR]"
            + bcolors.ENDC
            + bcolors.OKGREEN
            + " Expected "
            + bcolors.BOLD
            + output
            + bcolors.RED
            + " at Line: "
            + str(self.current_line)
        )
        exit()

    def __len_test(self):
        """Returns False if the string of the token is >30 chars"""

        if len(self.recognised_string) > 30:
            return 0
        return 1

    def num_op_token(self):
        self.recognised_string += self.char
        if self.char == "+":
            return Token(self.recognised_string, "addOP", self.current_line)
        elif self.char == "-":
            return Token(self.recognised_string, "minusOP", self.current_line)
        elif self.char == "*":
            return Token(self.recognised_string, "multiOP", self.current_line)
        elif self.char == '%':
            return Token(self.recognised_string, "moduloOP", self.current_line)
        elif self.char == "/":
            self.recognised_string += self.char
            self.char = self.file.read(1)
            if self.char == "/":
                return Token(self.recognised_string, "divisionOP", self.current_line)
            else:
                self.position = self.file.tell()
                self.file.seek(self.position - 1)
                print("Expected // Division")
                self.__error()

    def assign_token(self):
        self.state = "asgn"
        self.recognised_string += self.char
        self.char = self.file.read(1)
        self.position = self.file.tell()
        if self.char == "=":
            self.recognised_string += self.char
            return Token(self.recognised_string, "isEqual", self.current_line)
        else:
            self.file.seek(self.position - 1)
            return Token(self.recognised_string, "asgn", self.current_line)

    def relation_op_token(self):
        self.recognised_string += self.char
        if self.char == "<":
            self.char = self.file.read(1)
            self.position = self.file.tell()
            if self.char == "=":
                self.recognised_string += self.char
                return Token(self.recognised_string, "lessEqual", self.current_line)
            else:
                self.file.seek(self.position - 1)
                return Token(self.recognised_string, "lessThan", self.current_line)
        if self.char == ">":
            self.char = self.file.read(1)
            self.position = self.file.tell()
            if self.char == "=":
                self.recognised_string += self.char
                return Token(self.recognised_string, "greaterEqual", self.current_line)
            else:
                self.file.seek(self.position - 1)
                return Token(self.recognised_string, "greaterThan", self.current_line)
        if self.char == "!":
            self.char = self.file.read(1)
            self.position = self.file.tell()
            if self.char == "=":
                self.recognised_string += self.char
                return Token(self.recognised_string, "notEqual", self.current_line)
            else:
                self.recognised_string += self.char
                self.file.seek(self.position - 1)
                print("Expected = instead found : " + self.recognised_string)
                self.__error()

    def delimeter_token(self):
        self.recognised_string += self.char
        self.state = "delimeter"
        return Token(self.recognised_string, "del", self.current_line)

    def rem(self):
        """
        Handles the '#' character and returns the token it corresponds
        Either a comment, a keyword or a grouping symbol
        """
        self.recognised_string += self.char
        self.char = self.file.read(1)
        comment_line = self.current_line

        # comments state
        if self.char == "#":
            self.state = "comment"
            while self.state == "comment":
                self.recognised_string += self.char
                self.char = self.file.read(1)
                if self.char == "":
                    print(
                        "Reached EOF without closing comments, comments started @Line: "
                        + str(comment_line)
                    )
                    exit()
                if self.char == "\n":
                    self.current_line += 1
                if self.char == "#":
                    self.recognised_string += self.char
                    self.char = self.file.read(1)
                    if self.char == "\n":
                        self.current_line += 1
                    if self.char == "#":
                        self.recognised_string = ""
                        # this return statement is used to ignore the comments
                        return self.next_token()
        elif self.char in self.grouping_symbols:
            return self.grouping_symbol_token()
        elif self.char in self.alphabet:
            return self.keyword_token()

    def grouping_symbol_token(self):
        self.recognised_string += self.char
        return Token(self.recognised_string, "grouping_symbol", self.current_line)

    def keyword_token(self):
        self.state = "keyword"
        while self.state == "keyword":
            self.recognised_string += self.char
            self.char = self.file.read(1)
            self.position = self.file.tell()
            if (
                (self.char not in self.alphabet and self.char not in self.digits)
                or self.char == ""
                or self.char == " "
            ):
                self.state = "terminal"
                self.file.seek(self.position - 1)
                if self.recognised_string in self.keywords:
                    return Token(self.recognised_string, "keyword", self.current_line)
                return Token(self.recognised_string, "var", self.current_line)

    def digit_token(self):
        self.state = "digit"
        self.recognised_string = self.recognised_string + self.char
        ic(self.recognised_string)
        while self.state == "digit":
            self.char = self.file.read(1)
            self.position = self.file.tell()
            if (
                self.char not in self.digits
                or self.char == ""
                or self.char == " "
                or self.char in self.grouping_symbols
                or self.char == "="
            ):
                self.state = "terminal"
                # the -1 on position is very important to not consume the next char
                self.file.seek(self.position - 1)
                if (
                    self.char not in self.digits
                    and self.char != ""
                    and self.char != "\n"
                    and self.char not in self.grouping_symbols
                    and self.char not in self.delimiter_op
                    and self.char != ' '
                    and self.char!= "="
                    and self.char != '!'
                ):
                    ic("ERROR")
                    self.__error()
                    break
                # I have no idea how this condition fixed all this crap
                if self.char == "":
                    self.file.seek(self.position)
                if self.__len_test() == 0 or int(self.recognised_string) > 9999:
                    print("Error too large number")
                    break
                if self.char in self.grouping_symbols:
                    return Token(self.recognised_string, "dig", self.current_line)
                
            self.recognised_string = self.recognised_string + self.char
        return Token(self.recognised_string, "dig", self.current_line)


tk = Lex("test.cpy")


while True:
    tmp = (tk.next_token())
    ic(tmp.recognised_string)
