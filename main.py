import shutil
import sys
from time import sleep
import requests
import urllib.request
import subprocess
from bs4 import BeautifulSoup as bs
from pathlib import Path

import os
import design
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QHBoxLayout)
from PyQt5.QtCore import pyqtSignal


class LCHelper(QtWidgets.QMainWindow, design.Ui_mainWindow):
    lang_list = ["cpp", "java"]
    lang_codes = dict([('cpp', 00), ('java', 1)])
    BaseRscFolder = "base_resources"
    problemTitle = ""
    problemWorkingDir = ""
    problemDescription = ""
    language = ""
    codeSnippets = dict([])
    problemFound = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.cbLanguage.addItems(self.lang_list)
        self.pbFind.clicked.connect(self.onFindButton)
        self.problemFound.connect(self.onProblemFound)
        self.pbGenerate.clicked.connect(self.onGenerateButton)
        self.pbRunIde.clicked.connect(self.startVsCode)

        self.pbGenerate.setEnabled(0)
        # self.pbRunIde.setEnabled(0)
        self.cbLanguage.setEnabled(0)

    def onFindButton(self):
        self.leProblemTitle.setEnabled(0)
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
        errors = r.get('errors', 0)
        if errors:
            return "Couldn't find problem with title: " + problemName

        soup = bs(r['data']['question']['content'], 'lxml')

        self.problemTitle = r['data']['question']['title']

        # [00]['code'] # cpp
        self.codeSnippets = r['data']['question']['codeSnippets']
        self.problemDescription = soup.get_text()
        # print(title, '\n\n', question, '\n', codeSnippets[00]['code'])
        return 0

    def onProblemFound(self):
        self.teContent.setText(self.problemDescription)
        self.pbGenerate.setEnabled(1)
        self.cbLanguage.setEnabled(1)

    def onGenerateButton(self):
        self.cbLanguage.setEnabled(0)
        self.language = self.cbLanguage.currentText()
        self.makeWorkingDir(self.language)
        self.copyBaseFiles()

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
        print("src: " + src + '\n' + "dst: " + dst)
        shutil.copytree(src, dst, dirs_exist_ok=True)
        # args = src + " " + dst
        # subprocess.run(['cp', args + ">> log.txt"],
        #                stdout=subprocess.PIPE, universal_newlines=True)


def main():
    # getProblemDescription("Intersection of Two Arrays II")
    app = QtWidgets.QApplication(sys.argv)
    window = LCHelper()
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()
