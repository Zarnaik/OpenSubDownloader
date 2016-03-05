from subprocess import check_output
from xmlrpclib import Server

series = check_output('cd ~/Downloads/Torrents/SERIES && zenity --file-selection --multiple', shell=True).rstrip().split("|")


server = Server()