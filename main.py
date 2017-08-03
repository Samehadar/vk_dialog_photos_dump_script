# coding=utf-8

import requests
import re
import sys
import os
import urllib.request
import json

# argv[1] = remixsid_cookie
# argv[2] = dialog_id
# argv[3] = person_name

def printHelp():
    print("""
    Usage: python main.py <remixsid_cookie> <dialog_id> <name_of_folder>
    <dialog_id> is a string parameter "sel" in address line which you see when open a dialog
    """)

default_domain = "http://pp.userapi.com/c"
default_domain_for_origin = "http://127.0.0.1/"
def downloadOriginPhoto(my_jsons: list, photo: str):
    for my_json in my_jsons:
        if (my_json.get("id").__contains__(photo)):
            server = str(my_json.get("rotate").get("server"))
            orig_url = my_json.get("rotate").get("orig_url")
            res_url = default_domain + server + "/" + orig_url.replace(default_domain_for_origin, "")
            urllib.request.urlretrieve(res_url, str(photo) + ".jpg")


def downloadMaxAvailableSizePhoto(my_jsons: list, photo: str):
    for my_json in my_jsons:
        if (my_json.get("id").__contains__(photo)):
            server = re.findall("\d+",my_json.get("base")).pop()
            z_src = my_json.get("z_").__getitem__(0) + ".jpg"
            res_url = default_domain + server + "/" + z_src
            urllib.request.urlretrieve(res_url, str(photo) + ".jpg")

try:
    sys.argv[1]
except IndexError:
    printHelp()
    exit()

if( sys.argv[1] == '--help' ):
    printHelp()
    exit()
else:
    if( len(sys.argv) < 4 ):
        print("""
        Invalid number of arguments. Use parameter --help to know more
        """)
        exit()

remixsid_cookie = sys.argv[1]
user_id = "PUT YOUR ID HERE"

RequestData = {
    "act": "show",
    "al": 1,
    "loc":"im",
    "w": "history" + sys.argv[2] + "_photo",
    "offset" : 0,
    "part" : 1
}

request_href = "http://vk.com/wkview.php"
request_full_size_image_href = "http://vk.com/al_photos.php" # this we get full_size image url
bound = {"count" : 10000, "offset" : 0}

try:
    os.mkdir("drop_" + sys.argv[3])
except OSError:
    print("Проблемы с созданием папки 'drop_" + sys.argv[3] + "'")
if( os.path.exists("drop_" + sys.argv[3]) ):
    os.chdir("drop_" + sys.argv[3])
else:
    print("Не удалось создать папку\n")
    exit()

test = open("links.txt", "w")
photos = open("photos.txt", "w")
mails_file = open("mails.txt", "w")
while( bound['offset'] < bound['count'] ):
    RequestData['offset'] = bound['offset']
    content = requests.post(request_href, cookies={"remixsid": remixsid_cookie}, params=RequestData).text
    json_data_offset = re.compile('\{"count":.+?,"offset":.+?\}').search(content)
    bound = json.loads(content[json_data_offset.span()[0]:json_data_offset.span()[1]])
    bound['count'] = int(bound['count'])
    bound['offset'] = int(bound['offset'])

    links = re.compile('http://cs.+?"').findall(content)
    photo_refs = re.compile("""\('\d+_+\d+',""").findall(content) # - 123123_231231 -pattern
    mails = re.compile("""'mail\d+'""").findall(content) # - mail123123 - pattern

    for st in links:
        st = st.replace("&quot;,&quot;x_&quot;:[&quot;", "").replace("\"", "").split(");")[0]
        test.write(st + '\n')
    for mail in mails:
        mail = mail.replace("'", "")
        mails_file.write(mail + '\n')
    for ref in photo_refs:
        ref = ref.replace("(", "").replace(",", "").replace("'", "")
        photos.write(ref + '\n')

test.close()
mails_file.close()
photos.close()


photos = open("photos.txt", "r")
mails_file = open("mails.txt", "r")
file_num = 0
for photo, mail in zip(photos, mails_file):
    RequestDataFullSize = {
        "act": "show",
        "al": 1,
        "al_ad": 0,
        "gid": 0,
        "list": mail.replace("\n", ""),
        "module": "im",
        "photo": photo.replace("\n", "")
    }
    try:
        content = requests.post(request_full_size_image_href, cookies={"remixsid": remixsid_cookie}, params=RequestDataFullSize).text
        xml_trash = re.findall("<{1}\S*>{1}", content)
        for trash in xml_trash:
            content = content.replace(trash, "")
        content = content[1:]
        raw_jsons = re.findall("{\"id[^}]+\S+}", content)
        jsons = [json.loads(raw) for raw in raw_jsons]

        if (photo.__contains__(user_id)):
            downloadOriginPhoto(jsons, photo.replace("\n", ""))
        else:
            downloadMaxAvailableSizePhoto(jsons, photo.replace("\n", ""))

    except:
        print("Не удалось скачать изображение по ссылке: " + str(photo.replace("\n", "")))
    file_num += 1
    print("Скачано " + str(file_num) + " файлов\n")
photos.close()
mails_file.close()