import requests
import xmltodict
import urllib
from prettytable import PrettyTable,ALL
import pickle
import re
import os
import urllib
from datetime import datetime
import pyperclip
import bencodepy
import hashlib
import base64
import requests

from subprocess import Popen, PIPE, TimeoutExpired,call
class Colors:
    """ ANSI color codes """
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"
    WHITE = "\033[40m"

temp_dir='C:\webtorrent'

suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def humansize(nbytes):
    nbytes = float(nbytes)
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])
    
# name=input("Query: ")

color_index_mapping={
    2:Colors.YELLOW,
    3:Colors.GREEN,
    4:Colors.GREEN,
    5:Colors.LIGHT_BLUE 
}

def to_color(li,mapping):
    return [mapping[i]+str(x)+Colors.END if i in mapping else str(x) for i,x in enumerate(li)] 

def get_torrent_data(query):
    res=requests.get(f'http://152.67.231.52:9117/api/v2.0/indexers/all/results/torznab?apikey=hbzavtb8ksbnsjohvvdchqiuo2ubfkkb&t=search&q={urllib.parse.quote_plus(query)}')
    data=xmltodict.parse(res.content)
    # pickle.dump(data,open(f'data.pkl','wb'))
    data=pickle.load(open("data.pkl","rb"))
    query_split=[x for x in query.lower().split(' ') if x!='']
    parsed_data=[]
    for item in data['rss']['channel']['item']:
        seeds=next((itr['@value'] for itr in item['torznab:attr'] if itr['@name']=='seeders'),None)
        peers=next((itr['@value'] for itr in item['torznab:attr'] if itr['@name']=='peers'),None)
        indexer=item['jackettindexer']['@id']
        parsed_data.append([item['title'],humansize(item['size']),int(seeds),int(peers),indexer,item['link'],int(item['size'])])
    parsed_data=sorted(parsed_data,key=lambda x:(x[2],x[3]),reverse=True)
    parsed_data=list(filter(lambda x:all(y in x[0].lower() for y in query_split),parsed_data))
    return parsed_data

def convert_to_table_history(data):
    all_data = PrettyTable()
    all_data.hrules=ALL
    all_data.field_names = ["Index","Title","Searched Date"]
    all_data._max_width = {"Index": 10,"Title": 70, "Last Access": 30}
    for i,item in enumerate(data,1):
        # add row with color
        all_data.add_row(to_color([i,item[0],item[1]],color_index_mapping))
    return all_data

def convert_to_table_search(data):
    all_data = PrettyTable()
    all_data.hrules=ALL
    all_data.field_names = ["Index","Title", "Size", "Seeds", "Peers", "Indexer"]
    all_data._max_width = {"Index": 10,"Title": 70, "Size": 10, "Seeds": 10, "Peers": 10, "Indexer": 30}
    for i,item in enumerate(data,1):
        # add row with color
        all_data.add_row(to_color([i,item[0],item[1],item[2],item[3],item[4]],color_index_mapping))
    return all_data

def convert_to_table_magnet(magnet_info):
    torrent_data = PrettyTable()
    torrent_data.hrules=ALL
    torrent_data.field_names = ["Index","Title", "Size"]
    torrent_data._max_width = {"Index": 10,"Title": 100, "Size": 10}
    for i,item in enumerate(magnet_info,1):
        matches=re.match(r"(\d+)(.*)\((.*)\)",item)
        torrent_data.add_row(to_color([i,matches.group(2).strip(),matches.group(3).strip()],color_index_mapping))
    return torrent_data




def get_magnet_info(link):
    with Popen(f'webtorrent -o {temp_dir} "{link}" --select', shell=True, stdout=PIPE) as process:
        try:
            op = process.communicate(timeout=30)[0]
            r = re.compile("\d+\s.*")
            conv_list=op.decode("utf-8").split('\n')
            magnet_info=list(filter(r.match, conv_list))
            return magnet_info
        except TimeoutExpired:
            call(['taskkill', '/F', '/T', '/PID',  str(process.pid)])
            input("Timeout. Press Enter to continue...")
            return None
    


def get_input_for_any(magnet,parsed_data,whichone):
    start=0
    end=10
    all=False
    while True:
        os.system('cls')
        if whichone=='link':
            print(convert_to_table_search(parsed_data[start:end]),'\n')
        elif whichone=='magnet':
            print(convert_to_table_magnet(parsed_data[start:end]),'\n')
        else:
            print(convert_to_table_history(parsed_data[start:end]),'\n')
        if all:
            ip=input(f"{len(parsed_data)} results found - Enter Index / Press Enter for next page / m for main / b for back / t for top level: ")
        else:
            ip=input(f"(Page {((start)//10)+1} / {((len(parsed_data)-1)//10)+1}) - Enter Index / Press Enter for next page / m for main / b for back / t for top level: ")
        
        direct_page=re.search(r'(\d+)p',ip)
        to_sort = re.search(r"s\s([a-z]+)", ip)
        downloads=re.findall(r'(\d+)d',ip)
        streams=re.findall(r'(\d+)\b',ip)

        if ip=='' and not all:
            if start+10<len(parsed_data):
                start+=10
        elif ip=='v':
            if all:
                end=start+10
                all=False
            else:
                start=0
                end=len(parsed_data)
                all=True
        elif ip=='m':
            start=0
        elif ip =='t':
            return ip
        elif ip=='b' and not all:
            if start-10>=0:
                start-=10
        elif (whichone=='link' and to_sort):
            if to_sort.group(1)=='size':
                parsed_data = sorted(parsed_data, key=lambda x: x[6],reverse=True)
            elif to_sort.group(1)=='seeds':
                parsed_data = sorted(parsed_data, key=lambda x: x[2],reverse=True)
            elif to_sort.group(1)=='peers':
                parsed_data = sorted(parsed_data, key=lambda x: x[3],reverse=True)
            else:
                continue
        elif whichone=='link' and ip.isdigit() and 0<int(ip)<=len(parsed_data[start:end]):
            link=parsed_data[start:end][int(ip)-1][5]
            return link
        elif whichone=='magnet':
            for i in downloads:
                if 0<int(i)<=len(parsed_data[start:end]):
                    current_file=re.match(r"(\d+)(.*)\((.*)\)", parsed_data[start:end][int(i)-1]).group(2).strip()
                    print(f"Downloading {current_file}")
                    os.system(f'start cmd /c webtorrent download -o {temp_dir} \"{magnet}\" --s {start+int(i)-1}')
            for i in streams:
                if 0<int(i)<=len(parsed_data[start:end]):
                    current_file=re.match(r"(\d+)(.*)\((.*)\)", parsed_data[start:end][int(i)-1]).group(2).strip()
                    print(f"Streaming {current_file}")
                    os.system(f'start cmd /c webtorrent --mpv -o {temp_dir} \"{magnet}\" --s {start+int(i)-1}')
            input("Press Enter to continue...")
        elif whichone=='history' and ip.isdigit() and 0<int(ip)<=len(parsed_data[start:end]):
                return parsed_data[int(ip)-1][2:]

        elif not all and direct_page and int(direct_page.group(1))<=len(parsed_data)//10:
            start=(int(direct_page.group(1))*10)-10
        else:
            continue
        if not all:
            end=start+10


def addToHistory(magnet,magnet_info):
    to_add=[urllib.parse.unquote(re.search(r"dn=([^&]*)",magnet).group(1)),datetime.now().strftime("%d-%m-%Y %H:%M:%S"),magnet,magnet_info]
    history=[]
    if not os.path.isfile("history_torrent.pkl"):
        pickle.dump(history,open("history_torrent.pkl","wb"))

    history=pickle.load(open("history_torrent.pkl","rb"))
    history=list(filter(lambda x:x[0]!=to_add[0],history))
    history.append(to_add)
    history=history[-100:]
    pickle.dump(history,open("history_torrent.pkl","wb"))

def get_magnet_from_torrent(magnet):
    metadata = bencodepy.decode(magnet)
    subj = metadata[b'info']
    hashcontents = bencodepy.encode(subj)
    digest = hashlib.sha1(hashcontents).digest()
    b32hash = base64.b32encode(digest).decode()
    return 'magnet:?'\
             + 'xt=urn:btih:' + b32hash\
             + '&dn=' + metadata[b'info'][b'name'].decode()\
             + '&tr=' + metadata[b'announce'].decode()\
             + '&xl=' + str(metadata[b'info'][b'piece length'])

while True:
    os.system('cls')
    name=input("Query / h for history: ").strip()
    if name=='h':
        while True:
            history=pickle.load(open("history_torrent.pkl","rb"))
            history.reverse()
            ip=get_input_for_any('',history,'history')
            if ip=='t':
                break
            else:
                ip=get_input_for_any(ip[0],ip[1],'magnet')
                if ip=='t':
                    continue
    elif not name.startswith('magnet') and len(name)>5:
        parsed_data=get_torrent_data(name)
        if len(parsed_data)==0:
            continue 
        while True:
            magnet=get_input_for_any('',parsed_data,'link')
            # print(magnet)
            if magnet=='t':
                break
            if not re.search(r'^magnet',magnet):
                res=requests.get(magnet, allow_redirects=False)
                if(int(res.headers.get('Content-Length')) > 0):
                    magnet=get_magnet_from_torrent(res.content)
                else:
                    res=requests.get(magnet,allow_redirects=False)
                    magnet=res.headers['Location']

            pyperclip.copy(magnet)
            magnet_info=get_magnet_info(magnet)
            if magnet_info:
                addToHistory(magnet,magnet_info)
                ip=get_input_for_any(magnet,magnet_info,'magnet')
                if ip=='t':
                    continue
            else:
                continue
    elif name.startswith('magnet'):
        magnet_info=get_magnet_info(name)
        if magnet_info:
            addToHistory(name,magnet_info)
            ip=get_input_for_any(name,magnet_info,'magnet')
            if ip=='t':
                continue
    else:
        continue


        
        