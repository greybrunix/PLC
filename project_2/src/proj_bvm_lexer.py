import ply.lex as lex
import sys


reserved = {
        'IF' : 'IF',
        'ELSE' : 'ELSE',
        'WHILE' : 'WHILE',
        'INT'   : 'INT',
        'CHAR'  : 'CHAR',
        'FLOAT' : 'FLOAT',
        'RETURN': 'RETURN'
        'GOTO'  : 'GOTO',
        'SWITCH': 'SWITCH',
        'CASE'  : 'CASE'
}

# List of Tokens
tokens = [
        'INTEGER',
        'INTARIT',
        'INTLOG',
        'REL',
        'CONDLOG',
        'ID',
        'ATRIB',
        'INSEND',
        'ARRCONT',
        'LPAREN',
        'RPAREN',
        'ARRINDL',
        'ARRINDR',
        'BLOCK_START',
        'BLOCK_END'
] + list(reserved.values())

t_INTARIT   = r'[\+\-\*\/]'
t_CONDLOG   = r'\&\&|\|\|'
t_INTLOG    = r'[\^\&\|\!]|\>\>|\<\<'
t_REL       = r'<=|>=|==|!=|<|>'
t_ATRIB     = r'\='
t_INSEND    = r'\x3B'
t_ARRCONT   = r'\x2C'
t_ARRINDL   = r'\x5B'
t_ARRINDR   = r'\x5D'
t_LPAREN    = r'\x28'
t_RPAREN    = r'\x29'
t_BLOCK_START = r'\{'
t_BLOCK_END = r'\}'


def t_COMMENT(t):
    r'\/\*(.|\n)*?\*\/'; pass
    # /* . | \n  *  ? */

def t_FLOATING(t):
    r'\d+\.\d+'
    t.value = float(t.value); return t

def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value); return t

def t_ID(t):
    r'[A-Za-z\_]+';t.type = reserved.get(t.value, 'ID'); return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = '\x20\t'

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    # t.lexer.skip(1)

lexer = lex.lex()

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as file:
        cont = file.read()

    lexer.input(cont)
    token = lexer.token()
    while token:
        print(token)
        token = lexer.token()
