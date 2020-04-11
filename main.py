#! usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QVBoxLayout, QProgressBar
from workthreads import ThreadFunction

class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        
        # 레이아웃 요소
        self.label1 = QLabel("검색", self)
        self.search_input = QLineEdit(self)
        self.search_button = QPushButton("검색", self)
        self.label_pb = QLabel("스크랩 상태", self)
        self.progressbar = QProgressBar(self)
        self.output = QTextEdit(self)

        # 쓰레드
        self.tf = ThreadFunction()

        self.initUI()

    def initUI(self):
        # 레이아웃 구성
        vbox = QVBoxLayout()
        vbox.addWidget(self.label1)
        vbox.addWidget(self.search_input)
        vbox.addWidget(self.search_button)
        vbox.addWidget(self.label_pb)
        vbox.addWidget(self.progressbar)
        vbox.addWidget(self.output)
        self.setLayout(vbox)

        # 동작
        self.search_button.clicked.connect(self.function)
        self.search_input.editingFinished.connect(self.function)
        # 쓰레드 연동 출력
        self.tf.progress_scrap.connect(self.progressbar.setValue)
        self.tf.progress_message.connect(self.output.setText)

        # 창 띄우기
        self.setWindowTitle("사람인 공고 수집기")
        self.setGeometry(300, 300, 300, 200)
        self.show()

    def function(self):
        searchword = self.search_input.text()
        self.tf.set_searchword(searchword)
        self.tf.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
