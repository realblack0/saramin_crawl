from PyQt5.QtCore import QThread, pyqtSignal
from saramin import writer_init, writer, get_recruit_totalPage, get_recruit_urls_from_page, saramin_scrapper
from selenium import webdriver
from pandas import read_csv

class ThreadFunction(QThread):
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

        # 크로울링   
        queue = list()
        totalPages = get_recruit_totalPage(self.searchword)
        self.progress_message.emit("공고 URL을 수집 중입니다.")
        
        for i, recruitPage in enumerate(range(1, totalPages+1)):
            queue.extend(get_recruit_urls_from_page(searchword=self.searchword, recruitPage=recruitPage))
            
        # 초기화
        driver = webdriver.Chrome()
        fp, result_path = writer_init(self.searchword)

        # 스크래핑
        totalURLs = len(queue)
        self.progress_message.emit(f"총 {totalURLs}개의 공고에 대하여 스크랩 중입니다.\n원격 웹브라우저를 종료하지 마세요.")

        for j, url in enumerate(queue):
            contents = saramin_scrapper(url, driver)
            writer(fp, contents)

            progress = int(j / totalURLs * 100)
            self.progress_scrap.emit(progress)

        # 엑셀 파일 생성
        df = read_csv(result_path, sep='|',  encoding='ansi')
        xlsx_result_path = result_path.split(".")[0] + ".xlsx"
        df.to_excel(xlsx_result_path)
        self.progress_message.emit(f"공고 수집이 완료되었습니다.\n{xlsx_result_path} 파일을 확인하십시오.")

        # 종료
        driver.close()
        fp.close()

