"""
    PROJECT 2022/2023
"""
import sys
from ply import  lex


reserved = {
        'IF'     : 'IF','ELSE'      : 'ELSE',
        'WHILE'  : 'WHILE','INT'    : 'INT',
        'STR'    : 'STR','REF'      : 'REF',
        'RETURN' : 'RETURN','UNTIL' : 'UNTIL',
        'DO'     : 'DO', 'VOID'     : 'VOID'
}

# List of Tokens
tokens = [
        'NUMBER','SUM','MULT','DIV','MODULO','SUB',
        'ID',#'XOR','AND','OR','SHIFTLEFT','SHIFTRIGHT',
        'NOT','GEQ','LEQ','DIF','EQ','LESSER','GREATER',
        'CONDAND','CONDOR','ATRIB','INSEND','ARRCONT',
        'LPAREN','RPAREN','ARRINDL','ARRINDR','BLOCK_START',
        'BLOCK_END','STRING','ADDR'
] + list(reserved.values())

########### INTEGER ARITHMETIC ############
t_SUM   = r'\+';t_MULT  = r'\*'
t_DIV   = r'\/';t_MODULO = r'\%'
t_SUB   = r'\-'
########## BITWISE ##################
#t_XOR = r'\^';t_AND = r'\&'
#t_OR  = r'\|'
#t_SHIFTLEFT = r'\<\<';t_SHIFTRIGHT = r'\>\>'
########### BOOLEAN #################
t_GEQ = r'\>\=';t_LEQ = r'\<\='
t_DIF = r'\!\=';t_EQ = r'\=\='
t_LESSER  = r'\<';t_GREATER = r'\>'
t_CONDAND = r'\&\&';t_CONDOR = r'\|\|'
t_NOT = r'\!'
######### SYNTAX RELATIVE SYMBOLS ##########
t_ATRIB     = r'\:\=';t_INSEND    = r'\x3B' # ;
t_ARRCONT   = r'\x2C' # ,
t_ARRINDL   = r'\x5B' # [ Indexing arrays translates to load or store
t_ARRINDR   = r'\x5D' # ] Indexing arrays translates to load or store
t_ADDR      = r'\&'
# a[0] = 1;
# a[1] = 2;
# b = a[0];
# writei(b) -> 1
# a[20] is alloc 20


t_LPAREN    = r'\x28' # (
t_RPAREN    = r'\x29' # )
#t_BLOCK_START = r'BEGIN\n';t_BLOCK_END = r'END\n'
#t_BLOCK_START = r'\{';t_BLOCK_END = r'\}'

def t_STRING(t):
    r'\".*\"';t.type = reserved.get(t.value, 'STRING'); return t
def t_COMMENT(t):
    r'\/\*(.|\n)*?\*\/'; pass
    # Ignores everything between /* */


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value); return t

def t_BLOCK_START(t):
    r'^BEGIN|(?<=\s)BEGIN';return t
def t_BLOCK_END(t):
    r'(?<=[\s\n])END(?=\n)';return t
def t_ID(t):
    r'[A-Za-z][A-Za-z\_0-9]*';t.type = reserved.get(t.value, 'ID'); return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = '\x20\t' # Spaces and Tabs

def t_error(t):
    print(f"Illegal character {t.value[0]}")
    # t.lexer.skip(1)

lexer = lex.lex()

if __name__ == '__main__':
    with open(sys.argv[1], 'r', encoding='UTF-8') as file:
        cont = file.read()

    lexer.input(cont)
    token = lexer.token()
    while token:
        print(token)
        token = lexer.token()
