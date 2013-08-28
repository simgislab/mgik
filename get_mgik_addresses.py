# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------------
# get_mgik_uiks.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# About: Grabber for Mosgorizberkom data on UIKs: http://mosgorizbirkom.ru/web/guest/searchuik Creates data/geodata.
# Created: 25.08.2013
# Usage example: 
#                   grab all:           python get_mgik_uiks.py 
#                   grab specific uik:  python get_mgik_uiks.py 2632 
# ---------------------------------------------------------------------------

import csv
import sys
import urllib2
from bs4 import BeautifulSoup
from datetime import datetime

def download_search(link,id,i):
    try:
        u = urllib2.urlopen(link)
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            print 'We failed to reach a server for ' + str(id) + '.' + ' Attempt: ' + str(i)
            print 'Reason: ', e.reason
            error = e.reason[0]
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request. Error code: ', e.code
            error = e.code
    else:
        f = open("mgik_addr/" + id + ".html","wb")
        f.write(u.read())
        f.close()
        print("Listing for " + id + " was downloaded")
        error = 0
    
    return error

def read_link(link):
    for i in range(1,5):
        try:
            u = urllib2.urlopen(link)
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server for ' + str(id) + '.' + ' Attempt: ' + str(i)
                print 'Reason: ', e.reason
                error = e.reason[0]
            elif hasattr(e, 'code'):
                print 'The server couldn\'t fulfill the request. Error code: ', e.code
                error = e.code
        else:
            d = u.read()
            error = 0
            break
        
        if error == 404:
            break
    
    return d,error

def parse_search(id):
    f_search = open("mgik_addr/" + id + ".html",'rb')
    soup = BeautifulSoup(''.join(f_search.read()))
    sections = soup.findAll("section", { "class" : "" })
    
    lvl1_val = sections[0].find("input")['value']
    
    lvl1_link = link_mgik_base + sections[2].find("form")['action']
    
    d_lvl1,error_lvl1 = read_link(lvl1_link)
    if error_lvl1 == 0:
        soup_lvl1 = BeautifulSoup(''.join(d_lvl1))
        lis_lvl1 = soup_lvl1.findAll("li")
        for li_lvl1 in lis_lvl1:
            lvl2_link = link_mgik_base + li_lvl1.find("a")['href']
            lvl2_val = list(li_lvl1.find("a").strings)[0]
            
            d_lvl2,error_lvl2 = read_link(lvl2_link)
            if error_lvl2 == 0:
                soup_lvl2 = BeautifulSoup(''.join(d_lvl2))
                #check if node is final
                if len(soup_lvl2.findAll("h4")) !=0 or len(soup_lvl2.findAll("section")) == 0:
                    if len(soup_lvl2.findAll("section")) !=0: 
                        sections_lvl2 = soup_lvl2.findAll("section", { "class" : "" })
                        uik_id = list(sections_lvl2[0].find("p", {"class":"value"}).strings)[0]
                    else:   #case http://mosgorizbirkom.ru/precinct/precinct/boundary/byaddress/54955
                        uik_id = -1
                    lvl3_val = lvl2_val
                    lvl2_val = ""
                    lvl3_link = ""
                    write_csv(uik_id,lvl1_val,lvl2_val,lvl3_val,lvl2_link)
                else:
                    lvl2_link = lvl2_link.replace("search/","children/byname/")
                    d_lvl2,error_lvl2 = read_link(lvl2_link)
                    if error_lvl2 == 0:
                        soup_lvl2 = BeautifulSoup(''.join(d_lvl2))
                        lis_lvl2 = soup_lvl2.findAll("li")
                        for li_lvl2 in lis_lvl2:
                            lvl3_link = link_mgik_base + li_lvl2.find("a")['href']
                            lvl3_val = list(li_lvl2.find("a").strings)[0]
                            
                            d_lvl3,error_lvl3 = read_link(lvl3_link)
                            if error_lvl3 == 0:
                                soup_lvl3 = BeautifulSoup(''.join(d_lvl3))
                                if len(soup_lvl3.findAll("section")) == 0: #case http://mosgorizbirkom.ru/precinct/address/1045/search/
                                    uik_id = -1
                                else:
                                    sections_lvl3 = soup_lvl3.findAll("section", { "class" : "" })
                                    uik_id = list(sections_lvl3[0].find("p", {"class":"value"}).strings)[0]
                                
                                write_csv(uik_id,lvl1_val,lvl2_val,lvl3_val,lvl2_link)
                                
                            else:
                                f_errors.write(lvl3_link  + "," + str(error_lvl3) + "\n")
                    else:
                        f_errors.write(lvl2_link  + "," + str(error_lvl2) + "\n")    
            else:
                f_errors.write(lvl2_link  + "," + str(error_lvl2) + "\n")
    else:
        f_errors.write(lvl1_link  + "," + str(error_lvl1) + "\n")
    
    
def write_csv(uik_id,lvl1_val,lvl2_val,lvl3_val,lvl2_link):
    csvwriter.writerow(dict(UIK_ID=uik_id,
                            LVL1=lvl1_val.encode("utf-8"),
                            LVL2=lvl2_val.encode("utf-8"),
                            LVL3=lvl3_val.encode("utf-8"),
                            SEARCH_L=link_base + str(id) + "/search",
                            LVL2_LINK=lvl2_link))

def make_csvt(f_output_name,fieldnames_types):
    f_csvt_name = f_output_name.replace("csv","csvt")
    f_csvt = open(f_csvt_name,"w")
    f_csvt.write(','.join(fieldnames_types))
    f_csvt.close()

if __name__ == '__main__':
    specific_id = 0
    args = sys.argv[1:]
    if len(args) == 1:
        specific_id = args[0]
    
    curdate = datetime.now().strftime("%Y%m%d")
    link_base = "http://mosgorizbirkom.ru/precinct/address/"
    link_mgik_base = "http://mosgorizbirkom.ru"
    
    n = 4000
    all_addr = range(1,n)
    if specific_id == 0:
        sequence = all_addr
        name_root = "mgik_addr_all"
    else:
        sequence = [specific_id]
        name_root = str(specific_id)
    
    f_output_name = name_root + "_" + curdate + '.csv'
    f_output = open(f_output_name, 'wb')
    f_errors = open('addr_errors.log','wb')
    
    fieldnames_data = ('UIK_ID', 'LVL1', 'LVL2', 'LVL3', 'SEARCH_L', 'LVL2_LINK')
    fieldnames_types = ("String(255)", "String(255)", "String(255)", "String(255)", "String(255)", "String(255)", "String(255)")
    
    make_csvt(f_output_name,fieldnames_types)

    f_output.write(','.join(fieldnames_data) + "\n")
    csvwriter = csv.DictWriter(f_output, fieldnames=fieldnames_data)
    
    for id in sequence:
        url = link_base + str(id) + "/search"
        
        for i in range(1,5):
            error = download_search(url,str(id),i)  #http://mosgorizbirkom.ru/precinct/address/3/search
            i = i + 1
            if error == 0 or error == 404:
                break
        
        if error == 0:
            parse_search(str(id))
        else:
            f_errors.write(str(id) + "," + url  + "," + str(error) + "\n")
    
    f_output.close()
    f_errors.close()
    
