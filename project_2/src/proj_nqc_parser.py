import ply.yacc as yacc
import sys
import subprocess
import re
import proj_nqc_lexer as lx
from proj_nqc_lexer import tokens


#################### GRAMMAR ######################
###################################################


###################################################
###################### AXIOM ######################
# The axiom 'program' generates the function that calls main
def p_program(p):
    'program : functions'
    p[0] = 'calling: nop\n\tstart\n\tnop\n\tpushi 0'
    p[0] += '\n\tpusha MAIN\n\tcall\n\tnop\n\tnot\n'
    p[0] += '\tjz L0\n\tnop\n\tstop\nL0:\n\tpushs "Exited with code "'\
            +'\n\twrites\n\twritei\n\t\pushs "\\n"\n\twrites\n\tstop\n'+p[1]
    if parser.success:
        parser.result += p[0]

def p_functions_1(p):
    'functions :  '
    if 'MAIN' not in parser.namespace.keys():
        print(f"ERROR: Lacking a MAIN function!")
        parser.success = False
    if parser.result:
        p[0] = '\n'

def p_functions_2(p):
    'functions : function functions'
    if parser.result:
        p[0] = p[1] + p[2]

def p_function(p):
    'function : function_header function_code_outline'
    if parser.result:
        p[0] = p[1] + p[2]

def p_function_header(p):
    'function_header : func_type ID argument_list_head'
    name = p[2]
    args = p[3]
    r_type = p[1]
    if (name == 'MAIN'):
        if (r_type != 'INT' or args != []):
            print(f'ERROR: Incorrect type for MAIN in line {p.lineno}')
            parser.success = False
        if parser.success:
            parser.namespace['MAIN'] = {'class':'funct',
                                    'arguments':[], 'return':'INT'}
    else:
        if (name in parser.namespace):
            print("ERROR: Name already used")
            parser.success = False
        if parser.success:
            try:
                parser.namespace[name] = {'class':'funct',
                                  'arguments':args.split(','),'return':r_type}
            except AttributeError:
                parser.namespace[name] = {'class':'funct',
                                  'arguments':[],'return':'p[1]'}
    if parser.success:
        parser.currentfunc = name;
        p[0] = p[2] + ':\n\tnop\n'

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
        p[0] = p[1] + p[2]
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
    'function_code : declarations code_logic code_end'
    if parser.success:
        p[0] = p[1] + p[2] + p[3]

# Definition of what a declaration block can be
def p_declarations_1(p):
    'declarations :  '
    if parser.success:
        p[0] = ''
def p_declarations_2(p):
    'declarations : declaration declarations'
    if parser.success:
        p[0] = p[1] + p[2]

# Each declaration
def p_declaration_1(p):
    'declaration : data_type ID INSEND'
    if (p[2] in parser.namespace):
        print(f"ERROR(ln {p.lineno}): Name already in use!")
    if parser.success:
        # TODO add the new system for namespace
        p[0] = f'pushi 0\n'

def p_declaration_2(p):
    'declaration : INT ID ARRINDL INTEGER ARRINDR INSEND'
    if (p[2] in parser.namespace):
        print(f"ERROR(ln {p.lineno}): Name already in use!")
        parser.success = False
    if parser.success:
        # TODO add the new system for namespace
        p[0] = f'\tpushfp\npushi {ind}\n\tpadd\n\tpushn {p[4]}\n'


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
    'code_logic : function_calls'
    if parser.success:
        p[0] = p[1]


def p_atributions(p):
    'atributions : atribution code_logic'
    p[0] = p[1] + '\n' + p[2]
def p_atribution_1(p):
    'atribution : ID ATRIB expression INSEND'
    #TODO check if var_name_atr is defined
    if p[1] not in parser.namespace:
        print(f"ERROR(ln {p.lineno}): Attribution without declaration.")
        parser.success = False
    if parser.success:
        p[0] = f'\tpushi {p[3]}\n\tstorel {p[1]}\n'



def p_atribution_2(p):
    'atribution : ID ATRIB cond_expression INSEND'
    p[0] = f'{p[3]}\nstorel {index}' #TODO
def p_atribution_3(p):
    'atribution : indarr ATRIB expression INSEND'
    # Understand arrays
    #p[0] = p[2]

def p_indarr_1(p):
    'indarr : ID ARRINDL expression ARRINDR' # Risks SEGFAULT But
    if p[1] not in parser.namespace:              # it is User responsability
        print(f"ERROR(ln {p.lineno}): Attribution without declaration.")
        parser.success = False
    if parser.success:
        if (parser.namespace[p[1]]['class'] != 'var'
          or parser.namespace[p[1]]['type'] != 'int'
          or parser.namespace[p[1]]['dim'] != 1):
            print(f"ERROR(ln {p.lineno}): Malformed indexing.")
            parser.success = False
        else:
            p[0] = f'\tpushl {p[1]}\n\t{p[3]}\n\tloadn\n'
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
        #TODO i was here 188
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

def p_conditional_until(p):
    'conditional : UNTIL cond_expression cond_code'
    loop_label = 'L' + str(parser.labelcounter)
    parser.labelcounter += 1
    end_label = 'L' + str(parser.labelcounter)
    parser.labelcounter += 1
    p[0] = f'{loop_label}:\n{p[2]}\tjz {end_label}\n{p[3]}{end_label}:\n'

def p_conditional_do_until(p):
    'conditional : DO cond_code UNTIL cond_expression'
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
    else_label = 'L' + str(parser.labelcounter)
    parser.labelcounter += 1
    end_label = 'L' + str(parser.labelcounter)
    parser.labelcounter += 1
    p[0] = f'{p[2]}\tjz {else_label}\n{p[3]}\tjump {end_label}\n'
    p[0]+= f'{else_label}:\n{p[5]}\t{end_label}:\n'
def p_cond_expr(p):
    'cond_expression : LPAREN expression RPAREN'
    pass
def p_cond_expr_1(p):
    'cond_expression : LPAREN cond_expression bool_op cond_expression RPAREN'
    pass
def p_bool_op_eq(p):
    'bool_op : EQ'
    p[0] = f'\tdup 2\n\tinfeq\n\tsupeq\n\tmul\n'
def p_bool_op_dif(p):
    'bool_op : DIF'
    p[0] = f'\tdup 2\n\tinf\n\tsup\n\tadd\n'
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
    'call_function : ID args_lst'
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

def p_func_type_1(p):
    'func_type : VOID'
    p[0] = p[1]

def p_func_type_2(p):
    'func_type : data_type'
    p[0] = p[1]

def p_data_type(p):
    'data_type : STR'
    p[0] = p[1]
def p_data_type_1(p):
    'data_type : INT'
    p[0] = p[1]
def p_data_type_2(p):
    'data_type : INT pointer'
    p[0] = p[1] + p[2]

def p_pointer_1(p):
    'pointer : MULT'
    p[0] = p[1] # NOTE THESE TWO RETURN FOR TYPE
def p_pointer_rec(p):
    'pointer : MULT pointer'
    p[0] = p[1] + p[2]

def p_code_end_v(p):
    'code_end : RETURN INSEND' # Needs to check if curr_func is void
    if parser.namespace[currentfunc]['return'] == 'void':
        p[0] = f'\treturn\n\tnop\n'
    else:
        parser.success = False

def p_code_end_1(p):
    'code_end : RETURN expression INSEND' #NOTE no validations here
    p[0] = f'{p[2]}\tstorel {index}\n\treturn\nnop\n'


def p_error(p):
    parser.success = False
    print('ERROR: Could not parse this file.\n')




################### MAIN FUNCTION ##############################
################################################################
def main():
    parser = yacc.yacc()


    parser.namespace = {
       # '__FUNCTION_NAME_NO_ONE_WILL_EVER_USE__':{
       #     'class':'funct',
       #     'arguments':[], # Contains a list of the arguments
       #     'return':'VOID' # Contains the type to be returned
       #     # IF VOID THE RETURN MUST BE 'RETURN;'
       # }, # Exemplify functions
       # '__VAR_NAME_NO_ONE_CAN_USE__':{
       #     'class':'var', # self explanatory
       #     'address':'0', # the address is the offset to %EBP
       #     'type':'__TYPE_NO_ONE_WILL_EVER_USE__', # self explanatory
       #     'dim': '0', # 0 int, 1 array, 2 bidimarray
       #     'dimmax':'0,0', # might be removed 
       #     'scope':'__FUNCTION_NAME_NO_ONE_WILL_EVER_USE__'
       #     }, # this serves only to exemplify declared variables
       # '__TYPE_NO_ONE_WILL_EVER_USE__':{
       #     # data and reserved only have one field as they don't require
       #     # any other information, maybe data would require words
       #     # but that info is wasted on the VM
       #     'class':'data'
       #     #'class':'reserved
       # }, # Exemplify Types and Reserved words
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
        'INT':{'class':'data'},
        'STR':{'class':'data'},
        'IF':{'class':'reserved'},
        'ELSE':{'class':'reserved'},
        'WHILE':{'class':'reserved'},
        'RETURN':{'class':'reserved'},
        'UNTIL':{'class':'reserved'},
        'DO':{'class':'reserved'}
    }
    parser.labelcounter = 1 # main calling function has a label
    parser.currentfunc  = 'MAIN'
    parser.result       = ''
    parser.success      = True
    flag_err            = False
    argc                = len(sys.argv)
    flag_run = False # Flag for Runnnig the Virtual Machine upon compilation
    # NOTE Only works on linux as it requires vms installed and in an
    # accepted location (or in PATH) but it still generates a vm code file
    flag_name = False
    if argc >= 2:
        name = re.match(r'(.*)\.nqc', sys.argv[1])
        if name:
            name = name.group(1) + '.vm'
        else:
            flag_err = True
    else:
        flag_err = True

    if not flag_err and argc == 3:
        if sys.argv[3] == '-r':
            flag_run = True
    else:
        flag_err = True

    if not flag_err and argc > 3:
        if sys.argv[3] == '-o':
            if argc >= 4:
                new_name = re.match(r'(.*\.vm)',sys.argv[3])
                new_name = new_name.group(1)
                flag_name = True
            else:
                flag_err = True
            if not flag_err:
                if argc == 5:
                    if sys.argv[-1] == '-r':
                        flag_run = True
                    else:
                        flag_err = True

    if not flag_err:
        with open(sys.argv[1],'r') as f:
            cont = f.read()
        res = parser.parse(cont)
        if parser.success:
            if (flag_name):
                with open(new_name, 'w+') as nf:
                    nf.write(res)
            else:
                with open(name, 'w+') as nf:
                    nf.write(res)
            print("Code Generated")
            if (flag_run):
                try:
                    if flag_name:
                        subprocess.run(["vms "+new_name], check=True)
                    else:
                        subprocess.run(["vms "+name], check=True)
                except subprocess.CalledProcessError:
                    print("""Please install the Virtual Machine, VM.
                            Then move vms to PATH.""")
            print("Success")
        else:
            print("Fail")

    return flag_err;


if __name__ == '__main__':
    main()


####################### PROGRESS ################################
#################################################################
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
##################### DISREGARD PREVIOUS IDEAS ############
# NOTE One single namespace for the ID table which contains the
# scope for each variable, see UNION FOR ID TABLE section
#
# NOTE dec n pode ter atribuicao
# atribuicao do array tem de ser sequencial
# ATRIBUICAO TEM DE SER POR INDEXACAO INDIVIDUAL
# AKA a[1] = 0;
##### indexar
# ARRAY BIDIMENSIONAL pode ser nome[dim1,dim2];
# nome[12][23]
#
# NOTE REFACTORED ARRAY RECOGNITION
#
# TODO ERROR MESSAGES AND VALIDATE IF ERRORS ARENT PROPAGATED
#
############################ NOTES ################################
###################################################################
#
###################################################################
######################## UNION FOR ID TABLE #######################
# class funct args return
# class data
# class var type dim dimmax--[10,2] scope
# class reserved
###################################################################
######################## COMPILER FLAGS AND ARGS ##################
# flags = "-o"/"-r"
# argc size 2 to 4
# -r runs immediately (ONLY WORKS ON UBUNTU LINUX X86-64)
# -o compiles to a vm file with a different name at the users choice
# must be
#    python name    -> orfile.nqc -> -o newfile.vm -> -v
# or python name -> orfile.nqc -> -o newfile.vm
# or python name -> orfile.nqc -> -v
# or python name -> orfile.nqc
#
###################################################################
####################### REQUIREMENTS ##############################
###################################################################
# TODO 1) INTEGERS # NOTE PROJETO
#
# NOTE everything past this is optional and for further work
#### AKA nitpicks I'd like
# TODO 2) POINTERS OVER INTEGERS # MIGHT ease array # It doesn't but makes
# the solution consistent with itself
# TODO 3) CHARACTERS
# TODO 4) POINTERS OVER CHARACTERS
# TODO 5) FLOATS
# TODO 6) POINTERS OVER FLOATS

