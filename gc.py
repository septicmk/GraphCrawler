#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Date     : 2015/09/25 20:21:53
FileName : syncc.py
Author   : septicmk
"""

import re
import logging
import ConfigParser
import getopt
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')

graph={}

def check_existed(path):
    import os
    return os.path.exists(path)

def pause():
    raw_input('press \'Enter\' to continue')

def get_revalue(html, rex, er, ex):
    v = re.search(rex, html)
    if v is None:
        if ex:
            logging.error(er)
            raise TypeError(er)
        else:
            logging.warning(er)
        return ''
    return v.group(1)


def find_graph_des(html):
    pat = (r'<td .*? title="Nodes">(.*?)</td>'
           r'<td .*? title="Edges">(.*?)</td>'
           r"""<td class='{sortValue: .*?}'>(.*?)</td>.*?<a href="([^"]*?)">Download</a>""")
    ret = re.findall(pat,html)
    return ret

def cull(tb):
    MB_set = []
    KB_set = []
    for a,b,c,d in tb:
        if(a.endswith('K') or a.endswith('M')):
            if(b.endswith('K') or b.endswith('M')):
                if(c.endswith('MB') and int(c[:-3])<100):
                    MB_set.append((c,d))
                elif(c.endswith('KB')):
                    KB_set.append((c,d))
    return MB_set, KB_set
                    
def info(tb, ed):
    s = 0;
    for sz,url in tb:
        s = s+ int(sz[:-3])
    if ed == "MB":
        s = s/1024
    elif ed == "KB":
        s = s/(1024*1024.0)
    return s 

def download(url,file):
    def chunk_report(bytes_so_far, chunk_size, total_size):
      percent = int(bytes_so_far*100 / total_size)
      sys.stdout.write( "\r" + "Downloading" + '  ' + os.path.basename(file) + " ...(%.1f KB/%.1f KB)[%d%%]" % (bytes_so_far/1024.0, total_size/1024.0, percent))
      sys.stdout.flush()
      if bytes_so_far >= total_size:
         sys.stdout.write('\n')
         sys.stdout.flush()

    def chunk_read(response, chunk_size=8192, report_hook=None):
        try:
            total_size = response.info().getheader('Content-Length').strip()
        except:
            return response.read()

        total_size = int(total_size)
        bytes_so_far = 0
        ret = ''
    
        while 1:
            chunk = response.read(chunk_size)
            bytes_so_far += len(chunk)
            ret += chunk
    
            if not chunk:
                break
    
            if report_hook:
                report_hook(bytes_so_far, chunk_size, total_size)
        return ret

    output = open(file, 'wb')
    try:
        response = urllib2.urlopen(url)
        content = chunk_read(response, report_hook=chunk_report)
        output.write(content)
    except:
        parsed_link = urlparse.urlsplit(url.encode('utf8'))
        parsed_link = parsed_link._replace(path=urllib.quote(parsed_link.path))
        url = parsed_link.geturl()
        response = urllib2.urlopen(url)
        content = chunk_read(response, report_hook=chunk_report)
        output.write(content)

    output.close()


def downloadall(tb, pwd):
    if not os.path.exists(pwd):
        os.makedirs(pwd)
    for sz,url in tb:
        name = get_revalue(url,r'([^/]+?)$', 'get name error', 1)
        _pwd = os.path.join(pwd,name)
        print _pwd
        #download(url,_pwd)


if __name__ == '__main__':
    fh = open('target.html','r')
    html = fh.read()
    print "read over"
    ret = find_graph_des(html)
    A,B = cull(ret)
    print "Total Large Graph data set size: " + str(info(A,"MB")) + " GB, NUM: " + str(len(A))
    print "Total Small Graph data set size: " + str(info(B,"KB")) + " GB, NUM: " + str(len(B))
    downloadall(B,"/home/mengke/dataset/small/") 
    downloadall(A,"/home/mengke/dataset/large/") 
