from libs.pyparsing import *
from base64 import b64decode
import pprint

def verifyLen(t):
    t = t[0]
    if t.len is not None:
        t1len = len(t[1])
        if t1len != t.len:
            raise ParseFatalException, \
                  "invalid data of length %d, expected %s" % (t1len, t.len)
    return t[1]


# define punctuation literals
LPAR, RPAR, LBRK, RBRK, LBRC, RBRC, VBAR = map(Suppress, "()[]{}|")
decimal = Word("123456789", nums).setParseAction(lambda t: int(t[0]))
bytes = Word(printables)
raw = Group(decimal.setResultsName("len") + Suppress(":") + bytes).setParseAction(verifyLen)

token = Word(alphanums + "-./_:$*+=")

base64_ = Group(Optional(decimal, default=None).setResultsName("len") + VBAR 
                + OneOrMore(Word( alphanums +"+/=" )).setParseAction(lambda t: b64decode("".join(t)))
                + VBAR).setParseAction(verifyLen)

hexadecimal = ("#" + OneOrMore(Word(hexnums)) + "#").setParseAction(lambda t: int("".join(t[1:-1]),16))
oneSidedString = (Suppress(Literal("'")) + OneOrMore(token)) ##.setParseAction(lambda truncate: "".join(truncate[1:]))
qString = Group(Optional(decimal, default=None).setResultsName("len") + dblQuotedString.setParseAction(removeQuotes)).setParseAction(verifyLen)

simpleString = raw | token | base64_ | hexadecimal | oneSidedString | qString 


display = LBRK + simpleString + RBRK
string_ = Optional(display) + simpleString

sexp = Forward()
sexpList = Group(LPAR + ZeroOrMore(sexp) + RPAR)
sexp << ( string_ | sexpList )

def parse_file(file):
    f_handle = open(file, 'r')
    f_text = f_handle.read()
    sexpr = sexp.parseString(f_text)
    return sexpr

def parse(string):
    sexpr = sexp.parseString(string)
    return sexpr
