import socket
import threading
import random

HOST = "0.0.0.0"
PORT = 5050
MAX_PLAYERS = 2
MIN_NUM, MAX_NUM = 1, 100
WIN_SCORE = 2  # 2 puan kazanan oyunu bitirir

clients = []
nicknames = []
scores = {}

target_number = None
game_started = False

def broadcast(message):
    for c in clients:
        try:
            c.send(message.encode("utf-8"))
        except:
            pass

def new_round():
    global target_number
    target_number = random.randint(MIN_NUM, MAX_NUM)
    broadcast(f"\n🎯 Yeni tur başladı! {MIN_NUM}-{MAX_NUM} arasında bir sayı tuttum. Tahmin edin!\n")

def check_winner():
    for nickname, score in scores.items():
        if score >= WIN_SCORE:
            broadcast(f"\n🏆 {nickname} oyunu kazandı! Skorlar: {scores}\n")
            return True
    return False

def handle(client, nickname):
    global game_started
    while True:
        try:
            msg = client.recv(1024).decode("utf-8")
            if not msg:
                break

            if not game_started:
                continue

            try:
                guess = int(msg)
            except ValueError:
                client.send("⚠️ Lütfen sayı gir.\n".encode("utf-8"))
                continue

            if guess == target_number:
                scores[nickname] += 1
                broadcast(f"🎉 {nickname} doğru bildi! (Toplam: {scores[nickname]} puan)\n")

                if check_winner():
                    broadcast("💀 Oyun sona erdi. Sunucu kapatılıyor.")
                    for c in clients:
                        c.close()
                    exit(0)

                new_round()
            elif guess < target_number:
                broadcast(f"{nickname} → {guess} 🔺 Daha büyük!")
            else:
                broadcast(f"{nickname} → {guess} 🔻 Daha küçük!")

        except:
            if client in clients:
                idx = clients.index(client)
                clients.remove(client)
                nickname = nicknames[idx]
                nicknames.remove(nickname)
                broadcast(f"{nickname} oyundan ayrıldı.")
            client.close()
            break

def start_server():
    global game_started
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"🎮 Sunucu başlatıldı. IP: {socket.gethostbyname(socket.gethostname())}:{PORT}")

    while True:
        client, address = server.accept()
        print(f"{address} bağlandı.")
        client.send("Kullanıcı adın: ".encode("utf-8"))
        nickname = client.recv(1024).decode("utf-8").strip()

        clients.append(client)
        nicknames.append(nickname)
        scores[nickname] = 0

        broadcast(f"✅ {nickname} oyuna katıldı! ({len(clients)}/{MAX_PLAYERS})")

        thread = threading.Thread(target=handle, args=(client, nickname))
        thread.start()

        if len(clients) == MAX_PLAYERS and not game_started:
            game_started = True
            broadcast(f"\n🎮 Oyun başladı! {MAX_PLAYERS} oyuncu bağlı.")
            new_round()

if __name__ == "__main__":
    start_server()

