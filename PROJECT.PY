import re
import nltk
import traceback
class SymbolTable:
    def __init__(self):
        self.table = {}

    def add_symbol(self, name, type):
        if name not in self.table:
            self.table[name] = type

    def print_table(self):
        for name, type in self.table.items():
            print(f"{name} -> {type}")
class Node:
    def __init__(self, line_num, token_id, lexeme, token_type, class_type):
        self.line_num = line_num
        self.token_id = token_id
        self.lexeme = lexeme
        self.token_type = token_type
        self.class_type = class_type
        self.next = None

    def __iter__(self):
        return iter((self.line_num, self.token_id, self.lexeme, self.token_type, self.class_type))
class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
    def add_node(self, lexeme, token_type, line_number, symbol_table):
        new_node = Node(line_number, len(symbol_table.table),
                        lexeme, token_type, None)
        if self.head is None:
            self.head = new_node
        else:
            self.tail.next = new_node

        self.tail = new_node

        if token_type == "identifier":
            symbol_table.add_symbol(lexeme, "undefined")
    def print_list(self):
        current_node = self.head
        while current_node is not None:
            print(current_node.lexeme, "->", (" "), current_node.token_type,
                  (" "), "->", "Line", current_node.line_num)
            current_node = current_node.next
identifier_RE = r'\b[a-zA-Z_]\w*\b'
keyword_RE = r'\b(int|float|bool|str|ls|if|elif|else|while|for|break|continue|print|input|self|in|range|class|__init__)\b'
numerals_RE = r'\b\d+\b'
flt_numeral_RE = r'(\d+\.\d*|\.\d+|\d+e[+-]?\d+|\d+\.\d*e[+-]?\d+)'
special_characters_RE = r'[+\-*/=<>!%&|?^~:;,.(){}\[\]@#]'
token_patterns = [
    (r'\bint\b', 'keyword', 'datatype'),
    (r'\bfloat\b', 'keyword', 'datatype'),
    (r'\bbool\b', 'keyword', 'datatype'),
    (r'\bstr\b', 'keyword', 'datatype'),
    (r'\bls\b', 'keyword', 'datatype'),
    (r'\bif\b', 'keyword', None),
    (r'\belif\b', 'keyword', None),
    (r'\belse\b', 'keyword', None),
    (r'\bwhile\b', 'keyword', None),
    (r'\bfor\b', 'keyword', None),
    (r'\bbreak\b', 'keyword', None),
    (r'\bcontinue\b', 'keyword', None),
    (r'\bprint\b', 'keyword', None),
    (r'\binput\b', 'keyword', None),
    (r'\bself\b', 'keyword', None),
    (r'\bin\b', 'keyword', None),
    (r'\brange\b', 'keyword', None),
    (r'\bdef\b', 'keyword', None),
    (r'\bclass\b', 'keyword', None),
    (r'\b__init__\b', 'keyword', None),
    (identifier_RE, 'identifier', 'identifier'),
    (numerals_RE, 'numeral', 'literal'),
    (flt_numeral_RE, 'flt_numeral', 'literal'),
    (special_characters_RE, 'special_char', None),
    (r'\+', 'operator', 'operator'),
    (r'-', 'operator', 'operator'),
    (r'\*', 'operator', 'operator'),
    (r'/', 'operator', 'operator'),
    (r'=', 'assignment_operator', 'operator'),
    (r'\(', 'lparen', 'separator'),
    (r'\)', 'rparen', 'separator'),
    (r'{', 'l_brace', 'separator'),
    (r'}', 'r_brace', 'separator'),
    (r'\[', 'l_bracket', 'separator'),
    (r']', 'r_bracket', 'separator'),
    (r',', 'comma', 'separator'),
    (r'\'', 'apostrophe', 'delimiter'),
    (r'[()\[\]{}]', 'bracket', 'separator'),
    (r'\n', 'newline', 'separator'),
    (r'\s+', None, None),
    (r'.', 'invalid_char', 'invalid'),
    (r"\n", None, None),
    (r"[+\-*/=<>!%&|?^~:;,.(){}\[\]@#]", None, None),
    (r'<', 'operator', 'operator'),
    (r'>', 'operator', 'operator'),
    (r'==', 'operator', 'operator'),
    (r'<=', 'operator', 'operator'),
    (r'>=', 'operator', 'operator'),
    (r'!=', 'operator', 'operator'),
    (r'true', 'boolean', 'literal'),
    (r'false', 'boolean', 'literal'),
    (r"'(?:\\.|[^'])*'", 'string', 'literal'),
    (r'"(?:\\.|[^"])*"', 'string', 'literal'),

]
class Token:
    def __init__(self, id, value, type, class_type, line_number):
        self.id = id
        self.value = value
        self.type = type
        self.class_type = class_type
        self.line_number = line_number

    def __str__(self):
        return f"{self.value} ({self.id}, {self.value}, {self.type}, {self.class_type}, {self.line_number})"
def tokenize(code_input):
    tokens = []
    id_counter = 0
    inside_quotes = False
    quote_char = None
    quote_start = None
    symbol_table = SymbolTable()
    linked_list = LinkedList()
    for line_number, line in enumerate(code_input.split("\n"), 1):
        line = line.strip()
        if not line:
            continue
        while line:
            if inside_quotes:
                match = re.search(
                    rf"[^{quote_char}\\]+(?:\\.[^{quote_char}\\]+)*{quote_char}", line)
                if match:
                    lexeme = match.group(0)
                    id_counter += 1
                    token = Token(id_counter, lexeme,
                                  "string_literal", "literal", line_number)
                    tokens.append(token)
                    linked_list.add_node(
                        lexeme, "string_literal", line_number, symbol_table)
                    line = line[match.end():].lstrip()
                    inside_quotes = False
                    quote_char = None
                else:
                    invalid_literal = line[quote_start:]
                    print(
                        f"Invalid string literal: {invalid_literal} at line number {line_number}")
                    line = ""
            else:
                match = None
                for pattern, token_type, class_type in token_patterns:
                    match = re.match(pattern, line)
                    if match:
                        lexeme = match.group(0)
                        id_counter += 1
                        token = Token(id_counter, lexeme,
                                      token_type, class_type, line_number)
                        tokens.append(token)
                        linked_list.add_node(
                            lexeme, token_type, line_number, symbol_table)
                        symbol_table.add_symbol(lexeme, "undefined")
                        line = line[match.end():].lstrip()
                        break
                if not match:
                    invalid_char = re.match(r'\S', line)
                    if invalid_char:
                        print(
                            f"Invalid character: {invalid_char.group(0)} at line number {line_number}")
                    line = ""
                elif match.group(0) in ['"', "'"]:
                    inside_quotes = True
                    quote_char = match.group(0)
                    quote_start = len(line) - len(line.lstrip(quote_char))
    linked_list.print_list()
    print("\n")
    return tokens
c = open(r'InputProgForPythonCode.py')
code_input = c.read()
count = 0
def remove_Spaces(code_input):
    scan = []
    for line in code_input:
        if (line.strip() != ''):
            scan.append(line.strip())
    return scan

def remove_Comments(code):

    code = re.sub(r"#[^\n]*", "", code)

    code = re.sub(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'',
                  "", code, flags=re.DOTALL)
    return code
print("\n")
print("\n")
program_Comments_removed = remove_Comments(code_input)
prog = program_Comments_removed.split('\n')
scanned_Prog = remove_Spaces(prog)
scan = '\n'.join([str(elem) for elem in scanned_Prog])
scanned_Program_lines = scan.split('\n')
match_counter = 0
Source_Code = []
for line in scanned_Program_lines:
    Source_Code.append(line)
display_counter = 0
Source_Code = code_input.split("\n")
for line in Source_Code:
    count = count + 1
    print("line#", count, "\n", line)
    tokens = []
    for token in nltk.wordpunct_tokenize(line):
        if token.strip():
            tokens.append(token)
    print("Tokens are ", tokens)
    print("\n")
    code_tokens = nltk.wordpunct_tokenize(code_input)
print("All tokens are: \n", code_tokens, "\n")
tokens = tokenize(code_input)

print("\tThe output is in the order of The Tokens (Token Number, Token Class, Token Type, Line Number)\t")
print("\n")
for token in tokens:
    print("\t", str(token), end='  ')
    print('\n')

# class SyntaxAnalyzer:
#     #   Counter For Complete token_patterns
#     j = -1

#     def __init__(self, tokens):
#         self.tokens = tokens
#         self.j = -1
    
#     def PROGRAM(self):
#         if (self.BLOCK()):
#             if (token_patterns[self.j][0] == '.'):
#                 print('Syntax analysis completed successfully')
#                 return True
#             else:
#                 print('W: . required at line #'+str(token_patterns[self.j][2]))
#                 return False
#         else:
#             print('Syntax analysis failed')
#             return False

#     # TOKEN PARSER
#     def Analyse(self, code_input):
#         self.current_token = self.tokens[self.j]
#         self.BLOCK()

#     def BLOCK(self):
#         if self.current_token.value == '{':  # If a block is opened
#             self.eat('{')  # Eat the opening curly brace

#             while self.current_token.value != '}':  # while the end of the block is not reached
#                 self.STATEMENT()  # Call the STATEMENT method to handle each statement

#             self.eat('}')  # Eat the closing curly brace
#             return True

#         return False

#     def eat(self, value):
#         if self.current_token.value == value:
#             self.index += 1
#             if self.index < len(self.tokens):
#                 self.current_token = self.tokens[self.index]
#             return True
#         return False
    
#     # ----------------------------------------------------------

#     def while(self):
#         t = self.j
#         self.incJ()
#         if (token_patterns[self.j][0] == 'while'):
#             print('⌠ while LOOP START')
#             self.incJ()
#             if (token_patterns[self.j][0] == 'lparen'):
#                 if (self.EXP()):
#                     self.incJ()
#                     if (token_patterns[self.j][0] == 'rparen'):
#                         self.incJ()
#                         if (token_patterns[self.j][0] == ':'):
#                             while (self.Statement()):
#                                 self.incJ()
#                             if (token_patterns[self.j][0] == 'break'):
#                                 print('while LOOP COMPLETE ⌡')
#                                 self.incJ()
#                                 return True
#                             else:
#                                 print('W: break required at line #' +
#                                       str(token_patterns[self.j][2]))
#                                 self.j = t
#                                 return False
#                         else:
#                             print('W: : required at line #' +
#                                   str(token_patterns[self.j][2]))
#                             self.j = t
#                             return False
#                     else:
#                         print('W: ) required at line #' +
#                               str(token_patterns[self.j][2]))
#                         self.j = t
#                         return False
#                 else:
#                     print('W: ValIDENTIFIER Expression required at line #' +
#                           str(token_patterns[self.j][2]))
#                     self.j = t
#                     return False
#             else:
#                 print('W: ( required at line #'+str(token_patterns[self.j][2]))
#                 self.j = t
#                 return False
#         else:
#             self.j = t
#             return False
        
#     def PRINT(self):
#         t = self.j
#         self.incJ()
#         if (token_patterns[self.j][0] == 'PRINT'):
#             print('⌠ PRINT STATEMENT START')
#             self.incJ()
#             if (token_patterns[self.j][0] == 'lparen'):
#                 self.incJ()
#                 if (self.EXP()):
#                     self.incJ()
#                     while (token_patterns[self.j][0] == 'comma'):
#                         self.incJ()
#                         if (self.EXP()):
#                             self.incJ()
#                         else:
#                             print('P: Invalid expression at line #' +
#                                 str(token_patterns[self.j][2]))
#                             self.j = t
#                             return False
#                     if (token_patterns[self.j][0] == 'rparen'):
#                         print('PRINT STATEMENT COMPLETE ⌡')
#                         self.incJ()
#                         return True
#                     else:
#                         print('P: ) required at line #' +
#                             str(token_patterns[self.j][2]))
#                         self.j = t
#                         return False
#                 else:
#                     print('P: Expression required at line #' +
#                         str(token_patterns[self.j][2]))
#                     self.j = t
#                     return False
#             else:
#                 print('P: ( required at line #'+str(token_patterns[self.j][2]))
#                 self.j = t
#                 return False
#         else:
#             self.j = t
#             return False

#     def DEC(self):
#         t = self.j
#         self.incJ()
#         if (token_patterns[self.j][0] == 'IDENTIFIER'):
#             self.incJ()
#             for vf in token_patterns.assignmentoperator:
#                 if (token_patterns[self.j][0] == vf):
#                     if (self.ADEC()):
#                         # print('Valid IDENTIFIER Declaration')
#                         self.incJ()
#                         if (token_patterns[self.j][0] == 'SEMICOLON'):
#                             return True
#                         else:
#                             self.j = t
#                             print('; required')
#                             return False
#         self.j = t
#         return False

#     def EXP(self):
#         t = self.j
#         if (self.W()):
#             if (self.O()):
#                 if (self._E()):
#                     # print('ValIDENTIFIER Expression')
#                     return True
#                 else:
#                     self.j = t
#                     print('Incomplete Expression at line #' +
#                           str(token_patterns[self.j][0]))
#                     return False
#         self.j = t
#         return False

#     def IF(self):
#         t = self.j
#         self.incJ()
#         if (token_patterns[self.j][0] == 'IF'):
#             print('••••IF Start')
#             self.incJ()
#             if (token_patterns[self.j][0] == 'lparen'):
#                 if (self.EXP()):
#                     self.incJ()
#                     if (token_patterns[self.j][0] == 'rparen'):
#                         self.incJ()
#                         if (token_patterns[self.j][0] == 'CURLYOB'):
#                             while (self.Statement() and not token_patterns[self.j][0] == 'CURLYCB'):
#                                 None
#                             self.incJ()
#                             if (token_patterns[self.j][0] == 'CURLYCB'):
#                                 print('••••IF COMPLETE')
#                                 return True
#                             else:
#                                 print('I: } required at line # ' +
#                                       str(token_patterns[self.j][2]))
#                                 self.j = t
#                                 return False
#                         else:
#                             print('I: { required at line # ' +
#                                   str(token_patterns[self.j][2]))
#                             self.j = t
#                             return False
#                     else:
#                         print('I: ) required at line # ' +
#                               str(token_patterns[self.j][2]))
#                         self.j = t
#                         return False
#                 else:
#                     print('I: Invalid IDENTIFIER Expression at line # ' +
#                           str(token_patterns[self.j][2]))
#                     self.j = t
#                     return False
#             else:
#                 print('I: ( required at line # ' +
#                       str(token_patterns[self.j][2]))
#                 self.j = t
#                 return False
#         else:
#             self.j = t
#             return False

#     def ELSE(self):
#         t = self.j
#         self.incJ()
#         if (token_patterns[self.j][0] == 'otherwise'):
#             print('••••Otherwise Start')
#             self.incJ()
#             if (token_patterns[self.j][0] == 'CURLYOB'):
#                 while (self.Statement() and not token_patterns[self.j][0] == 'CURLYCB'):
#                     None
#                 self.incJ()
#                 if (token_patterns[self.j][0] == 'CURLYCB'):
#                     print('••••otherwise COMPLETE' +
#                           str(token_patterns[self.j][2]))
#                     return True
#                 else:
#                     # self.j=t
#                     print('E: } required at line # ' +
#                           str(token_patterns[self.j][2]))
#                     return False

#             else:
#                 print('E: { required at line # ' +
#                       str(token_patterns[self.j][2]))
#                 # self.j=t
#                 return False
#         self.j = t
#         return False

#     def Statement(self):
#         if (self.j < len(token_patterns)):
#             if (self.DEC()):
#                 print('\t►ValIDENTIFIER Declaration Complete◄')
#                 return True
#             elif (self.EXP()):
#                 print('\t♦♦♦ValIDENTIFIER Expression Complete♦♦♦')
#                 return True
#             elif (self.IF()):
#                 # print('ValIDENTIFIER IF Complete')
#                 return True
#             elif (self.ELSE()):
#                 # print('ValIDENTIFIER ELSE Complete')
#                 return True
#             elif (self.while()):
#                 # print('ValIDENTIFIER while Complete')
#                 return True
#             elif (token_patterns[self.j][0] == 'COLON' or token_patterns[self.j][0] == 'CURLYCB'):
#                 # self.j-=1
#                 return False
#             else:
#                 # self.j+=1
#                 # print('InvalIDENTIFIER Syntax at line #'+str(LexicalAnalyzer.TokenSets[self.j]))
#                 return False
#         else:

#             return False

#     def PMLIST(self):
#         t=self.j
#         self.incJ()
#         if(token_patterns[self.j][0]=='ID' or token_patterns[self.j][0]=='NUMBER' or
#            token_patterns[self.j][0]=='NUMBERF'):#Must be more options in list
#             self.incJ()
#             if(token_patterns[self.j][0]=='COMA'):
#                 if(self.PMLIST()):
#                     return True
#                 else:
#                     self.j=t
#                     print('incomplete parameter list at line #'+str(token_patterns[self.j][2]))
#                     return False
#                 return True
#             else:
#                 self.j-=1
#                 return True
#         self.j=t
#         return False
                  
#     def FUNCTION(self):
#         t=self.j
#         self.incJ()
#         if(token_patterns[self.j][0]=='DEF'):
#             print('▄▄FUNCTION DEFINATION START▄▄')
#             self.incJ()
#             if(token_patterns[self.j][0]=='ID'):
#                 self.incJ()
#                 if(token_patterns[self.j][0]=='OPENC'):
#                     self.PMLIST()
#                     self.incJ()
#                     if(token_patterns[self.j][0]=='CLOSEDC'):
#                         #print('Function )')
#                         self.incJ()
#                         if(token_patterns[self.j][0]=='CURLYOB'):
#                            # print('Function { at '+str(token_patterns[self.j][2]))
#                             while(self.Statement() #or not token_patterns[self.j][0]=='CURLYCB'
#                                   ):
#                                # if(token_patterns[self.j][0]=='CURLYCB'):
#                                  #   break
#                                 None
#                                # print('----3-----')
#                             self.incJ()
#                            # print('Now the Current State is ' +str(token_patterns[self.j][0])+ ' at '+
#                                   #str(token_patterns[self.j][2]))
#                             if(token_patterns[self.j][0]=='CURLYCB'):
#                                 #print('Function } at '+str(token_patterns[self.j][2]))
#                                 print('▀▀FUNCTION DEFINATION COMPLETE▀▀')
#                                 return True
#                             else:
#                                 print('F: } required at line # ' + str(token_patterns[self.j][2]))
#                                 return False
#                         else:
#                             print('F: { required at line # ' + str(token_patterns[self.j][2]))
#                             return False
#                     else:
#                         print('F: ) required at line # ' + str(token_patterns[self.j][2]))
#                         return False
#         self.j=t
#         return False
     
#     def FUNCTIONCALL(self):
#         t=self.j
#         self.incJ()
#         if(token_patterns[self.j][0]=='ID'):
#             self.incJ()
#             if(token_patterns[self.j][0]=='OPENC'):
#                # print('▄▄FUNCTION CALLING START▄▄')
#                 self.PMLIST()
#                 self.incJ()
#                 if(token_patterns[self.j][0]=='CLOSEDC'):
#                     self.incJ()
#                     if(token_patterns[self.j][0]=='SEMICOLON'):
#                         print('▄▄▄▄▄▄Function Called Successfully▄▄▄▄▄▄▄')
#                         return True
#                     else:
#                         print('FC: ; required at line # ' + str(token_patterns[self.j][2]))
#                         self.j=t
#                         return False
#                 else:
#                     print('FC: ) required at line # ' + str(token_patterns[self.j][2]))
#                     self.j=t
#                     return False
                
#             else:
#                 self.j=t
#                 return False
            
#         self.j=t
#         return False

#     def FOR(self):
#         t = self.j
#         self.incJ()
#         if token_patterns[self.j][0] == 'FOR':
#             print('⌠ FOR LOOP START')
#             self.incJ()
#             if token_patterns[self.j][0] == 'ID':
#                 self.incJ()
#                 if token_patterns[self.j][0] == 'IN':
#                     self.incJ()
#                     if token_patterns[self.j][0] == 'RANGE':
#                         self.incJ()
#                         if token_patterns[self.j][0] == '(':
#                             self.incJ()
#                             if self.EXP():
#                                 self.incJ()
#                                 if token_patterns[self.j][0] == ',':
#                                     self.incJ()
#                                     if self.EXP():
#                                         self.incJ()
#                                         if token_patterns[self.j][0] == ')':
#                                             self.incJ()
#                                             if token_patterns[self.j][0] == ':':
#                                                 while self.Statement():
#                                                     self.incJ()
#                                                 print('FOR LOOP COMPLETE ⌡')
#                                                 self.incJ()
#                                                 return True
#                                             else:
#                                                 print('F: : required at line #' +
#                                                     str(token_patterns[self.j][2]))
#                                                 self.j = t
#                                                 return False
#                                         else:
#                                             print('F: ) required at line #' +
#                                                 str(token_patterns[self.j][2]))
#                                             self.j = t
#                                             return False
#                                     else:
#                                         print('F: Expression required after , at line #' +
#                                             str(token_patterns[self.j][2]))
#                                         self.j = t
#                                         return False
#                                 else:
#                                     print('F: , required at line #' +
#                                         str(token_patterns[self.j][2]))
#                                     self.j = t
#                                     return False
#                             else:
#                                 print('F: Expression required before , at line #' +
#                                     str(token_patterns[self.j][2]))
#                                 self.j = t
#                                 return False
#                         else:
#                             print('F: ( required at line #' +
#                                 str(token_patterns[self.j][2]))
#                             self.j = t
#                             return False
#                     else:
#                         print('F: range() required at line #' +
#                             str(token_patterns[self.j][2]))
#                         self.j = t
#                         return False
#                 else:
#                     print('F: in keyword required at line #' +
#                         str(token_patterns[self.j][2]))
#                     self.j = t
#                     return False
#             else:
#                 print('F: Variable name required at line #' +
#                     str(token_patterns[self.j][2]))
#                 self.j = t
#                 return False
#         else:
#             self.j = t
#             return False

#     def ELIF(self):
#         t = self.j
#         self.incJ()
#         if (token_patterns[self.j][0] == 'ELIF'):
#             print('⌠ ELIF STATEMENT START')
#             self.incJ()
#             if (token_patterns[self.j][0] == 'lparen'):
#                 self.incJ()
#                 if (self.EXP()):
#                     self.incJ()
#                     if (token_patterns[self.j][0] == 'rparen'):
#                         self.incJ()
#                         if (token_patterns[self.j][0] == ':'):
#                             self.incJ()
#                             while (self.Statement()):
#                                 self.incJ()
#                             if (token_patterns[self.j][0] == 'break'):
#                                 print('ELIF STATEMENT COMPLETE ⌡')
#                                 self.incJ()
#                                 return True
#                             else:
#                                 print('E: break required at line #' +
#                                     str(token_patterns[self.j][2]))
#                                 self.j = t
#                                 return False
#                         else:
#                             print('E: : required at line #' +
#                                 str(token_patterns[self.j][2]))
#                             self.j = t
#                             return False
#                     else:
#                         print('E: ) required at line #' +
#                             str(token_patterns[self.j][2]))
#                         self.j = t
#                         return False
#                 else:
#                     print('E: Expression required at line #' +
#                         str(token_patterns[self.j][2]))
#                     self.j = t
#                     return False
#             else:
#                 print('E: ( required at line #'+str(token_patterns[self.j][2]))
#                 self.j = t
#                 return False
#         else:
#             self.j = t
#             return False

#     def CLASS_DEFINITION(self):
#         t = self.j
#         self.incJ()
#         if (token_patterns[self.j][0] == 'CLASS'):
#             print('▄▄ CLASS DEFINITION START ▄▄')
#             self.incJ()
#             if (token_patterns[self.j][0] == 'ID'):
#                 self.incJ()
#                 if (token_patterns[self.j][0] == 'COLON'):
#                     self.incJ()
#                     while (self.STATEMENT()):
#                         self.incJ()
#                     if (token_patterns[self.j][0] == 'CLASS_END'):
#                         print('▀▀ CLASS DEFINITION COMPLETE ▀▀')
#                         self.incJ()
#                         return True
#                     else:
#                         print('C: Class end marker (CLASS_END) required at line #' +
#                             str(token_patterns[self.j][2]))
#                         self.j = t
#                         return False
#                 else:
#                     print('C: : required after class name at line #' +
#                         str(token_patterns[self.j][2]))
#                     self.j = t
#                     return False
#             else:
#                 print('C: Invalid class name at line #' +
#                     str(token_patterns[self.j][2]))
#                 self.j = t
#                 return False
#         else:
#             self.j = t
#             return False

#     def CLASS_METHOD(self):
#         t = self.j
#         self.incJ()
#         if (token_patterns[self.j][0] == 'DEF'):
#             print('▄▄ CLASS METHOD DEFINITION START ▄▄')
#             self.incJ()
#             if (token_patterns[self.j][0] == 'ID'):
#                 self.incJ()
#                 if (token_patterns[self.j][0] == 'OPENC'):
#                     self.PMLIST()
#                     self.incJ()
#                     if (token_patterns[self.j][0] == 'CLOSEDC'):
#                         self.incJ()
#                         if (token_patterns[self.j][0] == 'COLON'):
#                             self.incJ()
#                             while (self.STATEMENT()):
#                                 self.incJ()
#                             if (token_patterns[self.j][0] == 'RETURN'):
#                                 self.incJ()
#                                 if (self.EXP()):
#                                     self.incJ()
#                                     if (token_patterns[self.j][0] == 'CLASS_METHOD_END'):
#                                         print('▀▀ CLASS METHOD DEFINITION COMPLETE ▀▀')
#                                         self.incJ()
#                                         return True
#                                     else:
#                                         print('CM: Class method end marker (CLASS_METHOD_END) required at line #' +
#                                             str(token_patterns[self.j][2]))
#                                         self.j = t
#                                         return False
#                                 else:
#                                     print('CM: Invalid return expression at line #' +
#                                         str(token_patterns[self.j][2]))
#                                     self.j = t
#                                     return False
#                             else:
#                                 print('CM: Return statement required at line #' +
#                                     str(token_patterns[self.j][2]))
#                                 self.j = t
#                                 return False
#                         else:
#                             print('CM: : required after class method signature at line #' +
#                                 str(token_patterns[self.j][2]))
#                             self.j = t
#                             return False
#                     else:
#                         print('CM: ) required after class method signature at line #' +
#                             str(token_patterns[self.j][2]))
#                         self.j = t
#                         return False
#                 else:
#                     print('CM: ( required after class method name at line #' +
#                         str(token_patterns[self.j][2]))
#                     self.j = t
#                     return False
#             else:
#                 print('CM: Invalid class method name at line #' +
#                     str(token_patterns[self.j][2]))
#                 self.j = t
#                 return False
#         else:
#             self.j = t
#             return False

#     def CONSTRUCTOR(self):
#         t = self.j
#         self.incJ()
#         if (token_patterns[self.j][0] == 'DEF'):
#             print('▄▄ CONSTRUCTOR DEFINITION START ▄▄')
#             self.incJ()
#             if (token_patterns[self.j][0] == 'CONSTRUCTOR'):
#                 self.incJ()
#                 if (token_patterns[self.j][0] == 'OPENC'):
#                     self.PMLIST()
#                     self.incJ()
#                     if (token_patterns[self.j][0] == 'CLOSEDC'):
#                         self.incJ()
#                         if (token_patterns[self.j][0] == 'COLON'):
#                             self.incJ()
#                             while (self.STATEMENT()):
#                                 self.incJ()
#                             if (token_patterns[self.j][0] == 'CONSTRUCTOR_END'):
#                                 print('▀▀ CONSTRUCTOR DEFINITION COMPLETE ▀▀')
#                                 self.incJ()
#                                 return True
#                             else:
#                                 print('C: Constructor end marker (CONSTRUCTOR_END) required at line #' +
#                                     str(token_patterns[self.j][2]))
#                                 self.j = t
#                                 return False
#                         else:
#                             print('C: : required after constructor signature at line #' +
#                                 str(token_patterns[self.j][2]))
#                             self.j = t
#                             return False
#                     else:
#                         print('C: ) required after constructor signature at line #' +
#                             str(token_patterns[self.j][2]))
#                         self.j = t
#                         return False
#                 else:
#                     print('C: ( required after constructor name at line #' +
#                         str(token_patterns[self.j][2]))
#                     self.j = t
#                     return False
#             else:
#                 print('C: Invalid constructor name at line #' +
#                     str(token_patterns[self.j][2]))
#                 self.j = t
#                 return False
#         else:
#             self.j = t
#             return False

#     def OBJECT_INSTANTIATION(self):
#         t = self.j
#         self.incJ()
#         if (token_patterns[self.j][0] == 'ID'):
#             print('⌠ OBJECT INSTANTIATION ⌡')
#             self.incJ()
#             if (token_patterns[self.j][0] == 'ASSIGN'):
#                 self.incJ()
#                 if (token_patterns[self.j][0] == 'NEW'):
#                     self.incJ()
#                     if (token_patterns[self.j][0] == 'ID'):
#                         self.incJ()
#                         if (token_patterns[self.j][0] == 'OPENC'):
#                             self.ARGLIST()
#                             self.incJ()
#                             if (token_patterns[self.j][0] == 'CLOSEDC'):
#                                 print('Object instantiated')
#                                 self.incJ()
#                                 return True
#                             else:
#                                 print('OI: ) required after argument list at line #' +
#                                     str(token_patterns[self.j][2]))
#                                 self.j = t
#                                 return False
#                         else:
#                             print('OI: ( required after object name at line #' +
#                                 str(token_patterns[self.j][2]))
#                             self.j = t
#                             return False
#                     else:
#                         print('OI: Invalid object name at line #' +
#                             str(token_patterns[self.j][2]))
#                         self.j = t
#                         return False
#                 else:
#                     print('OI: NEW keyword required for object instantiation at line #' +
#                         str(token_patterns[self.j][2]))
#                     self.j = t
#                     return False
#             else:
#                 print('OI: = required after object identifier at line #' +
#                     str(token_patterns[self.j][2]))
#                 self.j = t
#                 return False
#         else:
#             self.j = t
#             return False

#     def INPUT(self):
#         t = self.j
#         self.incJ()
#         if (token_patterns[self.j][0] == 'INPUT'):
#             print('⌠ INPUT STATEMENT ⌡')
#             self.incJ()
#             if (token_patterns[self.j][0] == 'OPENC'):
#                 self.incJ()
#                 if (token_patterns[self.j][0] == 'ID'):
#                     print('Variable:', token_patterns[self.j][1])
#                     self.incJ()
#                     if (token_patterns[self.j][0] == 'CLOSEDC'):
#                         self.incJ()
#                         return True
#                     else:
#                         print('IS: ) required after variable at line #' +
#                             str(token_patterns[self.j][2]))
#                         self.j = t
#                         return False
#                 else:
#                     print('IS: Invalid variable name at line #' +
#                         str(token_patterns[self.j][2]))
#                     self.j = t
#                     return False
#             else:
#                 print('IS: ( required after INPUT keyword at line #' +
#                     str(token_patterns[self.j][2]))
#                 self.j = t
#                 return False
#         else:
#             self.j = t
#             return False

# def SyntaxAndLexicalAnalysis(code_input):
#     tokens = tokenize(code_input)
#     analyzer = SyntaxAnalyzer(tokens)
#     analyzer.Analyse(code_input)
#  #  SyntaxAnalyzer.Statement(tokens)
#     Parsing(code_input,specific_functions)

# def Parsing(code_input):
#     max_iterations = 100
#     iteration = 0
#     syntax_error_found = False
#     error_tokens = set()

#     while iteration < max_iterations:
#         try:
#             compiled_code = compile(code_input, '<input>', 'exec')
#             exec(compiled_code)
#             syntax_error_found = False
#             break
#         except SyntaxError as e:
#             line_number = e.lineno
#             error_message = str(e)
#             error_token = re.search(r"([^\n]+)\n?$", error_message, re.MULTILINE)
#             if error_token:
#                 print(f"Syntax error on line {line_number}")
#                 error_tokens.add(error_token.group(1))
#             code_lines = code_input.split('\n')
#             error_line = code_lines[line_number - 1]
#             print(f"Error in code: {error_line}")
#             code_lines[line_number - 1] = ""
#             code_input = '\n'.join(code_lines)
#             syntax_error_found = True
#         except Exception as e:
#             tb_entries = traceback.extract_tb(e.__traceback__)
#             for tb_entry in tb_entries:
#                 line_number = tb_entry.lineno
#                 error_message = str(e)
#                 error_token = re.search(r"([^\n]+)\n?$", error_message, re.MULTILINE)
#                 if error_token:
#                     print(f"Error on line {line_number}: {error_token.group(1)}")
#                     error_tokens.add(error_token.group(1))
#             syntax_error_found = True
#             break

#         iteration += 1

#     if iteration == max_iterations:
#         print("Max number of iterations reached. Terminating.")

#     if not syntax_error_found and iteration < max_iterations and not error_tokens:
#         print("No syntax errors found")

                            #### new code ####

    
class SyntaxAnalyzer:
    j = -1
    token_patterns = [
        
    ]

    def __init__(self, tokens):
        self.tokens = tokens
        self.j = -1

    def PROGRAM(self):
        if self.BLOCK():
            if self.current_token and self.current_token.value == '.':
                print('Syntax analysis completed successfully')
                return True
            else:
                print('W: . required at line #' + str(self.current_token.line_number))
                return False
        else:
            print('Syntax analysis failed')
            return False

    def Analyse(self, code_input):
        self.current_token = self.tokens[self.j] if self.tokens else None
        self.PROGRAM()

    def BLOCK(self):
        if self.current_token and self.current_token.value == '{':
            self.eat('{')

            while self.current_token and self.current_token.value != '}':
                if not self.STATEMENT():
                    return False

            self.eat('}')
            return True

        return False

    def STATEMENT(self):
        # Add your statement parsing logic here
        return True

    def eat(self, value):
        if self.current_token and self.current_token.value == value:
            self.j += 1
            if self.j < len(self.tokens):
                self.current_token = self.tokens[self.j]
            else:
                self.current_token = None
            return True
        return False


def tokenize(code_input):
    # Tokenize code_input
    # ...
    return tokens


def SyntaxAndLexicalAnalysis(code_input):
    tokens = tokenize(code_input)
    analyzer = SyntaxAnalyzer(tokens)
    analyzer.Analyse(code_input)


specific_functions = {
    
    "while": """\
def while(self):
    if self.current_token and self.current_token.value == 'while':
        print('⌠ while LOOP START')
        self.eat('while')
        if self.current_token and self.current_token.value == '(':
            self.eat('(')
            if self.EXP():
                self.eat(')')
                if self.current_token and self.current_token.value == ':':
                    self.eat(':')
                    while self.STATEMENT():
                        pass
                    if self.current_token and self.current_token.value == 'break':
                        print('while LOOP COMPLETE ⌡')
                        self.eat('break')
                        return True
                    else:
                        print('W: break required at line #' + str(self.current_token.line_number))
                        return False
                else:
                    print('W: : required at line #' + str(self.current_token.line_number))
                    return False
            else:
                print('W: Expression required at line #' + str(self.current_token.line_number))
                return False
        else:
            print('W: ( required at line #' + str(self.current_token.line_number))
            return False
    else:
        return False"""
}



def Parsing(code_input, specific_functions):
    code_lines = code_input.split('\n')

    for line in code_lines:
        line_matched = False

        for function_name, function_syntax in specific_functions.items():
            if function_syntax.strip() == line.strip():
                line_matched = True
                break

        if not line_matched:
            print(f"Error: Line does not match the syntax of any specific function: {line}")

    print("Parsing complete")




#Parsing(code_input, specific_functions)
with open(r'InputProgForPythonCode.py') as f:
    code_input = f.read()
    SyntaxAndLexicalAnalysis(code_input)
    Parsing(code_input, specific_functions)
