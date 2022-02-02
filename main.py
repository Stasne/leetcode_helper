import shutil
import sys
import requests
import subprocess
from bs4 import BeautifulSoup as bs
from pathlib import Path

import os
import design
import cpp_gen as gen_cpp
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QHBoxLayout)
from PyQt5.QtCore import pyqtSignal


class LCHelper(QtWidgets.QMainWindow, design.Ui_mainWindow):
    lang_list = ["cpp", "java"]
    lang_codes = dict([('cpp', 00), ('java', 1)])
    BaseRscFolder = "base_resources"

    problemFound = pyqtSignal()
    generated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.cbLanguage.addItems(self.lang_list)
        self.pbFind.clicked.connect(self.onFindButton)
        self.problemFound.connect(self.onProblemFound)
        self.pbGenerate.clicked.connect(self.onGenerateButton)
        self.generated.connect(self.onGenerated)
        self.pbRunIde.clicked.connect(self.startVsCode)

        self.pbGenerate.setEnabled(False)
        self.pbRunIde.setEnabled(False)
        self.cbLanguage.setEnabled(False)

    def onFindButton(self):
        self.leProblemTitle.setEnabled(False)
        self.setStatus(". . . . . . . . . . . . . . . . . .")
        title = self.leProblemTitle.text()
        err = self.getProblemDescription(title)
        if err:
            self.setStatus(err)
            return self.leProblemTitle.setEnabled(1)

        self.setStatus("Successfully found")
        self.problemFound.emit()

    def getProblemDescription(self, problemName):
        problemName = problemName.replace(' ', '-')
        data = {"operationName": "questionData", "variables": {"titleSlug": problemName}, "query": "query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    boundTopicId\n    title\n    titleSlug\n    content\n    translatedTitle\n    translatedContent\n    isPaidOnly\n    difficulty\n    likes\n    dislikes\n    isLiked\n    similarQuestions\n    contributors {\n      username\n      profileUrl\n      avatarUrl\n      __typename\n    }\n    langToValidPlayground\n    topicTags {\n      name\n      slug\n      translatedName\n      __typename\n    }\n    companyTagStats\n    codeSnippets {\n      lang\n      langSlug\n      code\n      __typename\n    }\n    stats\n    hints\n    solution {\n      id\n      canSeeDetail\n      __typename\n    }\n    status\n    sampleTestCase\n    metaData\n    judgerAvailable\n    judgeType\n    mysqlSchemas\n    enableRunCode\n    enableTestMode\n    envInfo\n    libraryUrl\n    __typename\n  }\n}\n"}
        r = requests.post('https://leetcode.com/graphql', json=data).json()
        errors = r.get('errors', False)
        if errors:
            return "Couldn't find problem with title: " + problemName

        soup = bs(r['data']['question']['content'], 'lxml')

        self.problemTitle = r['data']['question']['title']
        self.codeSnippets = r['data']['question']['codeSnippets']
        self.problemDescription = soup.get_text()
        return False

    def onProblemFound(self):
        self.teContent.setText(self.problemDescription)
        self.pbGenerate.setEnabled(True)
        self.cbLanguage.setEnabled(True)

    def onGenerateButton(self):
        self.cbLanguage.setEnabled(False)
        self.language = self.cbLanguage.currentText()
        self.makeWorkingDir(self.language)
        self.copyBaseFiles()
        includeDescription = self.cbDescription.isChecked()
        if includeDescription == False:
            self.problemDescription = ''

        snippet = self.codeSnippets[self.lang_codes[self.language]]['code']
        generator = gen_cpp.CppGenerator(
            self.problemWorkingDir, self.problemDescription, snippet)
        success = generator.generate()
        if success != True:
            return self.setStatus("Something went wrong")
        self.generated.emit()

    def onGenerated(self):
        self.pbRunIde.setEnabled(True)

    def makeWorkingDir(self, language):
        self.problemWorkingDir = "Projects/" + language + '/' + \
            self.problemTitle.replace(' ', '_').lower()
        Path(self.problemWorkingDir).mkdir(parents=True, exist_ok=True)

    def setStatus(self, msg):
        self.lblStatus.setText(msg)

    def startVsCode(self):
        subprocess.run(['code', './' + self.problemWorkingDir],
                       stdout=subprocess.PIPE, universal_newlines=True)

    def copyBaseFiles(self):
        src = self.BaseRscFolder + '/' + self.language
        dst = self.problemWorkingDir
        shutil.copytree(src, dst, dirs_exist_ok=True)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = LCHelper()
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()
