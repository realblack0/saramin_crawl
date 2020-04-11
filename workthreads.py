#! usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QThread, pyqtSignal
from saramin import writer_init, writer, get_recruit_totalPage, get_recruit_urls_from_page, saramin_scrapper
from selenium import webdriver
from pandas import read_csv
import os

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
        driver = webdriver.Chrome(os.path.abspath("./chromedriver"))
        fp, result_path = writer_init(self.searchword)

        # 스크래핑
        totalURLs = len(queue)
        self.progress_message.emit("총 {totalURLs}개의 공고에 대하여 스크랩 중입니다.\n원격 웹브라우저를 종료하지 마세요.".format(totalURLs=totalURLs))

        for j, url in enumerate(queue):
            contents = saramin_scrapper(url, driver, delay=0.2)
            writer(fp, contents)

            progress = int(j / totalURLs * 100)
            self.progress_scrap.emit(progress)

        # 종료
        driver.close()
        fp.close()
        self.progress_scrap.emit(100)
        
        # 엑셀 파일 생성
        df = read_csv(result_path, sep='|',  encoding='utf-8')
        xlsx_result_path = result_path.split("/")[1] 
        xlsx_result_path = xlsx_result_path.split(".cache")[0] + ".xlsx"
        xlsx_result_path_save = os.path.join("/home/deepcell/바탕화면", xlsx_result_path)
        df.to_excel(xlsx_result_path_save)
        
        # 캐시 삭제 
        for cache in os.listdir("cache"):
            os.remove("cache/"+cache) 
        
        self.progress_message.emit("공고 수집이 완료되었습니다.\n바탕화면에서 {xlsx_result_path} 파일을 확인하십시오.".format(xlsx_result_path=xlsx_result_path))


