import socket

mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mysock.connect(('data.pr4e.org', 80))
# .encode() - Python data is in Unicode. Need to encode to UTF-8
cmd = 'GET http://data.pr4e.org/page1.htm HTTP/1.0\r\n\r\n'.encode()
# Headers after first 'n'
# cmd = 'GET http://data.pr4e.org/page1.htm HTTP/1.0\r\n \
# User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0\r\n\r\n'.encode()
mysock.send(cmd)

while True:
    # .recv() will wait until server answer
    data = mysock.recv(512)
    if len(data) < 1:
        break
    print(data.decode(), end='')

mysock.close()
