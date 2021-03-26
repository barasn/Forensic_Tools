#!/usr/bin/env python3
# coding : utf8

import PyPDF2
import argparse
import re
import exifread
import sqlite3 as sq
import webbrowser as wb


def connect_to_website(url, x, y):
    wb.open_new(f'{url}{x},{y}')


def get_pdf_meta(file_name):
    pdf_file =  PyPDF2.PdfFileReader(open(file_name, 'rb'))
    doc_info = pdf_file.getDocumentInfo()
    for info in doc_info:
        print(f'[+] {info}  : {doc_info[info]}')


def get_strings(file_name):
    with open(file_name, 'rb') as file:
        content = file.read()
    _re = re.compile("[\S\s]{4,}")
    for match in _re.finditer(content.decode('uft8', 'backslashreplace')):
        print(match.group())


def get_exif(file_name):
    with open(file_name, 'rb') as file:
        exif = exifread.process_file(file)
    if not exif:
        print("Aucune métadonnée EXIF")
    else:
        for tag in exif.keys():
            if tag != 'JPEGThumbnail':
                print(f'{tag} : {exif[tag]}')


def _convert_to_degres(value):

    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)
    return d + (m / 60.0) + (s / 3600.0)


def get_gps_from_exif(file_name):
    with open(file_name, 'rb') as file:
        exif = exifread.process_file(file)
    if not exit:
        print("Aucune métadonnée EXIF")
    else:
        latitude = exif.get("GPS GPSLatitude")
        longitude = exif.get("GPS GPSLongitude")
        latitude_ref = exif.get("GPS GPSLatitudeRef")
        longitude_ref = exif.get("GPS GPSLongitudeRef")
        if latitude and longitude and latitude_ref and longitude_ref:
            lat = _convert_to_degres(latitude)
            long = _convert_to_degres(longitude)
            if str(latitude_ref) != "N":
                lat = 0 - lat
            if str(longitude_ref) != 'E':
                long = 0 - long
            url = "http://maps.google.com/maps?q=loc:"
            lat = str(lat)
            long = str(long)
            connect_to_website(url, lat, long)


def get_firefox_history(file_places_sqlite):
    try:
        con = sq.connect(file_places_sqlite)
        cursor = con.cursor()
        query = "select url, datetime(last_visit_date/1000000, \
        \"unixepoch\") from moz_places, moz_historyvisits \
        where visit_count > 0 and moz_places.id == moz_historyvisits.place_id"
        cursor.execute(query)
        header = "<!DOCTYPE html><head></head><body><table><tr><th>URL</th><th>Date</th></tr>"
        with open('/home/baye/Bureau/Forensic_tools/rapport_firefox_history.html', 'a') as f:
            f.write(header)
            for row in cursor:
                url = str(row[0])
                date = str(row[1])
                # print(f'[+] {url}   {date}')
                f.write(f'<tr><td><a href=\"{url}\">{url}</a></td><td>{date}</td></tr>')
            footer = "</table></body></html>"
            f.write(footer)
            print("[+] OK")
    except Exception as e:
        print(f"[-] Error :  {e}")
        exit(1)


def get_firefox_cookies(file_cookies_sqlite):
    try:
        con = sq.connect(file_cookies_sqlite)
        cursor = con.cursor()
        query = "SELECT name, value, host From moz_cookies"
        cursor.execute(query)
        header = "<!DOCTYPE html><head><style>table,th,tr,td{border:1px solid blue;}</style>\
        </head><body><table><tr><th>Name cookie</th><th>Value cookie</th><th>Host cookie</th></tr>"
        with open('/home/baye/Bureau/Forensic_tools/rapport_firefox_cookies.html', 'a') as f:
            f.write(header)
            for row in cursor:
                name = str(row[0])
                value = str(row[1])
                host = str(row[2])
                # print(f'[+] {name}  {value}  {host}')
                f.write(f'<tr><td>{name}</td><td>{value}</td><td>{host}</td><tr>')
            footer = "</table></body></html>"
            f.write(footer)
            print("[+] Complete")

    except Exception as e:
        print(f"[-] Error :  {e}")
        exit(1)


parser = argparse.ArgumentParser(description="Forensic Tools")
parser.add_argument('-pdf', '--pdf', dest='pdf', help='Path of the pdf file', required=False)
parser.add_argument('-str', '--str', dest='str', help='Path of the pdf file which strings ', required=False)
parser.add_argument('-exif', '--exif', dest='exif', help='Path of the image for exif', required=False)
parser.add_argument('-gps', '--gps', dest='gps', help='Recover the image coordinate', required=False)
parser.add_argument('-fh', '--fh', dest='fhistory', help='Recover the history of the web page history in Firefox',
                    required=False)
parser.add_argument('-fc', '--fc', dest='fcookie', help='Recover the cookies of the web page history in Firefox',
                    required=False)

args = parser.parse_args()

if args.pdf:
    get_pdf_meta(args.pdf)

if args.str:
    get_strings(args.str)

if args.exif:
    get_exif(args.exif)

if args.gps:
    get_gps_from_exif(args.gps)

if args.fhistory:
    get_firefox_history(args.fhistory)

if args.fcookie:
    get_firefox_cookies(args.fcookie)