import ply.yacc as yacc
import sys
import re
import proj_nqc_lexer as lx
from proj_nqc_lexer import tokens


############## GRAMMAR #####################
# Generates the calling function of the main function
def p_program(p):
    'program : functions'
    p[0] = 'global: nop\n\tstart\n\tnop\n\tpushi 0'
    p[0] += '\n\tpusha MAIN\n\tcall\n\tnop\n\tnot\n'
    p[0] += '\tjz L0\n\tstop\nL0:\n\terr "terminated with code 1"'+p[1]
    print(p[0])

def p_functions_1(p):
    'functions :  '
    if 'MAIN' not in parser.namespace.keys():
        print(f"ERROR: Lacking a MAIN function!")
        parser.success = False
    else:
        p[0] = '\n'

def p_functions_2(p):
    'functions : function functions'
    p[0] = p[1] + p[2]

def p_function(p):
    'function : function_header function_code_outline'
    p[0] = p[1] + p[2]

def p_function_header(p):
    'function_header : data_type function_name argument_list_head'
    name = p[2]
    list = p[3]
    type = p[1]
    if (name == 'MAIN'):
        if (type != 'INT' or list != []):
            print(f'ERROR: Incorrect type for MAIN in line {p.lineno}')
            parser.success = False
        parser.namespace['MAIN'] = {'class':'funct',
                                    'arguments':[], 'return':'INT'}
    else:
        if (name in parser.namespace):
            print("ERROR: Name already used")
            parser.success = False
        try:
            parser.namespace[name] = {'class':'funct',
                              'arguments':list.split(','),'return':type}
        except AttributeError:
            parser.namespace[name] = {'class':'funct',
                              'arguments':[],'return':'p[1]'}
    p[0] = p[2] + ':\n'

def p_argument_list_head_1(p):
    'argument_list_head : LPAREN RPAREN '
    p[0] = []
def p_argument_list_head_2(p):
    'argument_list_head : LPAREN arg_head args_head RPAREN'
    p[0] = p[2] + p[3]

def p_arg_head(p):
    'arg_head : data_type ID'
    p[0] = p[1] + p[2]
def p_args_head_1(p):
    'args_head :  '
    p[0] = ''
def p_args_head_2(p):
    'args_head : ARRCONT arg_head args_head'
    p[0] = p[1] + p[2] + p[3]


def p_function_code_outline(p):
    'function_code_outline : BLOCK_START function_code BLOCK_END'
    p[0] = p[2]

def p_function_code_1(p):
    'function_code :  '
    p[0] = ''
def p_function_code_2(p):
    'function_code : declarations code_logic code_end'
    p[0] = p[1] + p[2] + p[3]

# Definition of what a declaration block can be
def p_declarations_1(p):
    'declarations :  '
    p[0] = ''
def p_declarations_2(p):
    'declarations : declaration declarations'
    p[0] = p[1] + p[2]

# Each declaration
def p_declaration_1(p):
    'declaration : data_type var_name_dec INSEND'
    index = len(namespace[curr_function]) #TODO
    p[0] = f'pushi 0\n'
def p_declaration_2(p):
    'declaration : data_type indarr_dec INSEND'
    p[0] = f'\tpushfp\n{p[2]}\n'

def p_indarr_dec(p):
    'indarr_dec : var_name_dec ARRINDL INT ARRINDR'
    #TODO
def p_code_logic(p):
    'code_logic :  '
    p[0] = ''
def p_code_logic_atr(p):
    'code_logic : atributions'
    p[0] = p[1]
def p_code_logic_cond(p):
    'code_logic : conditionals'
    p[0] = p[1]
def p_code_logic_func(p):
    'code_logic : function_calls'
    p[0] = p[1]


def p_atributions(p):
    'atributions : atribution code_logic'
    p[0] = p[1] + '\n' + p[2]
def p_atribution_1(p):
    'atribution : var_name_atr ATRIB expression INSEND'
    #TODO check if var_name_atr is defined
    if p[1] not in parser.namespace:
        print(f"ERROR: First use of Identifier in line {p.lineno}")
    p[0] = f'\tpushi {p[2]}\n\tstorel {p[1]}\n'



def p_atribution_2(p):
    'atribution : var_name_atr ATRIB conditional_expression INSEND'
    p[0] = f'{p[2]}\nstorel ' #TODO
def p_atribution_3(p):
    'atribution : indarr_atr ATRIB array INSEND'
    # Understand arrays
    p[0] = p[2]

def p_array_1(p):
    'array : BLOCK_START BLOCK_END'
    p[0] = ''
def p_array_2(p):
    'array : BLOCK_START arr_elem arr_elems BLOCK_END '
    p[0] = p[2] + p[3]

def p_arr_elem(p):
    'arr_elem : expression'
    p[0] = p[1] #TODO
def p_arr_elems(p):
    'arr_elems :  '
    P[0] = ''
def p_arr_elems_1(p):
    'arr_elems : ARRCONT arr_elem arr_elems'
    pass


def p_indarr_1(p):
    'indarr : var_name_atr ARRINDL expression ARRINDR' # Risks SEGFAULT But
    if p[1] not in parser.namespace:              # it is User responsability
        print(f"ERROR: First use of {p[1]} in line {p.lineno}")
        parser.success = False
    else:
        if (parser.namespace[p[1]]['class'] != 'var'
          or parser.namespace[p[1]]['type'] != 'int'
          or parser.namespace[p[1]]['dim'] != 1):
            print(f"ERROR: {p[1]} not array or not variable")
            parser.success = False
    if p[3] not in parser.namespace:
        print(f"ERROR: {p[3]} in line {p.lineno} not declared")
        parser.sucess = False
    else:
        if (parser.namespace[p[3]]['class'] != 'var'
          or parser.namespace[p[3]]['type'] != 'int'
          or parser.namespace[p[3]]['dim'] != 0):
            print(f"ERROR: {p[3]} in line {p.lineno} is not"
                    "a int type variable")
            parser.success = False
    p[0] = f'\tpushl {p[1]}\n\tpushl {p[1]}\n\tloadn\n'
def p_expression_1(p):
    'expression : term'
    p[0] = p[1]
def p_expression_2(p):
    'expression : expression ad_op term'
    p[0] = p[1] + p[3] + p[2]

def p_term(p):
    'term : factor'
    p[0] = p[1]
def p_term_1(p):
    'term : term mult_op factor'
    p[0] = p[1] + p[3] + p[2]
def p_factor(p):
    'factor : INTEGER'
    p[0] = f'\npushi {p[1]}\n'
def p_factor_id(p):
    'factor : ID'
    if (p[1] in namespace[curr_function]):
        p[0] = 'pushl ' + str(index(p[1]))
    else:
        parser.success = False
def p_factor_prio(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]
def p_factor_not(p):
    'factor : NOT expression'
    p[0] = p[2] + '\tnot\n'
def p_factor_sym(p):
    'factor : SUB expression'
    p[0] = f"{p[2]}\n\tpushi 2\n\tmul\n{p[2]}\n\tsub\n"
def p_factor_func(p):
    'factor : call_function'
    p[0] = p[1]
def p_factor_arr(p):
    'factor : indarr'
    p[0] = p[1]
def p_ad_op_sum(p):
    'ad_op : SUM'
    p[0] = '\tadd\n'
def p_ad_op_sub(p):
    'ad_op : SUB'
    p[0] = '\tsub\n'
#def p_ad_op_or(p):
#    'ad_op : OR'
#    pass
#def p_ad_op_xor(p):
#    'ad_op : XOR'
#    pass

def p_mult_op_1(p):
    'mult_op : MULT'
    p[0] = '\tmul\n'
def p_mult_op_2(p):
    'mult_op : DIV'
    p[0] = '\tdiv\n'
def p_mult_op_3(p):
    'mult_op : MODULO'
    p[0] = '\tmod\n'
#def p_mult_op_4(p):
    #'mult_op : AND'
    #pass
#def p_mult_op_5(p):
    #'mult_op : SHIFTRIGHT'
    #pass
#def p_mult_op_6(p):
    #'mult_op : SHIFTLEFT'
    #pass

def p_conditionals(p):
    'conditionals : conditional code_logic'
    p[0] = p[1] + p[2]

def p_conditional_while(p):
    'conditional : WHILE cond_expression cond_code'
    loop_label = 'L' + str(parser.labelcounter)
    parser.labelcounter += 1
    end_label = 'L' + str(parser.labelcounter)
    parser.labelcounter += 1
    p[0] = f'{loop_label}:\n{p[2]}\tjz {end_label}\n{p[3]}{end_label}:\n'

def p_conditional_do_while(p):
    'conditional : DO cond_code WHILE cond_expression'
    loop_label = 'L' + str(parser.labelcounter)
    parser.labelcounter += 1
    p[0] = f'{loop_label}:\n{p[2]}\t{p[4]}\tjz {loop_label}\n'

def p_conditional_if(p):
    'conditional : IF cond_expression cond_code'
    cond_label = 'L' + str(parser.labelcounter)
    parser.labelcounter += 1
    p[0] = f'{p[2]}\tjz {cond_label}\n{p[3]}{cond_label}:\n'

def p_conditional_if_else(p):
    'conditional : IF cond_expression cond_code ELSE cond_code'
    pass
def p_cond_expr(p):
    'cond_expression : LPAREN expression RPAREN'
    pass
def p_cond_expr_1(p):
    'cond_expression : LPAREN cond_expression bool_op cond_expression RPAREN'
    pass
def p_bool_op_eq(p):
    'bool_op : EQ'
    #eq
def p_bool_op_dif(p):
    'bool_op : DIF'
    #not
def p_bool_op_leq(p):
    'bool_op : LEQ'
    p[0] = '\tinfeq\n'
def p_bool_op_geq(p):
    'bool_op : GEQ'
    p[0] = '\tsupeq\n'
def p_bool_op_les(p):
    'bool_op : LESSER'
    p[0] = '\tinf\n'
def p_bool_op_gre(p):
    'bool_op : GREATER'
    p[0] = '\tsup\n'
def p_bool_op_and(p):
    'bool_op : CONDAND'
    p[0] = '\tmul\n'
def p_bool_op_or(p):
    'bool_op : CONDOR'
    p[0] = '\tadd\n'
def p_cond_code(p):
    'cond_code : BLOCK_START code_logic BLOCK_END'
    p[0] = p[2]
def p_function_calls(p):
    'function_calls : call_function code_logic'
    pass
def p_call_function(p):
    'call_function : function_name args_lst'
    pass
def p_args_lst(p):
    'args_lst : LPAREN RPAREN'
    pass
def p_args_lst_1(p):
    'args_lst : LPAREN arg args RPAREN'
    pass
def p_arg(p):
    'arg : expression'
    pass
def p_args(p):
    'args :  '
    pass
def p_args_1(p):
    'args : ARRCONT arg args'
    pass

def p_data_type(p):
    'data_type : INT'
    p[0] = p[1]

#def p_pointer(p):
#    '''
#        pointer : MULT
#                | MULT pointer
#    '''
#    pass

def p_function_name(p):
    'function_name : ID'
    p[0] = p[1]
def p_var_name_dec(p):
    'var_name_dec : ID'
    p[0] = p[1]
def p_var_name_atr(p):
    'var_name_atr : ID'
    # Verify if it's in var names (locally)
    p[0] = p[1]


def p_code_end_1(p):
    'code_end : RETURN expression INSEND'
    p[0] = p[2] + 'return\nnop\n'
    #pass
    #TODO RETHINK THIS
    #TODO IF EXPRESSION IS A VAR IT MUST BE index 0
 

def p_error(p):
    parser.success = False
    print('ERROR during parsing,\ntoken that caused error: ',p)

parser = yacc.yacc(debug=False,write_tables=False)


parser.namespace = {
        'READ' : {
            'class': 'funct',
            'arguments':[],
            'return':'CHAR*'
            },
        'WRITEI':{
            'class':'funct',
            'arguments':['INT i'],
            'return':'void'
            },
        'WRITES':{
            'class':'funct',
            'arguments':['CHAR* str'],
            'return':'void'
            },
        'INT':{'class':'data'},
        'CHAR*':{'class':'data'},
        'IF':{'class':'reserved'},
        'ELSE':{'class':'reserved'},
        'WHILE':{'class':'reserved'},
        'RETURN':{'class':'reserved'},
        'UNTIL':{'class':'reserved'},
        'DO':{'class':'reserved'}
        }

# class funct args return
# class data
# class var type dim dimmax--[10,2]
# class reserved
parser.labelcounter = 1 # main calling function has a label
parser.localvars = []
parser.currentfunc = 'MAIN'


def main():
    flag_err = False
    argc = len(sys.argv)
    if argc < 2 or argc > 4:
        flag_err = True
    if not flag_err:
        file_name = re.match(r'(.*)\.tnc', sys.argv[1])
        if (file_name):
            file_name = file_name.group(1)
            with open(sys.argv[1],'r') as f:
                cont = f.read()
            parser.success = True
            parser.parse(cont)
            if parser.success:
                print("Success")

    return flag_err;
if __name__ == '__main__':
    main()


####################### PROGRESS ################################
#
# NOTE Pointers recognized DONE DEPRECATED
# NOTE recognize function calls DONE
# NOTE recognize arrays DONE
#### NOTE Declarations of array types  NOTE indexing
# TODO convert INTEGERS code to ASSEMBLY
#### TODO translation grammar
# NOTE replaced the grammar for arrays with a more `accurate?' recursive
# form
# NOTE Added declarations for arrays and added arrays
# to expression factors
#
# NOTE RECOGNITION IS 100% DONE
# TODO ONLY TRANSLATION GRAMMAR REMAINS
#### Started progress on this
#### Trivial work need only some thought into some aspects of
#### the translation process
#
# TODO NEEDED data structures to hold each functions declared variables
# TODO global namespace (function names)
#
# dec n pode ter atribuicao
# atribuicao do array tem de ser sequencial
##### as in{12312391283,12389u1283,129831298}
##### indexar
# ARRAY BIDIMENSIONAL pode ser nome[dim1,dim2];
# nome[12][23]
# TODO whelp need to check all reserved words all local words
#### and check for arguments
######################## COMPILER FLAGS AND ARGS ##################
# flags = "-o"/"-r"
# argc size 2 to 4
# -r runs immediately
# -o compiles to a vm file with a different name at the users choice
# must be
#    python name    -> orfile.nqc -> -o newfile.vm -> -v
# or python name -> orfile.nqc -> -o newfile.vm
# or python name -> orfile.nqc -> -v
# or python name -> orfile.nqc
#
####################### REQUIREMENTS ##############################
# TODO 1) INTEGERS # NOTE PROJETO
#
# NOTE everything past this is optional and for further work
#### AKA nitpicks I'd like
# TODO 2) POINTERS OVER INTEGERS # MIGHT ease array # Not really
# TODO 3) CHARACTERS
# TODO 4) POINTERS OVER CHARACTERS
# TODO 5) FLOATS
# TODO 6) POINTERS OVER FLOATS

