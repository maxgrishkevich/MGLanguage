f = open('mgtest2.txt', 'r')
source_code = f.read()
f.close()

to_view = False

fsuccess = (True, 'MGLexer')

source_code += ' '

# table of language lexeme
table_of_language_tokens = {'mg->': 'keyword', '<-emg': 'keyword', 'in': 'keyword', 'out': 'keyword',
                            'while': 'keyword',
                            'do': 'keyword', 'if': 'keyword', 'goto': 'keyword', '=': 'assign_op',
                            '.': 'dot', '-': 'add_op', '+': 'add_op', '*': 'mult_op', '/': 'mult_op',
                            '^': 'degree_op', '<': 'rel_op', '<=': 'rel_op', '>=': 'rel_op', '>': 'rel_op',
                            '==': 'rel_op', '#': 'rel_op', '(': 'brackets_op', ')': 'brackets_op',
                            '{': 'brackets_op', '}': 'brackets_op', ',': 'punct',
                            ';': 'punct', ' ': 'ws', '\t': 'ws', '\n': 'eol'}

# rest of lexeme tokens
table_id_real_int = {2: 'id', 9: 'realnum', 6: 'intnum', 29: 'label'}

# state-transition function
stf = {  # identifier
        (0, 'dog'): 3, (3, 'Letter'): 10, (10, 'Letter'): 10, (10, 'Digit'): 10, (10, 'e'): 10, (10, 'other'): 2,
        # keyword
        (0, 'Letter'): 1, (0, 'e'): 1, (1, 'Letter'): 1, (1, 'e'): 1, (1, '>'): 1, (1, '-'): 1,
        (0, '<'): 11, (11, '-'): 1, (1, 'other'): 18,
        # label
        (0, '!'): 26, (26, 'Letter'): 27, (26, 'e'): 27, (27, 'Letter'): 27, (27, 'e'): 27,
        (27, 'Digit'): 27, (27, 'other'): 29,
        # intnum, realnum
        (0, 'Digit'): 4, (4, 'Digit'): 4, (4, 'e'): 7, (4, 'other'): 6, (4, 'dot'): 5, (5, 'Digit'): 19,
        (19, 'Digit'): 19, (19, 'other'): 9, (5, 'e'): 7, (7, 'AddOp'): 8, (7, '-'): 8, (7, 'Digit'): 8,
        (8, 'Digit'): 20, (20, 'Digit'): 20, (20, 'other'): 9,
        # operators, punctuations & whitespaces
        (0, '='): 17, (0, '#'): 12, (0, '>'): 15, (15, '='): 16, (11, '='): 16, (17, '='): 16,
        (0, 'ws'): 0, (0, 'eol'): 13, (0, 'AddOp'): 14, (0, '-'): 14, (0, 'MultOp'): 14, (0, '^'): 14,
        (0, ','): 14, (0, ';'): 14, (0, 'Brackets'): 14,
        # errors
        (0, 'other'): 101, (3, 'other'): 102, (5, 'other'): 103, (7, 'other'): 104, (8, 'other'): 105,
        (26, 'other'): 108
       }

init_state = 0  # 0 - start position
end_states = {2, 6, 9, 12, 11, 13, 14, 15, 16, 17, 18, 29, 101, 102, 103, 104, 105, 106, 107, 108}  # end positions
star = {2, 6, 9, 18, 29}  # star
errors = {101, 102, 103, 104, 105, 107, 108}  # errors factoring

var_table = {}  # table of identifiers
const_table = {}  # table of constants
label_table = {}  # table of labels
symb_table = {}  # table of symbols

state = init_state  # current position

len_code = len(source_code) - 1  # number of the last symbol in program file
num_line = 1  # lexical analyse starts from firs line
num_char = -1  # and from first symbol
char = ''  # current symbol
lexeme = ''  # current lexeme


def lexer():
    global char, lexeme, state, fsuccess
    try:
        while num_char < len_code:
            char = next_char()
            char_class = class_of_char(char)
            state = next_state(state, char_class)
            if char == '<' and next_char(with_inc=False) == '-':
                lexeme += char
            elif is_final(state):
                processing()
                if state in errors:
                    break
            elif state == 0:
                lexeme = ''
            else:
                lexeme += char
    except SystemExit as e:
        # notify about error detection
        fsuccess = (False, 'MGLexer')
        print('\nMGLexer: Exit from program with error code {0}'.format(e))
        exit()

    if to_view:
        print_tables('All')
    # print("\033[36m{}".format(""), end="")
    print('\nMGLexer: Lexical analyse is ended successfully!\n')
    # print("\033[0m{}".format(""), end="")

    # print('\nMGLexer: Lexical analyse is ended successfully!')
    # print('\nMGLexer: Table of symbols:')
    # print(symb_table)
    # print('\nMGLexer: Table of variables:')
    # print(var_table)
    # print('\nMGLexer: Table of constants:')
    # print(const_table)
    # print('\nMGLexer: Table of labels:')
    # print(label_table)


def processing():
    global state, lexeme, num_line, num_char  # , char, tableOfSymb
    if state in (2, 6, 9, 18, 29):  # ident, int, float, keyword, label
        token = get_token(state, lexeme)
        if token == 'error':
            state = 107
            fail()
        elif token != 'keyword':  # if not keyword
            index = index_id_const_label(state, lexeme, token)
            # print('{0:<3d} {1:<10s} {2:<10s} {3:<2d} '.format(num_line, lexeme, token, index))
            symb_table[len(symb_table) + 1] = (num_line, lexeme, token, index)
        else:  # if keyword
            # print('{0:<3d} {1:<10s} {2:<10s} '.format(num_line, lexeme, token))
            symb_table[len(symb_table) + 1] = (num_line, lexeme, token, '')
        lexeme = ''
        num_char = previous_char(num_char)  # star
        state = init_state
    if state == 13:  # \n
        num_line += 1
        state = init_state
    if state == 15 or state == 11:  # rel_op
        lexeme += char
        if next_char() == '=':
            char_class = class_of_char('=')
            state = next_state(state, char_class)
        else:
            num_char -= 1
            token = get_token(state, lexeme)
            # print('{0:<3d} {1:<10s} {2:<10s} '.format(num_line, lexeme, token))
            symb_table[len(symb_table) + 1] = (num_line, lexeme, token, '')
            lexeme = ''
            state = init_state
    if state == 17:  # assign_op
        lexeme += char
        if next_char() == '=':
            char_class = class_of_char('=')
            state = next_state(state, char_class)
        else:
            num_char -= 1
            token = get_token(state, lexeme)
            # print('{0:<3d} {1:<10s} {2:<10s} '.format(num_line, lexeme, token))
            symb_table[len(symb_table) + 1] = (num_line, lexeme, token, '')
            lexeme = ''
            state = init_state
    if state == 14:
        lexeme += char
        token = get_token(state, lexeme)
        # print('{0:<3d} {1:<10s} {2:<10s} '.format(num_line, lexeme, token))
        symb_table[len(symb_table) + 1] = (num_line, lexeme, token, '')
        lexeme = ''
        state = init_state
    if state == 16:
        lexeme += '='
        token = get_token(state, lexeme)
        # print('{0:<3d} {1:<10s} {2:<10s} '.format(num_line, lexeme, token))
        symb_table[len(symb_table) + 1] = (num_line, lexeme, token, '')
        lexeme = ''
        state = init_state
    if state == 12:
        token = get_token(state, lexeme)
        # print('{0:<3d} {1:<10s} {2:<10s} '.format(num_line, lexeme, token))
        symb_table[len(symb_table) + 1] = (num_line, lexeme, token, '')
        lexeme = ''
        state = init_state
    if state in errors:  # (101): error
        fail()


def fail():
    # print("\033[31m{}".format(""), end="")
    if state == 101:
        print('\nMGLexer ERROR:\n\t[{0}]: Unexpected symbol \'{1}\'.'
              '\n\tSymbol \'{1}\' isn`t exist in MGAlphabet'
              .format(num_line, char))
        exit(101)
    if state == 102:
        print('\nMGLexer ERROR:\n\t[{0}]: Wrong symbol in identifier \'{1}\'.'
              '\n\tFirst symbol in identifier must be a letter.'
              .format(num_line, char))
        exit(102)
    if state == 103:
        print('\nMGLexer ERROR:\n\t[{0}]: Wrong format of number.'
              '\n\tExpected digit after symbol \'.\'.'.format(num_line))
        exit(103)
    if state == 104:
        print('\nMGLexer ERROR:\n\t[{0}]: Wrong format of number.'
              '\n\tExpected digit or add operator after symbol \'e\'.'.format(num_line))
        exit(104)
    if state == 105:
        print('\nMGLexer ERROR:\n\t[{0}]: Wrong format of number.'
              '\n\tExpected digit after digit or add operator.'.format(num_line))
        exit(105)
    if state == 108:
        print('\nMGLexer ERROR:\n\t[{0}]: Wrong symbol in label \'{1}\'.'
              '\n\tFirst symbol in label must be a letter.'
              .format(num_line, char))
        exit(108)
    if state == 107:
        print('\nMGLexer ERROR:\n\t[{0}]: Entered lexeme could not recognized \'{1}\'.'
              '\n\tDelete it or fix the error'
              .format(num_line, lexeme))
        exit(107)


def is_final(end_state):
    if end_state in end_states:
        return True
    else:
        return False


def next_char(with_inc=True):
    global num_char
    if with_inc:
        num_char += 1
        return source_code[num_char]
    else:
        return source_code[num_char + 1]


def previous_char(num_char):
    return num_char - 1


def next_state(current_state, char_class):
    try:
        return stf[(current_state, char_class)]
    except KeyError:
        if (current_state, 'other') in stf:
            return stf[(current_state, 'other')]
        else:
            return 107


def class_of_char(current_char):
    if current_char in "#=<>^,;e-!":
        res = current_char
    elif current_char in '@':
        res = "dog"
    elif current_char in '.':
        res = "dot"
    elif current_char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
        res = "Letter"
    elif current_char in "0123456789":
        res = "Digit"
    elif current_char in " \t":
        res = "ws"
    elif current_char in "\n":
        res = "eol"
    elif current_char in "(){}":
        res = "Brackets"
    elif current_char in "+-":
        res = "AddOp"
    elif current_char in "*/":
        res = "MultOp"
    elif current_char in "^":
        res = "DegreeOp"
    else:
        res = 'symbol is not in the MGAlphabet'
    return res


def get_token(current_state, current_lexeme):
    try:
        return table_of_language_tokens[current_lexeme]
    except KeyError:
        if current_state in table_id_real_int:
            return table_id_real_int[current_state]
        else:
            return 'error'


def index_id_const_label(current_state, current_lexeme, current_token):
    index = 0
    # index1 = []
    if current_state == 2:
        index1 = var_table.get(current_lexeme)
        if index1 is None:
            index = len(var_table) + 1
            var_table[current_lexeme] = (index, 'type_undef', 'val_undef')  # ('type_undef', 'val_undef')
    elif current_state == 29:
        index1 = label_table.get(current_lexeme)
        if index1 is None:
            index = len(label_table) + 1
            label_table[current_lexeme] = index  # ('type_undef', 'val_undef')
    elif current_state in (6, 9):
        index1 = const_table.get(current_lexeme)
        if index1 is None:
            index = len(const_table) + 1
            val = 0
            if current_state == 9:
                val = float(current_lexeme)
            elif current_state == 6:
                val = int(current_lexeme)
            const_table[current_lexeme] = (index, current_token, val)
        if not (index1 is None):        #
            if len(index1) == 2:        #
                index, _ = index1       #
            else:                       #
                index, _, _ = index1    #
    return index


def print_tables(table):
    if table == "Symbol":
        print_symb_table()
    elif table == "Id":
        print_id_table()
    elif table == "Const":
        print_const_table()
    elif table == "Label":
        print_label_table()
    else:
        print_symb_table()
        print_id_table()
        print_const_table()
        print_label_table()
    return True


def print_symb_table():
    print("\n Table of symbols")
    s1 = '{0:<10s} {1:<10s} {2:<10s} {3:<10s} {4:<5s} '
    s2 = '{0:<10d} {1:<10d} {2:<10s} {3:<10s} {4:<5s} '
    print(s1.format("numRec", "numLine", "lexeme", "token", "index"))
    for numRec in symb_table:
        numLine, lexeme, token, index = symb_table[numRec]
        print(s2.format(numRec, numLine, lexeme, token, str(index)))


def print_id_table():
    print("\n Table of identifiers")
    s1 = '{0:<10s} {1:<15s} {2:<15s} {3:<10s} '
    print(s1.format("Ident", "Type", "Value", "Index"))
    s2 = '{0:<10s} {2:<15s} {3:<15s} {1:<10d} '
    for id in var_table:
        index, type, val = var_table[id]
        print(s2.format(id, index, type, str(val)))


def print_const_table():
    print("\n Table of constants")
    s1 = '{0:<10s} {1:<10s} {2:<10s} {3:<10s} '
    print(s1.format("Const", "Type", "Value", "Index"))
    s2 = '{0:<10s} {2:<10s} {3:<10} {1:<10d} '
    for const in const_table:
        index, type, val = const_table[const]
        print(s2.format(str(const), index, type, val))


def print_label_table():
    if len(label_table) == 0:
        print("\n Table of labels is empty")
    else:
        s1 = '{0:<10s} {1:<10s} '
        print("\n Table of labels")
        print(s1.format("Label", "Index"))
        s2 = '{0:<10s} {1:<10d} '
        for lbl in label_table:
            val = label_table[lbl]
            print(s2.format(lbl, val))


# lexer()
