#!/usr/bin/env python
# coding: utf-8

# In[9]:


import requests
import time


# In[13]:


def getDownload(url, params=None, wait=1, retry=3, **kwargs):
    """오류가 발생하면 잠시 멈췄다가 다시 시도하는 get방식의 request"""
    
    try:
        resp = requests.get(url, params=params, **kwargs)
        resp.raise_for_status
    except:
        print('{} Error is occured.'.format(resp.status_code))
        if 500 <= resp.status_code < 600 and retry > 0:
            print("Retry to get page. (remained retry: {})".format(retry-1))
            time.sleep(wait)
            resp = getDownload(url, wait, retry-1, params=params, **kwargs)
    
    if not resp.ok:
        print("Failed to get page: {url}".format(url=url))
    
    return resp


# In[ ]:
def postDownload(url, data=None, wait=1, retry=3, **kwargs):
    """오류가 발생하면 잠시 멈췄다가 다시 시도하는 post방식의 request"""
    
    try:
        resp = requests.post(url, data=data, **kwargs)
        resp.raise_for_status
    except:
        print('{} Error is occured.'.format(resp.status_code))
        if 500 <= resp.status_code < 600 and retry > 0:
            print("Retry to get page. (remained retry: {})".format(retry-1))
            time.sleep(wait)
            resp = getDownload(url, wait, retry-1,  data=data, **kwargs)
    
    if not resp.ok:
        print("Failed to get page: {url}".format(url=url))
    
    return resp



