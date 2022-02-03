from ast import arg
import os
import re
import string


class CppGenerator():
    CMAKE_FILENAME = "CMakeLists.txt"
    SRC_FILE = "main.cpp"
    DUMMY_DESCRIPTION = '// DUMMY_DESCRIPTION'
    DUMMY_SNIPPET = '// DUMMY_SNIPPET'
    DUMMY_TESTS = '// DUMMY_TESTS'
    ASSERT_TEMPALTE = "assert((VAR1) == (VAR2));"
    CLASS_INSTANCE = 'solution'
    parameterTypes = dict()

    def __init__(self, workDir, problemDescription, codeSnippet):
        self.workDir = workDir
        self.code = codeSnippet
        self.description = problemDescription
        self.getRetTypesAndParams()

    def generate(self):
        try:
            self.setCmakeProjectName()
            self.configureMain()
            return True
        except:
            return False

    def setCmakeProjectName(self):
        cmakeFile = self.workDir + '/' + self.CMAKE_FILENAME
        name = "project (" + self.workDir.split("/")[-1] + ")"
        with open(cmakeFile, 'r') as file:
            filedata = file.read()

        filedata = re.sub(r'project \(.*\)', name, filedata, 1)
        with open(cmakeFile, 'w') as file:
            file.write(filedata)

    def configureMain(self):
        mainFile = self.workDir + '/' + self.SRC_FILE
        with open(mainFile, 'r') as file:
            filedata = file.read()
        # problem description
        filedata = filedata.replace(self.DUMMY_DESCRIPTION, self.description)
        # codeSnippet
        filedata = filedata.replace(self.DUMMY_SNIPPET, self.code)
        # examples  & asserts
        assertionBlock = "Solution " + self.CLASS_INSTANCE+";\n"
        assertionBlock += self.asserts
        filedata = filedata.replace(self.DUMMY_TESTS, assertionBlock)
        with open(mainFile, 'w') as file:
            file.write(filedata)

    def getRetTypesAndParams(self):
        code = self.code
        opBrck = code.find('(')
        clBrck = code.find(')')
        brackets = code[opBrck+1:clBrck]
        for argPair in brackets.split(','):
            argPair = argPair.strip().replace('&', '').split(' ')
            self.parameterTypes[argPair[1]] = argPair[0]

        typeFin = code.rfind(' ', 0, opBrck)
        typeStrt = code.rfind(' ', 0, typeFin)
        self.fooName = code[typeFin:opBrck].strip()
        self.returnType = code[typeStrt:typeFin].strip()
        if 'void' in self.returnType:
            self.returnType = 'auto'

    def parseExamples(self, examples):
        result = ''
        for example in examples:
            result += '\n{\n'
            example.replace(' ', '')
            splited = example.split('\n')
            for row in splited:
                if 'Input:' in row:
                    row = row.replace('Input:', '')
                    for arg in row.split(', '):
                        argType = self.parameterTypes.get(
                            arg.split('=')[0].strip(), 'auto')
                        if argType == 'auto':
                            print("ERROOOORROOO")
                        result += argType + ' ' +\
                            arg.replace('[', '{').replace(']', '}')
                        result += ';\n'
                elif 'Output:' in row:
                    row = row.replace('Output:', '')
                    result += self.returnType + ' result = ' + \
                        row.replace('[', '{').replace(']', '}')
                    result += ';\n'
                else:
                    continue
            fooBrackets = ''
            for k, v, in self.parameterTypes.items():
                fooBrackets += k + ','
            fooBrackets = fooBrackets[0:-1]
            result += self.ASSERT_TEMPALTE.replace('VAR1', 'result').replace(
                'VAR2', self.CLASS_INSTANCE + '.' + self.fooName + '('+fooBrackets+')')
            result += '\n}'
        self.asserts = result
