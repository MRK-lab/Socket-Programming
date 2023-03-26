'''
4. deneme başlıyorum
önce simetrik şifreleme yerine asimetrik yapacağım ve tüm simetrik kalıntılarını temizliyorum, listele kısmını da, serverdaki fonk kalıyor ama (kullanici_listesi)
şu anda şifrelemeyi bırakıp mesajlaşmayı yapıyorum
prototip hazır listelemeyi tekrar ekliyorum
şu anda bayağı yazmadım ama clentler aarası mesajlaşma hazır
sadece şifreleme yapılacak

5. prototipe başlıyorum
şifrelemeye bağlıuyorum
kişi seçimindde server koparsa program kapatsın ---------+++
public anahtar transferi yapılmıyordu durumu çözdüm ama serverda listelemektense pem uzantılı dosyadan almak daha mantıklı çünkü anahtar değişirse bile dinamikliği korur
yanlız şunu unutmamak lazım client kapanınca dosyayı sil ----------++

şu anda asimetrik şifreleme işlmei tamamlarndı
mesajlaşığıumız kisi kapatırsa mesaj döngüye giriyotr ------------++++


'''

import socket
import sys
import threading
import time
import rsa
from cryptography.fernet import Fernet
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import random
import os
import colorama
from colorama import Fore, Back, Style
colorama.init()

try:

    def green(metin):
        print(Fore.GREEN + metin + Style.RESET_ALL)

    def yellow(metin):
        print(Fore.YELLOW + metin + Style.RESET_ALL)

    def blue(metin):
        print(Fore.BLUE + metin + Style.RESET_ALL)

    def magenta(metin):
        print(Fore.MAGENTA + metin + Style.RESET_ALL)

    def white(metin):
        print(Fore.WHITE+ metin + Style.RESET_ALL)

    renk_kodu = random.randint(0,4)


    # sesimi dinlemek için değişken oluşturdum
    r=sr.Recognizer()

    #simetrik şifreleme
    key = Fernet.generate_key()
    fernet = Fernet(key)

    #asimetrik şifreleme
    publicKey, privateKey = rsa.newkeys(512)



    try:
        print("Sunucuya Bağlanıyor...")
        client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        host = socket.gethostbyname(socket.gethostname())
        client.connect((host,6000))
        print()
    except:
        print("\a",Fore.RED+"[HATA]~ Bağlantı Hatası"+Style.RESET_ALL)
        sys.exit()

    kontrol = 0
    while kontrol == 0:
        nickname = input(Fore.CYAN + "Kullanıcı adınız: " + Style.RESET_ALL)
        if nickname == "" or len(nickname) <= 2:
            print(Fore.RED + "Nickname en az 3 karakter olması gerekiyor." + Style.RESET_ALL)
        else:
            kontrol = 1

    FORMAT = 'utf-8'

    dosya_ismi=nickname+".pem"
    with open(dosya_ismi, "wb") as f:
        f.write(publicKey.save_pkcs1("PEM"))

    kisi_secimi_bool=False
    global sesli_dinleme
    sesli_dinleme=0

    def record():
        with sr.Microphone() as source:
            audio = r.listen(source, phrase_time_limit=3)
            voice=""
            try:
                voice = r.recognize_google(audio, language="tr-TR")
            except sr.UnknownValueError:
                return False
            except sr.RequestError:
                return False
            return voice

    def speak(string):
        tts=gTTS(string,lang="tr")
        rand=random.randint(1,10000)
        file="audio-"+str(rand)+".mp3"
        tts.save(file)
        playsound(file)
        os.remove(file)

    def dinle_kontrol():
        x=0
        while x==0:
            print(Fore.CYAN)
            gonder = input("Gönder: Enter / Tekrar sesimi dinle: l / Çıkış: ç = ")
            print(Style.RESET_ALL)
            if gonder == "l":
                return "/l"
            elif gonder == "":
                return True
            elif gonder=="ç":
                return False
            else:
                x=1

    def dinle():
        global x
        x=0
        while x==0:
            print(Fore.CYAN+"Dinliyor..."+Style.RESET_ALL)
            voice = record()
            if voice:
                print(voice)
                cevap=dinle_kontrol()
                if cevap==False:
                    return False
                elif cevap=="/l":
                    x=0
                else:
                    x=1
                    return voice
            else:
                print(Fore.RED+"Anlaşılmadı tekrar söyleyin..."+Style.RESET_ALL)

    def receive():
        while True:
            global kisi_secimi_bool,sesli_dinleme,renkler
            try:
                message=client.recv(1024).decode(FORMAT)
                if message =="NICK":
                    client.send(nickname.encode(FORMAT))
                elif message=="Kullanıcı Yok":
                    print(Fore.RED+"Kullanıcı Yok !!!"+Style.RESET_ALL)
                    kisi_secimi_bool=False
                elif message=="Kullanıcı var":
                    print(Fore.GREEN+"Bağlanıyor... ✓"+Style.RESET_ALL)
                    kisi_secimi_bool=True
                elif message=="/mesaj":
                    anahtar=client.recv(1024)
                    message2 = client.recv(1024)
                    anahtar = rsa.decrypt(anahtar, privateKey)
                    fernet2 = Fernet(anahtar)
                    message2 = fernet2.decrypt(message2).decode()
                    playsound("gelen mesaj.mp3")
                    x = message2.split(": ",1)
                    y=x[1].split(":",1)
                    message2=x[0]+": "+y[0]
                    oku=y[0]
                    renk_kodu=y[1]
                    renk_kodu=int(renk_kodu)
                    if(renk_kodu==0):
                        green(message2)
                    elif(renk_kodu==1):
                        yellow(message2)
                    elif (renk_kodu==2):
                        blue(message2)
                    elif (renk_kodu==3):
                        magenta(message2)
                    elif (renk_kodu==4):
                        white(message2)
                    else:
                        print(Fore.RED+"[HATA]~ Mesaj yazdırma hatası",)
                    if sesli_dinleme==1:

                        gonderen=x[0]
                        string=f"{gonderen} kişisinden mesaj"
                        try:
                            speak(string)
                            speak(oku)
                        except:
                            print(Fore.RED+"Sesli okumada hata.\n"
                                  "İnternet bağlantısını kontrol edin."+Style.RESET_ALL)
                            continue
                else:
                    print(Fore.GREEN+message+Style.RESET_ALL)
            except:
                print(Fore.RED+"[HATA]~ Alıcı kısmında hata!"+Style.RESET_ALL)
                client.close()
                break


    def kisi_secimi(client):
        global kisi_secimi_bool, sesli_dinleme
        while kisi_secimi_bool == False:
            print("\n")
            client.send("/list".encode(FORMAT))
            time.sleep(1)
            print(Fore.CYAN)
            alici = input("Mesaj göndermek istediğiniz kişiyi seçin\n~Çevrimiçi kullanıcıları listelemek için (Enter):\n")
            print(Style.RESET_ALL)
            if alici=="/a":
                sesli_dinleme=1
                continue
            elif alici=="/s":
                sesli_dinleme=0
                continue
            if alici=="":
                continue
            elif alici==nickname:
                speak("Kendinize mesaj gönderemezsiniz")
                continue
            alici2 = "/alici: " + alici
            client.send("/alici".encode(FORMAT))
            client.send(alici2.encode(FORMAT))
            time.sleep(1)
            if kisi_secimi_bool==True:
                return alici

    def alici_public_key(alici):
        global kisi_secimi_bool
        try:
            with open(alici+".pem","rb") as f:
                return rsa.PublicKey.load_pkcs1(f.read())
        except:
            print(Fore.RED+"Alıcı genel anahtarına erişilemedi.\n"
                  "Göndermek isteğiniz kişiyi tekrar seçmeniz gerekmektedir."+Style.RESET_ALL)
            kisi_secimi_bool=False


    def write():
        global kisi_secimi_bool,sesli_dinleme
        print(Fore.CYAN+"NOT: Gönderilen mesajların sesli okunması için: /a\n"
              "kapatmak için: /s\n"
		"Sesli mesaj göndermek için: /l\n"+Style.RESET_ALL)
        while True:
            if kisi_secimi_bool==False:
                alici=kisi_secimi(client)

            alici_public_key2=alici_public_key(alici)
            #print("alici public key: ",alici_public_key2)

            message1=nickname+": "
            message2=f'{input("")}'
            message=message1+message2
            if message2=="/çıkış":
                kisi_secimi_bool=False
                continue
            elif message2 == "/list":
                client.send(message2.encode(FORMAT))
            elif message2=="/a":
                sesli_dinleme=1
                continue
            elif message2=="/s":
                sesli_dinleme=0
                continue
            elif message2=="/l":
                cevap=dinle()
                if cevap==False:
                    continue
                else:
                    if kisi_secimi_bool == False:
                        continue

                    client.send("/mesaj".encode(FORMAT))

                    message2=cevap
                    message = message1 + message2
                    message = message + f":{str(renk_kodu)}"
                    message = fernet.encrypt(message.encode())
                    anahtar = rsa.encrypt(key, alici_public_key2)

                    client.send(alici.encode(FORMAT))
                    client.send(message)
                    time.sleep(0.2)
                    client.send(anahtar)
                    time.sleep(0.25)
            else:
                if kisi_secimi_bool==False:
                    continue
                client.send("/mesaj".encode(FORMAT))

                message=message+f":{str(renk_kodu)}"
                message = fernet.encrypt(message.encode())
                anahtar = rsa.encrypt(key, alici_public_key2)


                client.send(alici.encode(FORMAT))
                client.send(message)
                time.sleep(0.2)
                client.send(anahtar)
                time.sleep(0.25)

                playsound("gonderilen mesaj.mp3")

    receive_thread=threading.Thread(target=receive)
    receive_thread.start()

    write_thread=threading.Thread(target=write)
    write_thread.start()

except:
    print("\a[HATA]~ Program işleyişinde hata oluştu\n"
          "Tekrar dene")