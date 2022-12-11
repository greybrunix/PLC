import ply.yacc as yacc
import sys

from proj_bvm_lexer import tokens

def p_program(p):
    'program : functions'
    p[0] = 'global: nop\nstart\nnop\npusha main\ncall\nnop\nnop\nstop\n\n'+ p[1]

def p_functions_1(p):
    'functions :  '
    p[0] = '\n'

def p_functions_2(p):
    'functions : function functions'
    p[0] = p[1] + p[2]

def p_function(p):
    'function : function_header function_code_outline'
    p[0] = p[1] + p[2]
def p_function_header(p):
    'function_header : data_type function_name argument_list_head'
    p[0] = p[1] + p[2] + p[3]

def p_argument_list_head_1(p):
    'argument_list_head : LPAREN RPAREN '
    p[0] = p[1] + p[2]

def p_argument_list_head_3(p):
    'argument_list_head : LPAREN arg_head args_head RPAREN'
    pass

def p_arg_head_1(p):
    'arg_head : data_type ID'
    pass
def p_args_head_1(p):
    'args_head :  '
    pass
def p_args_head_2(p):
    'args_head : ARRCONT arg_head args_head'
    pass


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
    #TODO  check type
    p[0] = p[1] + p[2]
def p_declaration_2(p):
    'declaration : data_type indarr INSEND'
    #TODO check type
    p[0] = p[1] + p[2]
def p_declaration_3(p):
    'declaration : data_type atribution'
    #TODO check type
    p[0] = p[1] + p[2] + '\n'

# Code logic refers everything after declarations and before end of function
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
    p[0] = 'pushi ' + p[2]
def p_atribution_2(p):
    'atribution : var_name_atr ATRIB conditional_expression INSEND'
    p[0] = 'pushi ' + p[2]
def p_atribution_3(p):
    'atribution : indarr ATRIB array INSEND'
    # Understand arrays
    p[0] = p[2]
def p_atribution_4(p):
    'atribution : indarr ATRIB expression INSEND'
    #check array
    p[0] = p[2]

# Rules relative to arrays
def p_array_1(p):
    'array : BLOCK_START BLOCK_END'
    p[0] = ''
def p_array_2(p):
    'array : BLOCK_START arr_elem arr_elems BLOCK_END '
    p[0] = p[2] + p[3]

def p_arr_elem(p):
    'arr_elem : expression'
    pass
def p_arr_elems(p):
    'arr_elems :  '
    pass
def p_arr_elems_1(p):
    'arr_elems : ARRCONT arr_elem arr_elems'
    pass
def p_indarr(p):
    'indarr : ID ARRINDL INTEGER ARRINDR'
    pass
def p_indarr_1(p):
    'indarr : ID ARRINDL ID ARRINDR'
    pass

# Expression relative rules
def p_expression_1(p):
    'expression : term'
    pass
def p_expression_2(p):
    'expression : expression ad_op term'
    pass

def p_term(p):
    'term : factor'
    pass
def p_term_1(p):
    'term : term mult_op factor'
    pass
def p_factor(p):
    '''
        factor : INTEGER
               | ID
               | LPAREN expression RPAREN
               | NOT expression
               | SUB expression
               | call_function
               | indarr
    '''
    pass
def p_ad_op_sum(p):
    'ad_op : SUM'
    pass
def p_ad_op_sub(p):
    'ad_op : SUB'
    pass
def p_ad_op_or(p):
    'ad_op : OR'
    pass
def p_ad_op_xor(p):
    'ad_op : XOR'
    pass

# Multiplicative operators
def p_mult_op_1(p):
    'mult_op : MULT'
    pass
def p_mult_op_2(p):
    'mult_op : DIV'
    pass
def p_mult_op_3(p):
    'mult_op : MODULO'
    pass
def p_mult_op_4(p):
    'mult_op : AND'
    pass
def p_mult_op_5(p):
    'mult_op : SHIFTRIGHT'
    pass
def p_mult_op_6(p):
    'mult_op : SHIFTLEFT'
    pass

def p_conditionals(p):
    'conditionals : conditional code_logic'
    pass

def p_conditional_while(p):
    'conditional : WHILE conditional_expression cond_code'
    pass
def p_conditional_if(p):
    'conditional : IF conditional_expression cond_code'
    pass
def p_conditional_if_else(p):
    'conditional : IF conditional_expression cond_code ELSE cond_code'
    pass
def p_cond_expr(p):
    'conditional_expression : LPAREN expression RPAREN'
    pass
def p_cond_expr_1(p):
    'conditional_expression : LPAREN conditional_expression bool_op conditional_expression RPAREN'
    pass
def p_bool_op(p):
    '''
        bool_op : EQ
                | DIF
                | LEQ
                | GEQ
                | LESSER
                | GREATER
                | CONDAND
                | CONDOR
    '''
    pass
def p_cond_code(p):
    '''
        cond_code : BLOCK_START code_logic BLOCK_END
    '''
    pass
def p_function_calls(p):
    '''
        function_calls : call_function code_logic
    '''
    pass
def p_call_function(p):
    '''
        call_function : ID args_lst
    '''
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
    'data_type : base_type'
    pass
def p_base_type(p):
    'base_type : INT'
    pass

#def p_pointer(p):
#    '''
#        pointer : MULT
#                | MULT pointer
#    '''
#    pass

def p_function_name(p):
    'function_name : ID'
    pass
def p_var_name_dec(p):
    'var_name_dec : ID'
    pass
def p_var_name_atr(p):
    'var_name_atr : ID'
    pass
def p_code_end(p):
    'code_end : RETURN INSEND'
    pass
def p_code_end_1(p):
    'code_end : RETURN expression INSEND'
    p[0] = 'return\nnop\n'
    #pass
    #TODO RETHINK THIS


def p_error(p):
    parser.success = False
    print('ERROR during parsing,\ntoken that caused error: ',p)


if __name__ == '__main__':
    parser = yacc.yacc(debug=False,write_tables=False)
    with open(sys.argv[1],'r') as f:
        cont = f.read()
    parser.success = True
    parser.parse(cont)
    if parser.success:
        print("Success")

# NOTE Pointers recognized DONE
# NOTE recognize function calls DONE
# NOTE recognize arrays DONE
#   NOTE Declarations of array types  NOTE indexing
# TODO convert INTEGERS code to ASSEMBLY
#   TODO translation grammar
# NOTE replaced the grammar for arrays with a more `accurate?' recursive
# form
# NOTE Added declarations for arrays and added arrays
# to expression factors

# NOTE RECOGNITION IS 100% DONE
# TODO ONLY TRANSLATION GRAMMAR REMAINS


# TODO 1) INTEGERS # NOTE PROJETO
# TODO 2) POINTERS OVER INTEGERS # FACILITARIA a componente do array
# TODO 3) CHARACTERS
# TODO 4) POINTERS OVER CHARACTERS
# TODO 5) FLOATS
# TODO 6) POINTERS OVER FLOATS
