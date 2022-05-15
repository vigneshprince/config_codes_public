from prettytable import PrettyTable, ALL
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import subprocess
import re
import io
import threading


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

suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']


def humansize(nbytes):
    nbytes = float(nbytes)
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']
stack_data = []
service = None
rclone_config = r"C:\Users\vigne\AppData\Roaming\rclone\rclone.conf"
GD_FOLDER_ID = '0AImUfJK1GLwMUk9PVA'


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('gdrive_cred\\token.pickle'):
        with open('gdrive_cred\\token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'gdrive_cred\\credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('gdrive_cred\\token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    global service
    service = build('drive', 'v3', credentials=creds)


color_index_mapping = {
    2: Colors.GREEN,
}

color_index_mapping_1 = {
    1: Colors.YELLOW,
    2: Colors.GREEN,
}


def to_color(li, mapping):
    return [mapping[i]+str(x)+Colors.END if i in mapping else str(x) for i, x in enumerate(li)]


def searcher():
    global stack_data
    while True:
        os.system('cls')
        name = input("File name or '@'+folder name: ")
        t1.join()
        if len(name.strip()) > 0:
            if name[0] != '@':
                stack_data.append(getFileByName(name))
            else:
                stack_data.append(getFolderByName(name))
            ret = ''
            while ret != 'h':
                ret = process_file_folder_input()


def getFileByName(name):
    q = f"mimeType contains 'video/' and trashed=false and fullText contains '{name}'"
    query = service.files().list(
        pageSize=1000,
        corpora="allDrives",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        fields="files/name,files/id,files/parents,files/mimeType,files/driveId,files/size",
        q=q
    ).execute()
    
    # change datatype of size in query['files']
    [x.update({'size': float(x['size'])}) for x in query['files']]
    return sorted(query['files'], key=lambda x:x['size'], reverse=True)


def getFolderByName(name):
    q = f"mimeType='application/vnd.google-apps.folder' and trashed=false and fullText contains '{name[1:]}'"

    query = service.files().list(
        pageSize=1000,
        corpora="allDrives",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        fields="files/name,files/id,files/parents,files/mimeType,files/driveId",
        q=q
    ).execute()
    return query['files']


def print_stack(data):
    os.system('cls')
    all_data = PrettyTable()
    all_data.hrules = ALL
    all_data.field_names = ["Index", "Title", "Size"]
    all_data._max_width = {"Index": 10, "Title": 70, "Size": 30}
    total_size = 0
    for i, item in enumerate(data, 1):
        # add row with color
        if "folder" in item['mimeType']:
            all_data.add_row(
                to_color([i, item['name'], ''], color_index_mapping_1))
        else:
            all_data.add_row(
                to_color([i, item['name'], humansize(item['size'])], color_index_mapping))
            total_size += int(item['size'])
    print(all_data, '\n')
    if total_size > 0:
        print(f"Total size: {humansize(total_size)}")


def process_file_folder_input():
    global stack_data
    start = 0
    end = 10
    all = False
    new_parentid = None
    new_parent_name=None
    while True:
        latest_stack = stack_data[-1]
        latest_stack_n = latest_stack[start:end]
        print_stack(latest_stack_n)
        ip_text="Enter Index \n  Index + 'c' for copy / Index + 'f' to get parent / Press Enter for next page  \n  m for main / b for back / t for top level / h for home \n  v to change view / Index + 'p'  to page / s name / s size to sort:"
        if all:
            ip = input(
                f"{len(latest_stack)} results found - {ip_text} ")
        else:
            ip = input(
                f"(Page {((start)//10)+1} / {((len(latest_stack)-1)//10)+1}) - {ip_text} ")

         # parse inputs
        direct_page = re.search(r'(\d+)p', ip)
        new_foldername = re.search(r"(folder_)(.*)\b", ip)
        to_copy_range = re.search(r"([0-9]+)-([0-9]+)c", ip)
        to_copy = re.findall(r"([0-9]+)c", ip)
        to_parent_folder = re.search(r"([0-9]+)f", ip)
        to_expand_folder = re.search("([0-9]+)", ip)
        to_sort = re.search(r"s\s([a-z]+)", ip)

        # create new folder if provided under folder_(name)
        if new_foldername:
            if(len(service.files().list(q=f"name='{new_foldername.group(2)}' and mimeType='application/vnd.google-apps.folder' and trashed=false", supportsAllDrives=True,corpora="allDrives",includeItemsFromAllDrives=True).execute()['files'])==0):
                new_parentid,new_parent_name = create_folder(new_foldername.group(2))
            else:
                input("Folder already exists...")  
                continue

        if ip == '' and not all:
            if start+10 < len(latest_stack):
                start += 10
        elif ip == 'v':
            if all:
                end = start+10
                all = False
            else:
                start = 0
                end = len(latest_stack)
                all = True
        elif ip == 'm':
            start = 0
        elif (to_sort):
            stack_data[-1] = sorted(stack_data[-1], key=lambda x: x[to_sort.group(1)])
        elif ip == 't':
            if len(stack_data) > 1:
                stack_data.pop()
                start = 0
                end = 10
            else:
                return 'h'
        elif ip == 'b' and not all:
            if start-10 >= 0:
                start -= 10
        elif ip == 'h':
            return ip

        elif(to_copy_range):
            for index in range(int(to_copy_range.group(1)), int(to_copy_range.group(2))+1):
                if index <= len(latest_stack_n):
                    copy_file_folder(latest_stack_n[index-1], new_parentid,new_parent_name)
                    new_parentid = None
                    new_parent_name = None
                else:
                    print(f"Invalid input {index}")
            input("Enter to continue")
        elif(to_copy):
            for item in to_copy:
                index = int(item)
                if index <= len(latest_stack_n):

                    copy_file_folder(latest_stack_n[index-1], new_parentid,new_parent_name)
                    new_parentid = None
                    new_parent_name = None
                else:
                    print(f"Invalid input {index}")
            input("Enter to continue")
        elif(to_parent_folder):
            index = int(to_parent_folder.group(1))
            if index <= len(latest_stack_n):
                get_folder_by_id(
                    latest_stack_n[index-1]['parents'][0])

        elif(to_expand_folder):
            index = int(to_expand_folder.group(1))
            if index <= len(latest_stack_n) and "folder" in latest_stack_n[index-1]['mimeType']:
                get_folder_by_id(latest_stack_n[index-1]['id'])

        elif not all and direct_page and int(direct_page.group(1)) <= len(latest_stack)//10:
            start = (int(direct_page.group(1))*10)-10
        else:
            continue

        if not all:
            end = start+10


def create_folder(name):
    file_metadata = {
        'name': name,
        'parents': [GD_FOLDER_ID],
        'mimeType': 'application/vnd.google-apps.folder'
    }

    folder_info = service.files().create(
        body=file_metadata, supportsAllDrives=True, fields='id,name').execute()
    return folder_info['id'],folder_info['name']


def get_folder_by_id(id):
    global stack_data
    q = f"'{id}' in parents and trashed=false"

    query = service.files().list(
        corpora="allDrives",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        pageSize=1000,
        fields="files/name,files/id,files/parents,files/mimeType,files/size",
        q=q
    ).execute()

    filelist = list(filter(
        lambda x: x['mimeType'] != 'application/vnd.google-apps.folder', query['files']))
    folderlist = list(filter(
        lambda x: x['mimeType'] == 'application/vnd.google-apps.folder', query['files']))
    [x.update({'size': float(x['size'])}) for x in filelist]
    stack_data.append([*filelist, *folderlist])


def copy_file_folder(file_folder, parentid=None,parent_name=None):
    print(f"Copying {file_folder['name']}")
    if "folder" in file_folder['mimeType']:
        with open(rclone_config, 'r') as f_read:
            content = f_read.readlines()
            with open(rclone_config, 'w') as f_write:
                for i, line in enumerate(content, 1):
                    if i == 15:
                        f_write.writelines(
                            f"root_folder_id = {file_folder['id']}\n")
                    else:
                        f_write.writelines(line)
        if not parent_name:
            with subprocess.Popen(f'rclone mkdir mystoshiv:"{file_folder["name"]}"', shell=True, stdout=subprocess.PIPE) as process:
                for line in process.stdout:
                    print(line.decode('utf8'))
        with subprocess.Popen(f'rclone -v copy mystotemp: mystoshiv:"{parent_name or file_folder["name"]}"', shell=True, stdout=subprocess.PIPE) as process:
            for line in process.stdout:
                print(line.decode('utf8'))
    else:
        # with open(rclone_config, 'r') as f_read:
        #     content=f_read.readlines()
        #     with open(rclone_config,'w') as f_write:
        #         for i,line in enumerate(content,1):
        #             if i == 15:
        #                 f_write.writelines(f"root_folder_id = {file_folder['parents'][0]}\n")
        #             else:
        #                 f_write.writelines(line)

        # with subprocess.Popen(f'rclone -v copy mystotemp:"{file_folder["name"]}" mystoshiv:',shell=True, stdout=subprocess.PIPE) as process:
        #     for line in process.stdout:
        #         print(line.decode('utf8'))
        parentid = parentid or GD_FOLDER_ID

        try:
            service.files().copy(
                fileId=file_folder["id"], supportsAllDrives=True, body={'name': file_folder['name'], 'parents': [parentid]}).execute()
            print(f"Transferred")
        except:
            print(f"Failed")


t1 = threading.Thread(target=main)
t1.start()
searcher()
