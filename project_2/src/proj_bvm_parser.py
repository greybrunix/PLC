
import ply.yacc as yacc
import sys

from proj_bvm_lexer import tokens




def p_program(p):
    'program : functions'
    pass

def p_functions_1(p):
    'functions :  '
    pass
def p_functions_2(p):
    'functions : function functions'
    pass

def p_function(p):
    'function : function_header function_code_outline'
    pass
def p_function_header(p):
    'function_header : data_type ID argument_list_head'
    pass

def p_argument_list_head_1(p):
    'argument_list_head : LPAREN RPAREN '
    pass
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
    pass
def p_function_code_1(p):
    'function_code :  '
    pass
def p_function_code_2(p):
    'function_code : declarations code_logic code_end'
    pass
def p_declarations_1(p):
    'declarations :  '
    pass
def p_declarations_2(p):
    'declarations : declaration declarations'
    pass
def p_declaration_1(p):
    'declaration : data_type ID INSEND'
    pass
def p_declaration_2(p):
    'declaration : data_type atribution'
    pass
def p_code_logic(p):
    '''
        code_logic :  
        code_logic : atributions
        code_logic : conditionals
        code_logic : function_calls
    '''
    pass
def p_atributions(p):
    'atributions : atribution code_logic'
    pass
def p_atribution_1(p):
    'atribution : ID ATRIB expression INSEND'
    pass
def p_atribution_2(p):
    'atribution : ID ATRIB bool_expression INSEND'
    pass
def p_expression_1(p):
    'expression : term'
    pass
def p_expression_2(p):
    'expression : expression ad_op term'
    pass 

def p_term(p):
    '''
        term : factor
             | term mult_op factor
    '''
    pass
def p_factor(p):
    '''
        factor : INTEGER
               | ID
               | LPAREN expression RPAREN
               | NOT expression
               | SUB expression 
    '''                  # TODO double check not and sub
    pass
def p_ad_op(p):
    '''
        ad_op : ADD
              | SUB
              | LOGOR
              | BITOR
    '''
    pass
def p_mult_op(p):
    '''
        mult_op : MULT
                | DIVINT
                | MOD
                | LOGAND
                | BITAND
                | SHIFTR
                | SHIFTL
    '''
    pass


def p_data_type(p):
    ''' 
        data_type : base_type
                  | base_type pointer
    '''
    pass
def p_base_type(p):
    '''
        base_type : INT
                  | FLOAT
                  | CHAR
    '''
    pass
def p_pointer(p):
    '''
        pointer : MULT
                | MULT pointer
    '''
    pass

def p_error(p):
    parser.success = False
    print('ERROR during parsing,\ntoken that caused error: ',p)


if __name__ == '__main__':
    parser = yacc.yacc()
    with open(sys.argv[1],'r') as f:
        cont = f.read()
    parser.success = True
    parser.parse(cont)
    if parser.success:
        print("Success")

# NOTE Pointers done


# TODO 1) INTEGERS # PROJETO
# TODO 2) POINTERS OVER INTEGERS # FACILITA a componente do array
# TODO 3) CHARACTERS
# TODO 4) POINTERS OVER CHARACTERS
# TODO 5) FLOATS
# TODO 6) POINTERS OVER FLOATS

"""
void swap(float *x, float * y)
{
    float * tmp = *y;
    *y = *x;
    *x = *tmp;
}
"""
