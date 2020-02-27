from PyQt5.QtCore import QThread, pyqtSignal
from saramin import writer_init, writer, get_recruit_totalPage, get_recruit_urls_from_page, saramin_scrapper
from selenium import webdriver
from pandas import read_csv

class ThreadFunction(QThread):
    progress_crawl = pyqtSignal(int)
    progress_scrap = pyqtSignal(int)
    progress_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.searchword = None

    def set_searchword(self, searchword):
        self.searchword = searchword

    def run(self):
        if self.searchword == None:
            raise AttributeError("searchword is not set.")

        # 초기화
        driver = webdriver.Chrome()
        fp, result_path = writer_init(self.searchword)
        queue = list()

        # 크로울링   
        totalPages = get_recruit_totalPage(self.searchword)
        
        for i, recruitPage in enumerate(range(1, totalPages+1)):
            queue.extend(get_recruit_urls_from_page(searchword=self.searchword, recruitPage=recruitPage))
            
            progress = int(i / totalPages * 100)
            self.progress_crawl.emit(progress)

        # 스크래핑
        totalURLs = len(queue)

        for j, url in enumerate(queue):
            contents = saramin_scrapper(url, driver)
            writer(fp, contents)

            progress = int(j / totalURLs * 100)
            self.progress_scrap.emit(progress)

        # 엑셀 파일 생성
        df = read_csv(result_path, sep='|',  encoding='ansi')
        df.to_excel(result_path.split(".")[0] + ".xlsx")

        # 종료
        driver.close()
        fp.close()

