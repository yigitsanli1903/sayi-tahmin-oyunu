from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

target_number = random.randint(1, 100)
print(f"[INFO] Secret number is {target_number}")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('New player connected')
    emit('message', {'msg': 'Sayı tahmin oyununa hoş geldin! (1-100 arasında bir sayı tutuyorum.)'})

@socketio.on('guess')
def handle_guess(data):
    global target_number
    guess = int(data['guess'])
    if guess < target_number:
        emit('message', {'msg': 'Daha büyük bir sayı söyle!'}, broadcast=True)
    elif guess > target_number:
        emit('message', {'msg': 'Daha küçük bir sayı söyle!'}, broadcast=True)
    else:
        emit('message', {'msg': f'Tebrikler! {guess} doğru tahmin! 🎉 Yeni sayı tutuldu.'}, broadcast=True)
        target_number = random.randint(1, 100)
        print(f"[INFO] Yeni sayı: {target_number}")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
