from mglexer import lexer
from mglexer import symb_table

lexer()

num_row = 1

len_symb_table = len(symb_table)

postfix_code = []

view_translation = True
view_syntax = True


def parser():
    print('\n' + '=' * 60 + '\n')
    try:
        parse_token('mg->', 'keyword', '')
        parse_statement_list()
        print(postfix_code)
        print('\nMGParser: Parsing & translation are ended successful')
        return True
    except SystemExit as e:
        print('\nMGParser: Crash program with code {0}'.format(e))
        exit()


def parse_statement_list(spec_instr=''):
    if view_syntax:
        print('\t parse_statement_list():')
    while parse_statement(spec_instr):
        pass
    return True


def parse_statement(spec_instr=''):
    global num_row

    if view_syntax:
        print('\t\t parseStatement():')

    if get_symb():
        num_line, lexeme, token = get_symb()
    else:
        return False

    if token == 'id':
        parse_id()
        parse_assign()
        parse_token(';', 'punct', '')
        return True
    elif (lexeme, token) in [('int', 'keyword'), ('real', 'keyword'), ('bool', 'keyword')]:
        parse_id_types()
        return True
    elif (lexeme, token) == ('in', 'keyword'):
        parse_in()
        return True
    elif (lexeme, token) == ('out', 'keyword'):
        parse_out()
        return True
    elif lexeme in ('true', 'false') and token == 'boolval':
        parse_out()
        return True
    elif (lexeme, token) == ('if', 'keyword'):
        parse_if()
        return True
    elif (lexeme, token) == ('do', 'keyword'):
        parse_do_while()
        return True
    elif (lexeme, token) == ('<-emg', 'keyword'):
        parse_token(lexeme, token, '')
        return True
    elif spec_instr == 'IF':
        if (lexeme, token) == ('}', 'brackets_op'):
            return False
        else:
            fail_parse('instruction mismatch', (num_line, lexeme, token, ''))
            return False
    elif spec_instr == 'DO':
        if (lexeme, token) == ('}', 'brackets_op'):
            return False
        else:
            fail_parse('instruction mismatch', (num_line, lexeme, token, ''))
            return False
    else:
        fail_parse('instruction mismatch', (num_line, lexeme, token, ''))
        return False


def parse_id_types():
    global num_row

    if view_syntax:
        print('\t' * 4 + 'parse_id_types():')

    _, lexeme, token = get_symb()

    if lexeme in ['int', 'real', 'bool'] and token == 'keyword':
        num_row += 1
        parse_id()
        _, lexeme, token = get_symb()
        if lexeme == '=' and token == 'assign_op':
            parse_assign()
        parse_token(';', 'punct', '\t' * 5)
        return True
    else:
        return False


def parse_in():
    global num_row

    if view_syntax:
        print('\t' * 4 + 'parse_in():')

    _, lexeme, token = get_symb()
    if (lexeme, token) == ('in', 'keyword'):
        num_row += 1
        parse_token('(', 'brackets_op', '\t' * 5)
        parse_id_list()
        parse_token(')', 'brackets_op', '\t' * 5)
        parse_token(';', 'punct', '\t' * 5)
        return True
    else:
        return False


def parse_out():
    global num_row

    if view_syntax:
        print('\t' * 4 + 'parse_out():')

    _, lexeme, token = get_symb()
    if (lexeme, token) == ('out', 'keyword'):
        num_row += 1
        parse_token('(', 'brackets_op', '\t' * 5)
        parse_expression_list()
        parse_token(')', 'brackets_op', '\t' * 5)
        parse_token(';', 'punct', '\t' * 5)
        return True
    else:
        return False


def parse_if():
    global num_row

    if view_syntax:
        print('\t' * 4 + 'parse_if():')

    _, lexeme, token = get_symb()
    if (lexeme, token) == ('if', 'keyword'):
        num_row += 1
        parse_token('(', 'brackets_op', '\t' * 5)
        parse_bool_expression()
        parse_token(')', 'brackets_op', '\t' * 5)
        _, lexeme, token = get_symb()
        if (lexeme, token) == ('goto', 'keyword'):
            parse_token('goto', 'keyword', '\t' * 5)
        else:
            return False
        parse_token('{', 'brackets_op', '\t' * 5)
        parse_statement_list('IF')
        parse_token('}', 'brackets_op', '\t' * 5)
        return True
    else:
        return False


def parse_do_while():
    global num_row

    if view_syntax:
        print('\t' * 4 + 'parse_do_while():')

    _, lexeme, token = get_symb()
    if (lexeme, token) == ('do', 'keyword'):
        num_row += 1
        parse_token('{', 'brackets_op', '\t' * 5)
        parse_statement_list('DO')
        parse_token('}', 'brackets_op', '\t' * 5)
        _, lexeme, token = get_symb()
        if (lexeme, token) == ('while', 'keyword'):
            parse_token('while', 'keyword', '\t' * 5)
        else:
            return False
        parse_bool_expression()
        return True
    else:
        return False


def parse_expression_list():
    if view_syntax:
        print('\t' * 5 + 'parse_expression_list():')
    while parse_expression():
        if get_symb():
            numLine, lexeme, token = get_symb()
        else:
            return True
        if lexeme == ')':
            break
        parse_token(',', 'punct', '\t\t\t\t\t')
    return True


def parse_expression():
    global num_row, postfix_code

    if view_syntax:
        print('\t' * 5 + 'parse_expression():')

    parse_term()
    f = True

    while f:
        if get_symb():
            num_line, lexeme, token = get_symb()
        else:
            return True

        if token in 'add_op':
            num_row_copy = num_row
            num_row += 1
            if view_syntax:
                print('\t' * 6 + '[{0}]: {1}'.format(num_line, (lexeme, token)))
            parse_term()
            postfix_code.append((lexeme, token))
            if view_translation:
                print_config(lexeme, num_row_copy)
        else:
            f = False
    return True


def parse_bool_expression():
    global num_row

    if view_syntax:
        print('\t' * 5 + 'parse_bool_expr():')

    parse_expression()
    if get_symb():
        num_line, lexeme, token = get_symb()
    else:
        return True
    if token in 'rel_op':
        num_row += 1
        if view_syntax:
            print('\t' * 5 + '[{0}]: {1}'.format(num_line, (lexeme, token)))
        parse_expression()

    elif token in 'keyword':
        if view_syntax:
            print('\t' * 5 + '[{0}]: {1}'.format(num_line, (lexeme, token)))
        return True

    else:
        fail_parse('bool expression error', (num_line, lexeme, token, '==, #, <=, >=, <, >'))
    return True


def parse_assign():
    global num_row, postfix_code

    if view_syntax:
        print('\t' * 4 + 'parseAssign():')
    num_row -= 1
    num_line, lexeme, token = get_symb()
    postfix_code.append((lexeme, token))
    num_row += 1

    if view_translation:
        print_config(lexeme, num_row)

    if view_syntax:
        print('\t' * 5 + '[{0}]: {1}'.format(num_line, (lexeme, token)))

    if parse_token('=', 'assign_op', '\t\t\t\t\t'):
        _, lexeme, token = get_symb()
        if lexeme in ('true', 'false') and token == 'boolval':
            parse_token(lexeme, token, '')
        else:
            parse_expression()
        postfix_code.append(('=', 'assign_op'))
        if view_translation:
            print_config('=', num_row)
        return True
    else:
        return False


def parse_id_list():
    if view_syntax:
        print('\t' * 5 + 'parse_id_list():')

    while parse_id():
        if get_symb():
            num_line, lexeme, token = get_symb()
        else:
            return True

        if lexeme == ',':
            parse_token(',', 'punct', '\t\t\t\t\t')
        else:
            return True
    num_line, lexeme, token = get_symb()
    fail_parse('token mismatch in parse_id_list()', (num_line, lexeme, token))


def parse_id():
    if view_syntax:
        print('\t' * 6 + 'parse_id():')
    global num_row

    if num_row > len_symb_table:
        fail_parse('out of bounds', ('', 'ident', num_row))

    num_line, lexeme, token = get_symb()

    if token == 'id':
        num_row += 1

        if view_syntax:
            print('\t' * 6 + 'parseToken():\n' + '\t' * 6 + '[{0}]: {1}'.format(num_line, (lexeme, token)))
        return True
    else:
        return False


def parse_term():
    global num_row, postfix_code

    if view_syntax:
        print('\t' * 6 + 'parse_term():')

    parse_factor()
    f = True

    while f:
        if get_symb():
            num_line, lexeme, token = get_symb()
        else:
            return True

        if token in 'mult_op':
            num_row_copy = num_row
            num_row += 1

            if view_syntax:
                print('\t' * 6 + '[{0}]: {1}'.format(num_line, (lexeme, token)))

            parse_factor()

            postfix_code.append((lexeme, token))

            if view_translation:
                print_config(lexeme, num_row_copy)

        else:
            f = False
    return True


def parse_factor():
    global num_row, postfix_code

    if view_syntax:
        print('\t' * 7 + 'parseFactor():')
    if get_symb():
        num_line, lexeme, token = get_symb()
    else:
        return True

    if view_syntax:
        print('\t' * 7 + '[{0}]: {1}'.format(num_line, (lexeme, token)))

    if token in ('intnum', 'realnum', 'id'):
        postfix_code.append((lexeme, token))

        if view_translation:
            print_config(lexeme, num_row)

        num_row += 1

        if get_symb():
            num_line, lexeme, token = get_symb()
        else:
            return True

        if lexeme == '^':
            num_row_copy = num_row
            num_row += 1

            if view_syntax:
                print('\t' * 6 + '[{0}]: {1}'.format(num_line, (lexeme, token)))

            parse_factor()

            postfix_code.append((lexeme, token))

            if view_translation:
                print_config(lexeme, num_row_copy)

    elif lexeme == '(':
        num_row += 1
        parse_expression()
        parse_token(')', 'brackets_op', '\t' * 7)
    elif lexeme == '-':
        num_row_copy = num_row
        num_row += 1
        parse_expression()

        postfix_code.append(('NEG', token))

        if view_translation:
            print_config(lexeme, num_row_copy)

    else:
        fail_parse('expression->factor error',
                   (num_line, lexeme, token, 'intnum, realnum, id, \'(\' expression \')\''))
    return True


def fail_parse(string, ftuple):
    if string == 'out of bounds':
        (lexeme, token, num_str) = ftuple
        print(
            '\nMGParser ERROR: \n\tEnding of program is expected - in table of lexemes no lexeme with number {1}.'
            '\n\tError parsing element - {0}.'.format((lexeme, token), num_str))
        exit(106)

    elif string == 'inconsistency of tokens':
        (num_line, cur_lexeme, cur_token, lexeme, token) = ftuple
        print('\nMGParser ERROR: \n\t[{0}]: Unexpected current element (\'{1}\', {2}).'
              '\n\tTrying to parse - (\'{3}\', {4}).'.format(num_line, cur_lexeme, cur_token, lexeme, token))
        exit(107)

    elif string == 'instruction mismatch':
        (num_line, lexeme, token, expected) = ftuple
        print(
            '\nMGParser ERROR: \n\t[{0}]: Unexpected lexeme (\'{1}\', {2}).'.format(num_line, lexeme, token, expected))
        exit(108)

    elif string == 'expression->factor error':
        (num_line, lexeme, token, expected) = ftuple
        print(
            '\nMGParser ERROR: \n\t[{0}]: Unexpected expression->factor element (\'{1}\', {2}).'
            '\n\tExpected - \'{3}\'.'.format(num_line, lexeme, token, expected))
        exit(109)

    elif string == 'bool expression error':
        (num_line, lexeme, token, expected) = ftuple
        print(
            '\nMGParser ERROR: \n\t[{0}]: Unexpected bool element (\'{1}\', {2}).'
            '\n\tExpected relational operator - \'{3}\'.'.format(num_line, lexeme, token, expected))
        exit(110)

    elif string == ('token mismatch in parse_token()', 'token mismatch in parse_id_list()'):
        (num_line, lexeme, token) = ftuple
        print('\nMGParser ERROR: \n\t[{0}]: Unexpected element (\'{1}\', {2}).'
              '\n\tDetails: {3}'
              '\n\tExpected id'.format(num_line, lexeme, token, string))
        exit(111)


def print_config(lexeme, num_line):
    stage = '\nStep of translation\n'
    stage += 'lexeme: \'{0}\'\n'
    stage += 'symb_table[{1}] = {2}\n'
    stage += 'postfix_code = {3}\n'
    print(stage.format(lexeme, num_line, str(symb_table[num_line]), str(postfix_code)))


def get_symb():
    if num_row > len_symb_table:
        return False
    num_line, lexeme, token, _ = symb_table[num_row]
    return num_line, lexeme, token


def parse_token(lexeme, token, indent):
    global num_row

    if num_row > len_symb_table:
        fail_parse('out of bounds', (lexeme, token, num_row))

    cur_line, cur_lexeme, cur_token = get_symb()

    num_row += 1

    if lexeme == '':
        if cur_token == token:
            if view_syntax:
                print(indent + 'parseToken():\n' + indent + '[{0}]: {1}'.format(cur_line, (lexeme, token)))
            return True
        else:
            fail_parse('token mismatch in parse_token()', (cur_line, lexeme, token))
            return False

    if (cur_lexeme, cur_token) == (lexeme, token):
        if view_syntax:
            print(indent + 'parse_token():\n' + indent + '[{0}]: {1}'.format(cur_line, (lexeme, token)))
        return True
    else:
        fail_parse('inconsistency of tokens', (cur_line, cur_lexeme, cur_token, lexeme, token))
        return False


# parser()
