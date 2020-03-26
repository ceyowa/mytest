Win10:
Get-FileHash -Algorithm SHA1 D:\1.exe| format-list

win7：
CertUtil: -hashfile D:\1.exe SHA1
CertUtil: -hashfile D:\1.exe MD5