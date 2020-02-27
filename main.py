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
        self.label_pb1 = QLabel("크로울링 상태", self)
        self.progressbar1 = QProgressBar(self)
        self.label_pb2 = QLabel("스크랩 상태", self)
        self.progressbar2 = QProgressBar(self)
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
        vbox.addWidget(self.label_pb1)
        vbox.addWidget(self.progressbar1)
        vbox.addWidget(self.label_pb2)
        vbox.addWidget(self.progressbar2)
        vbox.addWidget(self.output)
        self.setLayout(vbox)

        # 동작
        self.search_button.clicked.connect(self.function)
        self.search_input.editingFinished.connect(self.function)
        # 쓰레드 연동 출력
        self.tf.progress_crawl.connect(self.progressbar1.setValue)
        self.tf.progress_scrap.connect(self.progressbar2.setValue)

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
