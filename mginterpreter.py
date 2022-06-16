from mglexer import symb_table, var_table, const_table, label_table, source_code
from mgparser import parser, postfix_code
from mgstack import Stack

stack = Stack()
stack.print()
to_view = True


def interpreter():
    if parser():
        global stack, postfix_code

        max_numb = len(postfix_code)
        try:
            for i in range(0, max_numb):
                lex, tok = postfix_code.pop(0)
                if tok in ('intnum', 'realnum', 'id'):
                    stack.push((lex, tok))
                else:
                    do_it(lex, tok)

                if to_view:
                    print_config(i + 1, lex, tok, max_numb)

            print('\nMGInterpreter: Interpreting ended successfully!')
            return True
        except SystemExit as e:
            print('\nMGInterpreter: Crash program with code {0}'.format(e))
        return True


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
    elif tok in ('add_op', 'mult_op', 'degree_op'):
        (lexR, tokR) = stack.pop()
        (lexL, tokL) = stack.pop()
        proc_add_mult_deg((lexL, tokL), lex, (lexR, tokR))
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
    else:
        pass
    stack.push((str(value), tokL))
    to_const_table(value, tokL)


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


def print_tables(table):
    if table == "Symbol":
        print_symb_table()
    elif table == "Id":
        print_var_table()
    elif table == "Const":
        print_const_table()
    elif table == "Label":
        print_label_table()
    else:
        print_symb_table()
        print_var_table()
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
        print(s2.format(numRec, numLine, lexeme, token, str(index) ))


def print_var_table():
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
        print("\n Table of labels - empty")
    else:
        s1 = '{0:<10s} {1:<10s} '
        print("\n Table of labels")
        print(s1.format("Label", "Value"))
        s2 = '{0:<10s} {1:<10d} '
        for lbl in label_table:
            val = label_table[lbl]
            print(s2.format(lbl, val))


interpreter()
