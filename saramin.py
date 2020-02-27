from bs4 import BeautifulSoup
import requests
import re
from math import ceil
from utils import getDownload
import time
import functools
import os

# crawler

def get_recruit_urls_from_page(searchword, recruitPage=1):
    """
    사람인에서 searchword 검색 결과, 특정 페이지의 구인 공고의 url을 수집함
    
    기본 설정값:
        url = 'http://www.saramin.co.kr/zf_user/search/recruit'
        params = {'searchword': searchword,
                 'recruitPage': recruitPage,
                 'recruitSort': 'relation',
                 'recruitPageCount': '100',
                 'company_cd': '0,1,2,3,4,5,6,7,9'}
 
    """
    # default option
    url = 'http://www.saramin.co.kr/zf_user/search/recruit'
    params = {'searchword': searchword,
             'recruitPage': recruitPage,
             'recruitSort': 'relation',
             'recruitPageCount': '100',
             'company_cd': '0,1,2,3,4,5,6,7,9'}
    
    # make dom
    resp = getDownload(url, params=params)
    dom = BeautifulSoup(resp.text, 'lxml')
    
    # get urls
    recruit_posts = dom.select("#recruit_info_list > div.content > div")
    recruit_urls = [requests.compat.urljoin(url, post.select_one("a")['href']) 
                     for post in recruit_posts] 
    
    return recruit_urls


def get_recruit_urls(searchword):
    """
    사람인에서 searchword 검색 결과, 모든 구인 공고의 url을 수집함
    
    참조:
        get_recruit_urls_from_page
    """
    resp = getDownload('http://www.saramin.co.kr/zf_user/search/recruit',
                       params={'searchword':searchword})
    dom = BeautifulSoup(resp.text, 'lxml')

    totalPosts = dom.select_one("#recruit_info > div.header > span").text
    totalPosts = int(re.sub("[^\d]", "", totalPosts))

    totalPages = ceil(totalPosts / 100)

    recruit_urls = []
    
    for recruitPage in range(1, totalPages+1):
        recruit_urls.extend(get_recruit_urls_from_page(searchword=searchword, recruitPage=recruitPage))
        
    return recruit_urls


def get_recruit_totalPage(searchword):
    """
    사람인에서 searchword 검색 결과, 구인 공고 페이지수를 구함
    """
    resp = getDownload('http://www.saramin.co.kr/zf_user/search/recruit',
                       params={'searchword':searchword})
    dom = BeautifulSoup(resp.text, 'lxml')

    totalPosts = dom.select_one("#recruit_info > div.header > span").text
    totalPosts = int(re.sub("[^\d]", "", totalPosts))

    totalPages = ceil(totalPosts / 100)

    return totalPages
    
# scrapper

def exception(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        try:
            result = fn(*args, **kwargs)
        except IndexError as e:
            return -1
        except AttributeError as e:
            return -1
        return result
    return inner

@exception
def get_company_name(dom):
    """사람인에서 공고기업의 이름"""
    company_name = dom.select_one(".wrap_jv_header .jv_header a.company").text.strip()
    return company_name

@exception
def get_workers_count(dom):
    """사람인에서 공고기업의 사원수"""
    company_info = dom.select_one(".jv_cont.jv_company > .cont.box > .wrap_info > .info ")
    workers_count = [_ for _ in company_info.find_all('dt') if '사원수' in _.text][0].next_sibling   
    workers_count = int(workers_count.text.split("명")[0])
    return workers_count

@exception
def get_company_address(dom):
    """사람인에서 공고기업의 주소"""
    company_info = dom.select_one(".jv_cont.jv_company > .cont.box > .wrap_info > .info ")
    company_address = [_ for _ in company_info.find_all('dt') if '기업주소' in _.text][0].next_sibling.text
    return company_address

@exception
def get_working_place(dom):
    """사람인에서 구인공고의 근무지"""
    working_place = dom.select_one('.jv_cont.jv_summary .cont').find('dt', text='근무지역').next_sibling # 근무지역
    working_place = working_place.text.split('지도')[0].strip()
    return working_place 
    
def get_recruitment(dom):
    """사람인에서 구인공고의 구인 수를 알 수 없음 (always returns -1)"""
    return -1
    
@exception
def get_applicant_count(dom):
    """사람인에서 구인공고의 지원자 수"""
    applicant_count = dom.select_one('.jv_cont.jv_statics .total > dd > span').text
    return applicant_count

def saramin_scrapper(url, driver):
    """
    구인 공고에서 필요한 내용을 스크랩한다.
    
    return: 
        (기업명, 근무자수, 기업주소,
        공고근무지, 모집인원, 지원자수,
        스크랩주소, 스크랩시간)
    """
    driver.get(url)
    time.sleep(0.5)
    dom = BeautifulSoup(driver.page_source, 'lxml')
    
    # 기업 정보
    company_name = get_company_name(dom)
    workers_count = get_workers_count(dom)
    company_address = get_company_address(dom)
    # 공고 정보
    working_place = get_working_place(dom)
    recruitment = get_recruitment(dom)
    applicant_count = get_applicant_count(dom)
    # 스크랩 정보
    scrap_url = url
    scrap_time = time.ctime()
    
    return (company_name, workers_count, company_address, 
             working_place, recruitment, applicant_count, 
             scrap_url, scrap_time)


# writer

def writer_init(searchword):
    """
    결과 csv 파일을 세팅한다.
    이미 파일이 존재하면 새롭게 csv 파일을 생성한다.
    """
    result_path = f'saramin_search_{searchword}.csv'
    if os.path.exists(result_path):

        for n in range(1, 10):
            if n == 10:
                raise Exception("결과 파일을 삭제하고 다시 시도하세요") 

            if os.path.exists(f'saramin_search_{searchword} ({n}).csv'):
                continue
            else: 
                result_path = f'saramin_search_{searchword} ({n}).csv'
                break

    fp = open(result_path, 'w', encoding='ANSI')
    fp.write('기업명| 근무자수| 기업주소| 공고근무지| 모집인원| 지원자수| 스크랩주소| 스크랩시간')
    fp.write('\n')
        
    return fp, result_path


def writer(fp, contents):
    contents = [str(_) for _ in contents]
    contents = '| '.join(contents)
    fp.write(contents)
    fp.write('\n')
