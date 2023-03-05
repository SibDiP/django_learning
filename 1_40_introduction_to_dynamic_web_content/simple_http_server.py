from socket import *

def createServer():
    serversocket = socket(AF_INET, SOCK_STREAM)

    try:
        # 1. The bind() method of Python's socket class assigns
        # an IP address and a port number to a socket instance.
        # 2. The bind() method is used when a socket needs to be
        # made a server socket.
        # 3. As server programs listen on published ports, it is
        # required that a port and the IP address to be assigned
        # explicitly to a server socket.
        serversocket.bind(('localhost', 9000))
        # .listen(n) n - amount of connection in queue
        serversocket.listen(5)
        while(1):
            # .accept() - wait untill client .connect
            # code will go futher only after connect
            (clientsocket, address) = serversocket.accept()

            # argument - buf_size
            rd = clientsocket.recv(5000).decode()
            #\n - отделяет первую строку с запросом (GET...)
            pieces = rd.split("\n")
            if (len(pieces) > 0) : print(pieces[0])

            data = "HTTP/1.1 200 OK\r\n"
            data += "Content-Type: text/html; charset=utf-8\r\n"
            data += "\r\n"
            data += "<html><body>Hello World</body></html>\r\n"
            clientsocket.sendall(data.encode())
            clientsocket.shutdown(SHUT_WR)

    except KeyboardInterrupt:
        print("\nShutting down...\n")
    except Exception as exc:
        print("Error:\n")
        print(exc)

    serversocket.close()

print('Access http://localhost:9000')
createServer()

