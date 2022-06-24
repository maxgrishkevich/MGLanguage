from mglexer import symb_table, var_table, const_table, label_table, source_code
from mglexer import print_tables, print_id_table, print_label_table, print_symb_table, print_const_table
from mgparser import parser, postfix_code
from mgstack import Stack
import re

stack = Stack()
# stack.print()
to_interpret = False
to_view = False
command_track = []
next_instr = 0


def interpreter():
    if parser():
        global stack, postfix_code, command_track, next_instr
        if to_view:
            print('\n' + '=' * 60 + '\n')

        # print(postfix_code)
        cycles_numb = 0
        instr_num = 0
        max_numb = len(postfix_code)
        try:
            # for i in range(0, max_numb):
            while instr_num < max_numb:
                cycles_numb += 1
                lex, tok = postfix_code[instr_num]
                command_track.append((instr_num, lex, tok))

                if tok in ('intnum', 'realnum', 'id', 'label'):
                    stack.push((lex, tok))
                    next_instr = instr_num + 1
                elif tok in ('jump', 'jf', 'colon'):
                    next_instr = do_jumps(tok)
                else:
                    do_it(lex, tok)
                    next_instr = instr_num + 1

                if to_interpret:
                    print_config(instr_num, lex, tok, max_numb)
                instr_num = next_instr

            if to_view:
                print_tables('All')
            # print("\033[36m{}".format(""), end="")
            print('\n\nMGInterpreter: Interpreting ended successfully!')
            # print("\033[0m{}".format(""), end="")
            return command_track
        except SystemExit as e:
            print('\nMGInterpreter: Crash program with code {0}'.format(e))
        return True


def do_jumps(tok):
    if tok == 'jump':
        next = processing_jump()
    elif tok == 'colon':
        next = processing_colon()
    elif tok == 'jf':
        next = processing_jf()
    return next


def processing_jump():
    global stack, label_table
    (lex_label, tok_label) = stack.pop()
    val = label_table[lex_label]
    return val


def processing_colon():
    global stack, next_instr
    stack.pop()
    return next_instr + 1


def processing_jf():
    global stack, label_table, next_instr
    (lex_label, tok_label) = stack.pop()
    try:
        (lex_bool, tok_bool) = stack.pop()
    except TypeError:
        fail('non recognized label', (lex_label, tok_label))
    if lex_bool == 'False':
        val = label_table[lex_label]
        return val
    else:
        return next_instr + 1


def print_config(step, lex, tok, maxN):
    if step == 1:
        print('\n' + '=' * 60)
        print_tables('All')

    print('\nStep of interpretation: {0}'.format(step))
    if tok in ('intnum', 'realnum'):
        print('Lexeme: {0} in const_table: {1}'.format((lex, tok), lex + ':' + str(const_table[lex])))
    elif tok in 'id':
        print('Lexeme: {0} in id_table: {1}'.format((lex, tok), lex + ':' + str(var_table[lex])))
    else:
        print('Lexeme: {0}'.format((lex, tok)))

    print('postfix_code={0}'.format(postfix_code))
    stack.print()

    if step == maxN:
        for table in ('Id', 'Const', 'Label'):
            print_tables(table)
    return True


def do_it(lex, tok):
    global stack, postfix_code, var_table, const_table, label_table
    if (lex, tok) == ('=', 'assign_op'):
        (lexL, tokL) = stack.pop()
        (lexR, tokR) = stack.pop()
        var_table[lexR] = (var_table[lexR][0], const_table[lexL][1], const_table[lexL][2])
    elif lex == 'NEG':
        (lexx, tokk) = stack.pop()
        processingNEG((lexx, tokk))
    elif tok in ('add_op', 'mult_op', 'degree_op', 'rel_op'):
        (lexR, tokR) = stack.pop()
        (lexL, tokL) = stack.pop()
        proc_add_mult_deg((lexL, tokL), lex, (lexR, tokR))
    elif tok == 'out':
        (lex, tok) = stack.pop()

        if tok == 'id':
            if var_table[lex][1] == 'type_undef':
                fail('non initialized variable', (lex, var_table[lex]))
            else:
                val = var_table[lex][2]
                print('Output ' + lex + ': ', end="")
                print(str(val))
        else:
            print(str(const_table[lex][2]))

    elif tok == 'in':
        (lex, tok) = stack.pop()

        inp = input('Input '+lex+': ')

        if inp.isdigit():
            inpType = 'integer'
            inpVal = int(inp)
        elif re.match('^[-+]?([0-9]+[.,])?[0-9]+(?:[e][-+]?[0-9]+)?$', inp):
            inpType = 'real'
            inpVal = float(inp)
        else:
            fail('wrong type', (lex, type(inp)))

        var_table[lex] = (var_table[lex][0], inpType, inpVal)

    return True


def processingNEG(lt):
    global stack, postfix_code, var_table, const_table, label_table
    lex, tok = lt

    if tok == 'id':
        if var_table[lex][1] == 'type_undef':
            fail('non initialized variable', (lex, var_table[lex]))
        else:
            val, tok = (var_table[lex][2], var_table[lex][1])
    else:
        val = const_table[lex][2]

    value = -val
    stack.push((str(value), tok))
    to_const_table(value, tok)


def proc_add_mult_deg(ltL, lex, ltR):
    global stack, postfix_code, var_table, const_table, label_table
    lexL, tokL = ltL
    lexR, tokR = ltR

    if tokL == 'id':
        if var_table[lexL][1] == 'type_undef':
            fail('non initialized variable', (lexL, var_table[lexL]))
        else:
            valL, tokL = (var_table[lexL][2], var_table[lexL][1])
    else:
        valL = const_table[lexL][2]

    if tokR == 'id':
        if var_table[lexR][1] == 'type_undef':
            fail('non initialized variable', (lexR, var_table[lexR]))
        else:
            valR, tokR = (var_table[lexR][2], var_table[lexR][1])
    else:
        valR = const_table[lexR][2]

    get_value((valL, lexL, tokL), lex, (valR, lexR, tokR))


def get_value(vtL, lex, vtR):
    global stack, postfix_code, var_table, const_table, label_table
    valL, lexL, tokL = vtL
    valR, lexR, tokR = vtR

    if lex == '+':
        value = valL + valR
    elif lex == '-':
        value = valL - valR
    elif lex == '*':
        value = valL * valR
    elif lex == '/' and valR == 0:
        fail('dividing by zero', ((lexL, tokL), lex, (lexR, tokR)))
    elif lex == '/':
        value = valL / valR
    elif lex == '^':
        value = pow(valL, valR)
    elif lex == '<':
        value = valL < valR
    elif lex == '<=':
        value = valL <= valR
    elif lex == '>':
        value = valL > valR
    elif lex == '>=':
        value = valL >= valR
    elif lex == '==':
        value = valL == valR
    elif lex == '#':
        value = valL != valR
    else:
        pass

    if isinstance(value, float):
        stack.push((str(value), "realnum"))
        to_const_table(value, "realnum")
    elif isinstance(value, bool):
        stack.push((str(value), "boolean"))
        to_const_table(value, "boolean")
    elif isinstance(value, int):
        stack.push((str(value), "intnum"))
        to_const_table(value, "intnum")


def to_const_table(val, tok):
    lexeme = str(val)
    indx1 = const_table.get(lexeme)
    if indx1 is None:
        indx = len(const_table) + 1
        const_table[lexeme] = (indx, tok, val)


def fail(str, tuple):
    if str == 'non initialized variable':
        (lx, rec) = tuple
        print('\nMGInterpreter ERROR: \n\t Value of variable {0}:{1} is undefined'.format(lx, rec))
        exit(112)
    elif str == 'dividing by zero':
        ((lexL, tokL), lex, (lexR, tokR)) = tuple
        print('\nMGInterpreter ERROR: \n\t Dividing by zero in {0} {1} {2}. '.format((lexL, tokL), lex, (lexR, tokR)))
        exit(113)
    elif str == 'wrong type':
        (lex, inpType) = tuple
        print('\n\nRunTime ERROR: \n\tType of variable is not supported.'
              '\n\tVariable {0} must be intnum or realnum.'
              '\n\tEntered type {1}'.format(lex, inpType))
        exit(114)
    elif str == 'non recognized label':
        (lex, inpType) = tuple
        print('\n\nMGInterpreter ERROR: \n\tYour label {0} is not recognized.'.format(lex, inpType))
        exit(115)


interpreter()
