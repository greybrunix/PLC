#! /bin/python3
"""
    PROJECT
"""
import sys
import re
from ply import yacc
from lexer import tokens

def p_program(p):
    'program : functions'
    if parser.success:
        p[0] = p[1]
        parser.result = 'calling: nop\n\tstart\n\tnop\n\tpushi 0'
        parser.result += '\n\tpusha MAIN\n\tcall\n\tnop\n\tdup 1\n\tnot\n'
        parser.result += '\tjz L0\n\tnop\n\tpop 1\n\tstop\nL0:\n\tpushs "Exited with code "'
        parser.result += '\n\twrites\n\twritei\n\tpushs "\\n"\n\twrites\n\tstop\n'+p[0]
def p_functions_1(p):
    'functions :  '
    if parser.success:
        if 'MAIN' not in parser.namespace.keys():
            print(f"ERROR: Lacking a MAIN function!",
                    file=sys.stderr)
            parser.success = False
        if parser.success:
            p[0] = '\n'

def p_functions_2(p):
    'functions : function functions'
    if parser.success:
        p[0] = p[1] + p[2]

def p_function(p):
    'function : function_header function_code_outline'
    if parser.success:
        p[0] = p[1] + p[2]

def p_function_header(p):
    'function_header : func_type ID argument_list_head'
    parser.currentfunc = p[2]
    if parser.success:
        name = p[2]
        args = p[3]
        r_type = p[1]
        if name == 'MAIN':
            if (r_type != 'INT' or args != []):
                print('ERROR: Incorrect type for MAIN',
                       file=sys.stderr)
                parser.success = False
            if parser.success:
                parser.namespace['MAIN'] = {'class':'funct',
                                    'arguments':[], 'return':'INT'}
                parser.namespace['MAIN1'] = {'class':'var',
                                         'address' : '-1',
                                         'type'    : 'INT',
                                         'size'    : '0',
                                         'scope'   : 'MAIN'}
        else:
            if name in parser.namespace:
                print("ERROR: Name already used",
                       file=sys.stderr)
                parser.success = False
            if parser.success:
                try:
                    parser.namespace[name] = {'class':'funct',
                                  'arguments':args.split(','),'return':r_type}
                    for elem in args.split(','):
                        stuff = elem.split(' ')
                        data = ' '.join(stuff[:-1])
                        var_name = stuff[-1]
                        parser.argnum -= 1
                        parser.namespace.update({var_name : {
                            'class'   : 'var',
                            'address' : str(parser.argnum),
                            'type'    : data,
                            'size'     : '0',
                            'scope'   : parser.currentfunc,
                        }})
                except AttributeError:
                    parser.namespace[name] = {'class':'funct',
                                  'arguments':[],'return':r_type}
                if r_type != 'VOID':
                    parser.namespace[name+'1'] = {'class' : 'var',
                                'address' : parser.argnum-1,
                                'type'    : r_type,
                                'size'   : '0',
                                'scope'  : parser.currentfunc
                    }
        if parser.success:
            parser.argnum = 0
            parser.varnum = 0
            p[0] = name + ':\n\tnop\n'

def p_argument_list_head_1(p):
    'argument_list_head : LPAREN RPAREN '
    if parser.success:
        p[0] = []
def p_argument_list_head_2(p):
    'argument_list_head : LPAREN arg_head args_head RPAREN'
    if parser.success:
        p[0] = p[2] + p[3]

def p_arg_head(p):
    'arg_head : data_type ID'
    if parser.success:
        name = p[2]
        data = p[1]
        if name in parser.namespace:
            if parser.namespace[name]['class'] != 'var':
                parser.success = False
        if parser.success:
            p[0] = data + ' ' + name
def p_args_head_1(p):
    'args_head :  '
    if parser.success:
        p[0] = ''
def p_args_head_2(p):
    'args_head : ARRCONT arg_head args_head'
    if parser.success:
        p[0] = p[1] + p[2] + p[3]


def p_function_code_outline(p):
    'function_code_outline : BLOCK_START function_code BLOCK_END'
    if parser.success:
        p[0] = p[2]

def p_function_code_1(p):
    'function_code :  '
    if parser.success:
        p[0] = ''
def p_function_code_2(p):
    'function_code : declarations code_logic'
    if parser.success:
        if parser.varnum:
            p[0] = p[1] + p[2] + f'\tpop {parser.varnum}\n\treturn\n\tnop\n'
        else:
            p[0] = p[1] + p[2] + '\treturn\n\tnop\n'


def p_declarations_1(p):
    'declarations :  '
    if parser.success:
        p[0] = ''
def p_declarations_2(p):
    'declarations : declaration declarations'
    if parser.success:
        p[0] = p[1] + p[2]


def p_declaration_1(p):
    'declaration : data_type ID COMP'
    if parser.success:
        name = p[2]
        data = p[1]
        if name in parser.namespace:
            if parser.namespace[name]['class'] == 'var':
                if parser.namespace[name]['scope'] == parser.currentfunc:
                    print("ERROR: Name already in use!",
                            file=sys.stderr)
                    parser.success = False
            else:
                print("ERROR: Name already in use!",
                        file=sys.stderr)
                parser.success = False
    if parser.success:
        ind = parser.varnum
        parser.varnum += 1
        parser.namespace.update({name: {
                'class'  : 'var',
                'address': str(ind),
                'type'   : data,
                'size'   : '0',
                'scope'  : parser.currentfunc
        }})
        if data == 'REF INT':
            p[0] = '\tpushgp\n\tpushi 99999\n\tpadd\n'
        else: p[0] = '\tpushi 0\n'

def p_declaration_2(p):
    'declaration : data_type ID ARRINDL NUMBER ARRINDR COMP'
    if parser.success:
        name = p[2]
        data = p[1]
        const = p[4]
        if data != 'INT':
            print("Arrays should be INT",
                    file=sys.stderr)
            parser.success = False
        if name in parser.namespace:
            if parser.namespace[name]['class'] == 'var':
                if parser.namespace[name]['scope'] == parser.currentfunc:
                    print("ERROR: Name already in use!",
                            file=sys.stderr)
                    parser.success = False
            else:
                print("ERROR: Name already in use!",
                        file=sys.stderr)
                parser.success = False
    if parser.success:
        ind = parser.varnum
        parser.varnum += 1 + const
        parser.namespace[name] = {
                'class' : 'var',
                'address': str(ind),
                'type'   : 'REF ' + data,
                'size'   : str(const),
                'scope'  : parser.currentfunc
        }
        p[0] = f'\tpushfp\n\tpushi {ind+1}\n\tpadd\n\tpushn {const}\n'
def p_declaration_bin_arr(p):
    'declaration : data_type ID ARRINDL NUMBER ARRCONT NUMBER ARRINDR COMP'
    if parser.success:
        row = p[4]
        col = p[6]
        total_size = int(row) * int(col)
        data = p[1]
        name = p[2]
        res = ''
        if data != 'INT':
            print("ERROR: Array must be of Integers",
                    file=sys.stderr)
            parser.success = False
        else:
            if name in parser.namespace:
                if parser.namespace[name]['class'] == 'var':
                    if parser.namespace[name]['scope'] == parser.currentfunc:
                        print("ERROR: Name already in use!",
                                file=sys.stderr)
                        parser.success = False
                else:
                    print("ERROR: Name already in use!",
                            file=sys.stderr)
                    parser.success = False
    if parser.success:
        ind = parser.varnum
        parser.varnum += row+total_size
        parser.namespace[name] = {
                'class' : 'var',
                'address' : str(ind),
                'type' : 'REF REF ' + data,
                'size' : str(total_size),
                'scope' : parser.currentfunc
                }
        for i in range(0,int(row)):
            res += f'\tpushfp\n\tpushi {ind+i}\n\tpadd\n\tpushi {col}\n\tpushi {i}\n\tadd\n\tpadd\n'
        p[0] = res + f'\tpushn {total_size}\n'


def p_code_logic(p):
    'code_logic :  '
    if parser.success:
        p[0] = ''
def p_code_logic_atr(p):
    'code_logic : atributions'
    if parser.success:
        p[0] = p[1]
def p_code_logic_cond(p):
    'code_logic : conditionals'
    if parser.success:
        p[0] = p[1]
def p_code_logic_func(p):
    'code_logic : call_functions'
    if parser.success:
        p[0] = p[1]


def p_atributions(p):
    'atributions : atribution code_logic'
    if parser.success:
        p[0] = p[1] + p[2]

def p_atribution_str(p):
    'atribution : ID ATRIB STRING COMP'
    if parser.success:
        name = p[1]
        string = p[3]
        if name in parser.namespace:
            if parser.namespace[name]['class'] == 'var':
                if parser.namespace[name]['scope'] != parser.currentfunc:
                    print("ERROR: Not declared!",
                            file=sys.stderr)
                    parser.success = False
                elif parser.namespace[name]['type'] != 'STR':
                    print("ERROR: Not a string",
                            file=sys.stderr)
            else:
                if name != parser.currentfunc:
                    print("ERROR: Not a variable!",
                            file=sys.stderr)
                    parser.success = False
                else:
                    if parser.namespace[name]['return'] != 'STR':
                        print("ERROR: Wrong type",
                                file=sys.stderr)
                        parser.success = False
                    if parser.namespace[name]['return'] == 'VOID':
                        print("ERROR: Assigning value to void function",
                                file=sys.stderr)
                        parser.success = False
        else:
            print("ERROR: Not declared!",
                    file=sys.stderr)
            parser.success = False
        if parser.success:
            if name == parser.currentfunc:
                address = parser.namespace[name+'1']['address']
            else: address = parser.namespace[name]['address']
            p[0] = f'\tpushs {p[3]}\n\tstorel {address}\n'
def p_atribution_1(p):
    'atribution : ID ATRIB expression COMP'
    if parser.success:
        name = p[1]
        if name in parser.namespace:
            if parser.namespace[name]['class'] == 'var':
                if parser.namespace[name]['scope'] != parser.currentfunc:
                    print("ERROR: Not Declared!",
                           file=sys.stderr)
                    parser.success = False
                elif parser.namespace[name]['type'] == 'STR':
                    print("ERROR: A String cannot be an expression",
                            file=sys.stderr)
                    parser.success=False
            else:
                if name != parser.currentfunc:
                    print("ERROR: Not a variable!",
                           file=sys.stderr)
                    parser.success = False
                else:
                    if parser.namespace[name]['return'] == 'STR':
                        print("ERROR: Mismatch type",
                                file=sys.stderr)
                        parser.success = False
                    elif parser.namespace[name]['return'] == 'VOID':
                        print("ERROR: Assigning value to void function",
                               file=sys.stderr)
                        parser.success = False
        else:
            print("ERROR: Not declared!",
                   file=sys.stderr)
            parser.success = False
    if parser.success:
        if name == parser.currentfunc:
            address = parser.namespace[name+'1']['address']
        else: address = parser.namespace[name]['address']
        p[0] = f'{p[3]}\tstorel {address}\n'
def p_atribution_deref(p):
    'atribution : DEREF ID ATRIB expression COMP'
    if parser.success:
        name = p[2]
        if name in parser.namespace:
            if parser.namespace[name]['class'] == 'var':
                if parser.namespace[name]['type'] != 'REF INT':
                    print("ERROR: Dereferencing value")
                    parser.success = False
                if parser.namespace[name]['scope'] != parser.currentfunc:
                    print(f"ERROR: {p[1]} Not Declared!")
                    parser.success = False
            else:
                print(f"ERROR: {p[1]} Not a variable!")
                parser.success = False
        else:
            parser.success = False
        if parser.success:
            address = parser.namespace[name]['address']
            p[0] = f'\tpushl {address}\n{p[4]}\tstore 0\n'

def p_atribution_3(p):
    'atribution : ID ARRINDL expression ARRINDR ATRIB expression COMP'
    if parser.success:
        name = p[1]
        ind = p[3]
        atrib_expr = p[6]
        if name not in parser.namespace:
            print("ERROR: Atribution without declaration.",
                    file=sys.stderr)
            parser.success = False
    if parser.success:
        if (parser.namespace[name]['class'] != 'var'
                or parser.namespace[name]['type'] != 'REF INT'):
            print("ERROR: Malformed indexing.",
                    file=sys.stderr)
            parser.success = False
        else:
            index = parser.namespace[name]['address']
            p[0] = f'\tpushl {index}\n{ind}{atrib_expr}\tstoren\n'
def p_atribution_4(p):
    'atribution : ID ARRINDL expression ARRCONT expression ARRINDR ATRIB expression COMP'
    if parser.success:
        name = p[1]
        row = p[3]
        col = p[5]
        atrib_expr = p[8]
        if name not in parser.namespace:
            print("ERROR: Atribution without declaration",
                    file=sys.stderr)
            parser.success = False
        if parser.success:
            if (parser.namespace[name]['class'] != 'var'
                    or parser.namespace[name]['type'] != 'REF REF INT'):
                print("ERROR: Malformed indexing.", file=sys.stderr)
                parser.success = False
            else:
                index = parser.namespace[name]['address']
                p[0] = f'\tpushl {index}\n{col}\tpadd\n{row}{atrib_expr}\tstoren\n'
def p_indarr_1(p):
    'indarr : ID ARRINDL expression ARRINDR'
    if parser.success:
        name = p[1]
        const = p[3]
        if name not in parser.namespace:
            print(f"ERROR: Indexing without declaration.",
                    file=sys.stderr)
            parser.success = False
    if parser.success:
        if (parser.namespace[name]['class'] != 'var'
            or parser.namespace[name]['type'] != 'REF INT'):
            print(f"ERROR: Malformed indexing.",
                    file=sys.stderr)
            parser.success = False
        else:
            index = parser.namespace[name]['address']
            p[0] = f'\tpushl {index}\n{const}\tloadn\n'
def p_indmat_2(p):
    'indmat : ID ARRINDL expression ARRCONT expression ARRINDR'
    if parser.success:
        name = p[1]
        if name not in parser.namespace:
            print("ERROR: Indexing without declaration.",
                    file=sys.stderr)
            parser.success = False
    if parser.success:
        if (parser.namespace[name]['class'] != 'var'
            or parser.namespace[name]['type'] != 'REF REF INT'):
            print("ERROR: Malformed indexing.")
            parser.success = False
        else:
            index = parser.namespace[name]['address']
            p[0] = f'\tpushl {index}\n{p[3]}\tpadd\n\t{p[4]}\tloadn\n'


def p_expression_1(p):
    'expression : term'
    if parser.success:
        p[0] = p[1]
def p_expression_2(p):
    'expression : expression ad_op term'
    if parser.success:
        p[0] = p[1] + p[3] + p[2]

def p_term(p):
    'term : factor'
    if parser.success:
        p[0] = p[1]
def p_term_1(p):
    'term : term mult_op factor'
    if parser.success:
        p[0] = p[1] + p[3] + p[2]
def p_factor(p):
    'factor : NUMBER'
    if parser.success:
        p[0] = f'\tpushi {p[1]}\n'
def p_factor_id(p):
    'factor : ID'
    if parser.success:
        name = p[1]
        if name in parser.namespace:
            if parser.namespace[name]['class'] == 'var':
                if parser.namespace[name]['scope'] != parser.currentfunc:
                    print("ERROR: Not Declared!",
                           file=sys.stderr)
                    parser.success = False
            else:
                if (name == parser.currentfunc and
                    parser.namespace[name]['return'] == 'VOID'):
                    print("ERROR: Accessing value of void function!",
                            file=sys.stderr)
                    parser.success = False
        else:
            if name != 'NIL' :
                print("ERROR: Not Declared!", file=sys.stderr)
                parser.success = False
    if parser.success:
        flag = False
        if name == 'NIL':
            flag = True
        if name == parser.currentfunc:
            address = parser.namespace[name+'1']['address']
        else:
            address = parser.namespace[name]['address']
        if flag:
            p[0] = '\tpushi 99999\n'
        else:
            p[0] = f'\tpushl {address}\n'
def p_factor_prio(p):
    'factor : LPAREN cond_expression RPAREN'
    if parser.success:
        p[0] = p[2]
def p_factor_not(p):
    'factor : NOT expression'
    if parser.success:
        p[0] = p[2] + '\tnot\n'
def p_factor_sym(p):
    'factor : SUB expression'
    if parser.success:
        p[0] = f"\tpushi 0\n{p[2]}\tsub\n"
def p_factor_func(p):
    'factor : call_function'
    if parser.success:
        p[0] = p[1]
def p_factor_arr(p):
    'factor : indarr'
    if parser.success:
        p[0] = p[1]
def p_factor_mat(p):
    'factor : indmat'
    if parser.success:
        p[0] = p[1]
def p_factor_address(p):
    'factor : ADDR ID'
    if parser.success:
        name = p[2]
        if name in parser.namespace:
            if parser.namespace[name]['class'] == 'var':
                if parser.namespace[name]['scope'] != parser.currentfunc:
                    print("ERROR: Not Declared!",
                            file=sys.stderr)
                    parser.success = False
            else:
                print("ERROR: Not a variable!",
                        file=sys.stderr)
                parser.success = False
    if parser.success:
        address = parser.namespace[name]['address']
        p[0] = f'\tpushfp\n\tpushi {address}\n\tpadd\n'
def p_factor_addrarr(p):
    'factor : ADDR ID ARRINDL expression ARRINDR'
    if parser.success:
        name = p[2]
        const = p[4]
        if name not in parser.namespace:
            print(f"ERROR: Indexing without declaration.",
                    file=sys.stderr)
            parser.success = False
    if parser.success:
        if (parser.namespace[name]['class'] != 'var'
            or parser.namespace[name]['type'] != 'REF INT'):
            print(f"ERROR: Malformed indexing.",
                    file=sys.stderr)
            parser.success = False
        else:
            index = parser.namespace[name]['address']
            p[0] = f'\tpushl {index}\n{const}\tpadd\n'
def p_facto_addrmat(p):
    'factor : ADDR ID ARRINDL expression ARRCONT expression ARRINDR'
    if parser.success:
        name = p[2]
        if name not in parser.namespace:
            print("ERROR: Indexing without declaration.",
                    file=sys.stderr)
            parser.success = False
    if parser.success:
        if (parser.namespace[name]['class'] != 'var'
            or parser.namespace[name]['type'] != 'REF REF INT'):
            print("ERROR: Malformed indexing.")
            parser.success = False
        else:
            index = parser.namespace[name]['address']
            p[0] = f'\tpushl {index}\n{p[4]}\tpadd\n\t{p[6]}\tpadd\n'
def p_factor_dereference(p):
    'factor : DEREF ID'
    if parser.success:
        name = p[2]
        if name in parser.namespace:
            if parser.namespace[name]['class'] == 'var':
                if parser.namespace[name]['type'] != 'REF INT':
                    print("ERROR: Derefencing value!",
                            file=sys.stderr)
                    parser.success = False
                if parser.namespace[name]['scope'] != parser.currentfunc:
                    print("ERROR: Not Declared!",
                            file=sys.stderr)
                    parser.success = False
            else:
                print("ERROR: Not a variable!",
                        file=sys.stderr)
                parser.success = False
    if parser.success:
        address = parser.namespace[name]['address']
        p[0] = f'\tpushl {address}\n\tload 0\n'

def p_ad_op_sum(p):
    'ad_op : SUM'
    if parser.success:
        p[0] = '\tadd\n'
def p_ad_op_sub(p):
    'ad_op : SUB'
    if parser.success:
        p[0] = '\tsub\n'

def p_mult_op_1(p):
    'mult_op : MULT'
    if parser.success:
        p[0] = '\tmul\n'
def p_mult_op_2(p):
    'mult_op : DIV'
    if parser.success:
        p[0] = '\tdiv\n'
def p_mult_op_3(p):
    'mult_op : MODULO'
    if parser.success:
        p[0] = '\tmod\n'

def p_conditionals(p):
    'conditionals : conditional code_logic'
    if parser.success:
        p[0] = p[1] + p[2]

def p_conditional_while(p):
    'conditional : WHILE cond_expression cond_code'
    if parser.success:
        loop_label = 'L' + str(parser.labelcounter)
        parser.labelcounter += 1
        end_label = 'L' + str(parser.labelcounter)
        parser.labelcounter += 1
        p[0] = f'{loop_label}:\n{p[2]}\tjz {end_label}\n{p[3]}\tjump {loop_label}\n{end_label}:\n'

def p_conditional_do_while(p):
    'conditional : DO cond_code WHILE cond_expression'
    if parser.success:
        loop_label = 'L' + str(parser.labelcounter)
        parser.labelcounter += 1
        p[0] = f'{loop_label}:\n{p[2]}\t{p[4]}\tjz {loop_label}\n'

def p_conditional_until(p):
    'conditional : UNTIL cond_expression cond_code'
    if parser.success:
        loop_label = 'L' + str(parser.labelcounter)
        parser.labelcounter += 1
        end_label = 'L' + str(parser.labelcounter)
        parser.labelcounter += 1
        p[0] = f'{loop_label}:\n{p[2]}\tnot\n\tjz {end_label}\n{p[3]}\tjump {loop_label}\n{end_label}:\n'

def p_conditional_do_until(p):
    'conditional : DO cond_code UNTIL cond_expression'
    if parser.success:
        loop_label = 'L' + str(parser.labelcounter)
        parser.labelcounter += 1
        p[0] = f'{loop_label}:\n{p[2]}\t{p[4]}\tnot\n\tjz {loop_label}\n'

def p_conditional_if(p):
    'conditional : IF cond_expression cond_code'
    if parser.success:
        cond_label = 'L' + str(parser.labelcounter)
        parser.labelcounter += 1
        p[0] = f'{p[2]}\tjz {cond_label}\n{p[3]}{cond_label}:\n'

def p_conditional_if_else(p):
    'conditional : IF cond_expression cond_code ELSE cond_code'
    if parser.success:
        else_label = 'L' + str(parser.labelcounter)
        parser.labelcounter += 1
        end_label = 'L' + str(parser.labelcounter)
        parser.labelcounter += 1
        p[0] = f'{p[2]}\tjz {else_label}\n{p[3]}\tjump {end_label}\n'
        p[0]+= f'{else_label}:\n{p[5]}{end_label}:\n'
def p_cond_expr(p):
    'cond_expression : expression'
    if parser.success:
        p[0] = p[1]
def p_cond_expr_1(p):
    'cond_expression : cond_expression bool_op expression'
    if parser.success:
        p[0] = p[1] + p[3] + p[2]
def p_bool_op_eq(p):
    'bool_op : EQ'
    if parser.success:
        p[0] = '\tequal\n'
def p_bool_op_dif(p):
    'bool_op : DIF'
    if parser.success:
        p[0] = '\tequal\n\tnot\n'
def p_bool_op_leq(p):
    'bool_op : LEQ'
    if parser.success:
        p[0] = '\tinfeq\n'
def p_bool_op_geq(p):
    'bool_op : GEQ'
    if parser.success:
        p[0] = '\tsupeq\n'
def p_bool_op_les(p):
    'bool_op : LESSER'
    if parser.success:
        p[0] = '\tinf\n'
def p_bool_op_gre(p):
    'bool_op : GREATER'
    if parser.success:
        p[0] = '\tsup\n'
def p_bool_op_and(p):
    'bool_op : CONDAND'
    if parser.success:
        p[0] = '\tand\n'
def p_bool_op_or(p):
    'bool_op : CONDOR'
    if parser.success:
        p[0] = '\tor\n'
def p_cond_code(p):
    'cond_code : BLOCK_START code_logic BLOCK_END'
    if parser.success:
        p[0] = p[2]
def p_call_functions(p):
    'call_functions : call_function COMP code_logic'
    if parser.success:
        p[0] = p[1] + p[3]
def p_call_function(p):
    'call_function : ID args_lst'
    if parser.success:
        name = p[1]
        args = p[2]
        if name not in parser.namespace:
            print("ERROR: Function not declared before use",
                    file=sys.stderr)
            parser.success = False
        if parser.success:
            if parser.namespace[name]['class'] != 'funct':
                print("ERROR: not a function",
                        file=sys.stderr)
                parser.success = False
            else:
                if len(parser.namespace[name]['arguments']) != len(args):
                    print("ERROR: incorrect length of arguments",
                            file=sys.stderr)
                    parser.success = False
    if parser.success:
        if parser.namespace[name]['return'] == 'VOID':
            res = ''
            for arg in args[::-1]:
                res += f'{arg}'
        else:
            res = '\tpushi 0\n'
            for arg in args[::-1]:
                res += f'{arg}'
        p[0] = res + f'\tpusha {name}\n\tcall\n\tpop {len(args)}\n'
def p_call_read(p):
    'call_function : READ LPAREN RPAREN'
    if parser.success:
        p[0] = '\tread\n'
def p_call_writes(p):
    'call_function : WRITES LPAREN STRING RPAREN'
    if parser.success:
        p[0] = f'\tpushs {p[3]}\n\twrites\n'
def p_call_writesid(p):
    'call_function : WRITES LPAREN ID RPAREN'
    if parser.success:
        name = p[3]
        if name in parser.namespace:
            if parser.namespace[name]['class'] == 'var':
                if parser.namespace[name]['scope'] != parser.currentfunc:
                    print("ERROR: Not Declared!",
                           file=sys.stderr)
                    parser.success = False
                elif parser.namespace[name]['type'] != 'STR':
                    print("ERROR: Not a string variable",
                            file=sys.stderr)
                    parser.success = False
            else:
                print("ERROR: Not a valid variable!",
                        file=sys.stderr)
                parser.success = False
        else:
            print("ERROR: Not declared!",
                    file=sys.stderr)
            parser.success = False
    if parser.success:
        address = parser.namespace[name]['address']
        p[0] = f'\tpushl {address}\n\twrites\n'
def p_call_writeread(p):
    'call_function : WRITES LPAREN READ LPAREN RPAREN RPAREN'
    if parser.success:
        p[0] = '\tread\n\twrites\n'
def p_call_writeint(p):
    'call_function : WRITEI LPAREN expression RPAREN'
    if parser.success:
        p[0] = f'{p[3]}\twritei\n'
def p_call_atoi(p):
    'call_function : ATOI LPAREN STRING RPAREN'
    if parser.success:
        p[0] = f'\tpushs {p[3]}\n\tatoi\n'
def p_call_atoi_1(p):
    'call_function : ATOI LPAREN ID RPAREN'
    if parser.success:
        name = p[3]
        if name in parser.namespace:
            if parser.namespace[name]['class'] == 'var':
                if parser.namespace[name]['scope'] != parser.currentfunc:
                    print("ERROR: Not Declared!",
                           file=sys.stderr)
                    parser.success = False
                elif parser.namespace[name]['type'] != 'STR':
                    print("ERROR: Not a string variable",
                            file=sys.stderr)
                    parser.success = False
            else:
                print("ERROR: Not a valid variable!",
                        file=sys.stderr)
                parser.success = False
        else:
            print("ERROR: Not declared!",
                    file=sys.stderr)
            parser.success = False
    if parser.success:
        address = parser.namespace[name]['address']
        p[0] = f'\tpushl {address}\n\twrites\n'
def p_call_atoi_2(p):
    'call_function : ATOI LPAREN READ LPAREN RPAREN RPAREN'
    if parser.success:
        p[0] = '\tread\n\tatoi\n'

def p_args_lst(p):
    'args_lst : LPAREN RPAREN'
    if parser.success:
        p[0] = []
def p_args_lst_1(p):
    'args_lst : LPAREN expression args RPAREN'
    if parser.success:
        p[0] = [p[2]] + p[3]
def p_args(p):
    'args :  '
    if parser.success:
        p[0] = []
def p_args_1(p):
    'args : ARRCONT expression args'
    if parser.success:
        p[0] = [p[2]] + p[3]

def p_func_type_1(p):
    'func_type : VOID'
    if parser.success:
        p[0] = p[1]

def p_func_type_2(p):
    'func_type : data_type'
    if parser.success:
        p[0] = p[1]

def p_data_type(p):
    'data_type : STR'
    if parser.success:
        p[0] = p[1]
def p_data_type_1(p):
    'data_type : INT'
    if parser.success:
        p[0] = p[1]
def p_data_type_2(p):
    'data_type : pointer data_type'
    if parser.success:
        p[0] = p[1] + ' ' + p[2]

def p_pointer_1(p):
    'pointer : REF'
    if parser.success:
        p[0] = p[1]
def p_pointer_2(p):
    'pointer : REF REF'
    if parser.success:
        p[0] = p[1] + ' ' + p[2]


def p_error(p):
    parser.success = False
    print(f'ERROR: Could not parse this file.\n{p.lineno}\n{p}',
            file=sys.stderr)
def main():
    parser.namespace = {
        'READ' : {
            'class': 'funct',
            'arguments':[],
            'return':'STR'
            },
        'WRITEI':{
            'class':'funct',
            'arguments':['INT i'],
            'return':'VOID'
            },
        'WRITES':{
            'class':'funct',
            'arguments':['STR str'],
            'return':'VOID'
            },
        'ATOI':{
            'class':'funct',
            'arguments':['STR str'],
            'return':'INT'
            },
        'INT':{'class':'data'},
        'STR':{'class':'data'},
        'IF':{'class':'reserved'},
        'ELSE':{'class':'reserved'},
        'WHILE':{'class':'reserved'},
        'RETURN':{'class':'reserved'},
        'UNTIL':{'class':'reserved'},
        'DO':{'class':'reserved'}
    }
    parser.labelcounter = 1
    parser.currentfunc  = ''
    parser.varnum       = 0
    parser.argnum       = 0
    parser.result       = ''
    parser.success      = True
    flag_err            = False
    argc                = len(sys.argv)
    flag_name = False
    if argc >= 2:
        name = re.search(r'([A-Za-z\_0-9]+)\.nqc', sys.argv[1])
        if not name:
            print("ERROR: not a nqc file",
                    file=sys.stderr)
            flag_err = True
    else:
        print("ERROR: Not enough arguments",
                file=sys.stderr)
        flag_err = True

    if not flag_err and argc > 3:
        if sys.argv[2] == '-o':
            if argc >= 4:
                new_name = re.match(r'(.*\.vm)',sys.argv[3])
                new_name = new_name.group(1)
                flag_name = True
            else:
                print("ERROR: Missing new name",
                        file=sys.stderr)
                flag_err = True

    if not flag_err:
        with open(sys.argv[1],'r',encoding='UTF-8') as f:
            cont = f.read()
        parser.parse(cont)
        res = str(parser.result)
        if parser.success:
            if flag_name:
                with open(new_name, 'w+', encoding='UTF-8') as nf:
                    nf.write(res)
            else:
                print(res)
            print("Code Generated",file=sys.stderr)
        else:
            print("Error generating code",file=sys.stderr)
    return flag_err

parser = yacc.yacc(debug=0)
sys.exit(main())

