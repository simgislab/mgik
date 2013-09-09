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

def download_uik(link,id,i):
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
        f = open("mgik_uik/" + id + ".html","wb")
        f.write(u.read())
        f.close()
        print("Listing for " + id + " was downloaded")
        error = 0
    
    return error

def parse_uik(id):
    f_uik = open("mgik_uik/" + id + ".html",'rb')
    soup = BeautifulSoup(''.join(f_uik.read()))
    sections = soup.findAll("section", { "class" : "" })
    
    id = list(sections[0].find("p", {"class":"value"}).strings)[0]
    
    addr_o_link = sections[1].find("p", {"class":"label"}).find("a")['href']
    link_o_q = addr_o_link.split("=")[1]
    if link_o_q[0:2] == "55":
        lat_o = float(link_o_q.split(",")[0])
        lon_o = float(link_o_q.split(",")[1])
        wkt_o = "POINT (" + str(lon_o) + " " + str(lat_o) + ")"
    else:
        wkt_o = lat_o = lon_o = None
    
    if len(list(sections[1].findAll("p", {"class":"value"})[0].strings)) != 0: #case 2687
        addr_o = list(sections[1].findAll("p", {"class":"value"})[0].strings)[0]
    else:
        addr_o = "empty"
    
    if sections[1].findAll("p", {"class":"value"})[1].find("a") != None:
        phone_o = sections[1].findAll("p", {"class":"value"})[1].find("a")['href']
        phone_o = phone_o.replace("tel:","")
    else:
        phone_o = "none"
    
    if len(list(sections[1].findAll("p", {"class":"value"})[2].strings)) != 0:
        place_o = list(sections[1].findAll("p", {"class":"value"})[2].strings)[0]
    else:
        place_o = "none"
    
    addr_v_link = sections[2].find("p", {"class":"label"}).find("a")['href']
    link_v_q = addr_v_link.split("=")[1]
    if link_v_q[0:2] == "55":
        lat_v = float(link_v_q.split(",")[0])
        lon_v = float(link_v_q.split(",")[1])
        wkt_v = "POINT (" + str(lon_v) + " " + str(lat_v) + ")"
    else:
        wkt_v = lat_v = lon_v = None
    
    if len(list(sections[2].findAll("p", {"class":"value"})[0].strings)) != 0:
        addr_v = list(sections[2].findAll("p", {"class":"value"})[0].strings)[0]
    else:
        addr_v = "empty"
    
    if sections[2].findAll("p", {"class":"value"})[1].find("a") != None:
        phone_v = sections[2].findAll("p", {"class":"value"})[1].find("a")['href']
        phone_v = phone_v.replace("tel:","")
    else:
        phone_v = "none"
    
    if len(list(sections[2].findAll("p", {"class":"value"})[2].strings)) != 0:
        place_v = list(sections[2].findAll("p", {"class":"value"})[2].strings)[0]
    else:
        place_v = "none"
        
    src = link_base + str(id)
    
    csvwriter.writerow(dict(ID=id,
                            WKT=wkt_v,
                            WKT_O=wkt_o,
                            LAT=lat_v,
                            LON=lon_v,
                            LAT_O=lat_o,
                            LON_O=lon_o,
                            ADDR_V=addr_v.encode("utf-8"),
                            ADDR_V_L=addr_v_link.encode("utf-8"),
                            PLACE_V=place_v.encode("utf-8"),
                            PHONE_V=phone_v,
                            ADDR_O=addr_o.encode("utf-8"),
                            ADDR_O_L=addr_o_link.encode("utf-8"),
                            PLACE_O=place_o.encode("utf-8"),
                            PHONE_O=phone_o,
                            SRC=src))

def make_csvt(f_output_name,fieldnames_types):
    f_csvt_name = f_output_name.replace("csv","csvt")
    f_csvt = open(f_csvt_name,"w")
    f_csvt.write(','.join(fieldnames_types))
    f_csvt.close()

def make_prj(f_output_name):
    f_prj_name = f_output_name.replace("csv","prj")
    f_prj = open(f_prj_name,"w")
    f_prj.write("""GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]""")
    f_prj.close()

def make_vrt(f_vrt_name,key):
    vrt_latlon = """<OGRVRTDataSource>
    <OGRVRTLayer name="%s">
        <SrcDataSource relativeToVRT="1">%s</SrcDataSource>
        <LayerSRS>EPSG:4326</LayerSRS>
        <GeometryType>wkbPoint</GeometryType>
        <GeometryField encoding="WKT" field="%s"/>
    </OGRVRTLayer>
</OGRVRTDataSource>""" % (f_output_name.replace(".csv",""),f_output_name,key)
    
    f_vrt = open(f_vrt_name,"w")
    f_vrt.write(vrt_latlon)
    f_vrt.close()
    
if __name__ == '__main__':
    specific_id = 0
    args = sys.argv[1:]
    if len(args) == 1:
        specific_id = args[0]
    
    curdate = datetime.now().strftime("%Y%m%d")
    #link_base = "http://mosgorizbirkom.ru/precinct/precinct/bynumber/?number=" <-old link
    link_base = "http://mosgorizbirkom.ru/precinct/precinct/"
    
    n = 4000
    all_uiks = range(1,n)
    if specific_id == 0:
        sequence = all_uiks
        name_root = "mgik_uiks_all"
    else:
        sequence = [specific_id]
        name_root = str(specific_id)
    
    f_output_name = name_root + "_" + curdate + '.csv'
    f_output = open(f_output_name, 'wb')
    f_errors = open('errors.log','wb')
    
    fieldnames_data = ('ID', 'WKT', 'WKT_O', 'LAT', 'LON', 'LAT_O', 'LON_O', 'ADDR_V', 'ADDR_V_L', 'PLACE_V', 'PHONE_V', 'ADDR_O', 'ADDR_O_L', 'PLACE_O', 'PHONE_O', 'SRC')
    fieldnames_types = ("Integer(5)", "String(255)", "String(255)", "Real(10.7)", "Real(10.7)", "Real(10.7)", "Real(10.7)", "String(255)", "String(255)", "String(255)", "String(255)", "String(255)", "String(255)", "String(255)", "String(255)", "String(255)")
    
    make_csvt(f_output_name,fieldnames_types)
    make_prj(f_output_name)
    
    f_vrt_name = f_output_name.replace("csv","vrt")
    make_vrt(f_vrt_name, 'WKT')
    f_vrt_name = f_output_name.replace(".csv","_office.vrt")
    make_vrt(f_vrt_name, 'WKT_O')
    
    f_output.write(','.join(fieldnames_data) + "\n")
    csvwriter = csv.DictWriter(f_output, fieldnames=fieldnames_data)

    
    for id in sequence:
        url = link_base + str(id) 
        
        for i in range(1,5):
            error = download_uik(url,str(id),i)
            i = i + 1
            if error == 0 or error == 404:
                break
        
        if error == 0:
            parse_uik(str(id))
        else:
            f_errors.write(str(id) + "," + url  + "," + str(error) + "\n")
    
    f_output.close()
    f_errors.close()
    
