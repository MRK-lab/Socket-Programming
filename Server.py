import socket
import threading
import time
import os
import colorama
from colorama import Fore, Back, Style

port=6000
FORMAT = 'utf-8'

try:
    host = socket.gethostbyname(socket.gethostname())
    print("Server bağlandığı IP adresi:",host,"\n\n")
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((host,port))
    server.listen()

    clients=[]
    nicknames=[]

    def broadcast(message): # herkese mesaj gönderme kısmı
        for client in clients:
            client.send(message)

    def kullanici_listesi(client):
        online_list = ""
        i = 0
        while i != len(nicknames):
            if i == 0:
                online_list = nicknames[0]
            else:
                online_list = online_list + ", " + nicknames[i]
            i = i + 1
        online_list = "Çevrimiçi Kullanıcılar: " + online_list
        client.send(online_list.encode(FORMAT))


    def mesjlasma(message,alici,gonderici_client,anahtar):
        index_alici=-1
        j=0
        for i in nicknames:
            if i==str(alici):
                index_alici=j
            j=j+1
        if index_alici==-1:
            gonderici_client.send("Kullanıcı Yok".encode(FORMAT))
        else:
            alici_client=clients[index_alici]
            alici_client.send("/mesaj".encode(FORMAT))
            alici_client.send(anahtar)
            time.sleep(0.2)
            alici_client.send(message)

    def online_mi(alici,client):
        index_alici = -1
        j = 0
        for i in nicknames:
            if i == str(alici):
                index_alici = j
            j = j + 1
        if index_alici == -1:
            client.send("Kullanıcı Yok".encode(FORMAT))
        else:
            client.send("Kullanıcı var".encode(FORMAT))

    def handle(client):
        while True:
            try:
                msg = client.recv(1024).decode(FORMAT)
                # print("mesaj: ",msg)
                if msg=="/list":
                    kullanici_listesi(client)
                elif msg=="/alici":
                    msg2=client.recv(1024).decode(FORMAT)
                    msg2=msg2[8:]
                    online_mi(msg2,client)
                elif msg=="/mesaj":
                    alici = client.recv(1024).decode(FORMAT)
                    mesaj=client.recv(1024)
                    anahtar=client.recv(1024)
                    mesjlasma(mesaj,alici,client,anahtar)
                    #broadcast(message)
            except:
                index=clients.index(client)
                clients.remove(client)
                client.close()
                nickname=nicknames[index]
                print(Fore.RED+f"{nickname} bağlantıdan ayrıldı!"+Style.RESET_ALL) # herkese ayrılan kişiyi söylüyor
                dosya=nickname+".pem"
                try:
                    os.remove(dosya)
                except:
                    print(Fore.RED+"Dosya bulunamadı"+Style.RESET_ALL)
                nicknames.remove(nickname)
                break

    def receive():
        while True:
            client,address=server.accept()
            print(Fore.CYAN+f"Bağlandı: {str(address)}"+Style.RESET_ALL)

            client.send("NICK".encode(FORMAT))
            nickname=client.recv(1024).decode(FORMAT)
            nicknames.append(nickname)
            clients.append(client)

            print(Fore.CYAN+f"Bağlanan takma ad: {nickname}!"+Style.RESET_ALL)
            #broadcast(f"{nickname} joined the chat!".encode(FORMAT)) # herkses katılan kişiyi söylüyor
            client.send("Sunucu bağlantısı kuruldu!".encode(FORMAT))
            time.sleep(0.5)

            thread=threading.Thread(target=handle, args=(client,))
            thread.start()

    print(Fore.CYAN+"Bağlantı Dinleniyor..."+Style.RESET_ALL)
    receive()

except:
    print("\a[HATA]~ Program işleyişinde hata oluştu\n"
          "Tekrar dene")