import os
import re


class CppGenerator():
    CMAKE_FILENAME = "CMakeLists.txt"
    SRC_FILE = "main.cpp"
    DUMMY_DESCRIPTION = '// DUMMY_DESCRIPTION'
    DUMMY_SNIPPET = '// DUMMY_SNIPPET'
    DUMMY_TESTS = '// DUMMY_TESTS'

    def __init__(self, workDir, problemDescription, codeSnippet):
        self.workDir = workDir
        self.code = codeSnippet
        self.description = problemDescription

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

        with open(mainFile, 'w') as file:
            file.write(filedata)
