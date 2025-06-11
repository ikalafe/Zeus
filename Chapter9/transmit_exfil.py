import ftplib
import os
import socket
import win32file

def plain_ftp(docpath, server='192.168.xxx.xxx'):
    ftp = ftplib.FTP(server)
    ftp.login("anonymous", "anon@example.com")
    ftp.cwd('/pub/')
    ftp.storbinary("STOR" + os.path.basename(docpath), open(docpath, "rb"), 1024)
    ftp.quit()