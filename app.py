from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import io
import time
import hashlib
import json
import numpy as np
import cv2
from collections import defaultdict
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials
from flask_socketio import SocketIO, emit

app = Flask(__name__, static_folder='/Users/yoonmo/Desktop/bee 2/image_folder')
socketio = SocketIO(app)

IMAGE_FOLDER = '/Users/yoonmo/Desktop/bee 2/image_folder'
app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER
app.config['SECRET_KEY'] = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

users = {'testuser': {'password': 'testpassword'}}  # 예시 사용자 데이터

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('home'))  # 'index'를 'home'으로 수정
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def group_images_by_date(image_names):
    images_by_date = defaultdict(list)
    for image_name in image_names:
        date_key = image_name[:4]  # 날짜 부분만 사용하여 키 생성 (예: 240702)
        images_by_date[date_key].append(image_name)
    return images_by_date

def calculate_flew_away(images, loaded_data):
    cumulative_flew_away = 0
    for image_name in images:
        img_base_name = image_name[:-6]  # 이미지 파일 이름에서 베이스 이름 추출
        prev_bee = int(loaded_data.get(f'{img_base_name}_prev_bee', 0))
        now_bee = int(loaded_data.get(f'{img_base_name}_now_bee', 0))
        flew_away = max(0, prev_bee - now_bee)
        cumulative_flew_away += flew_away
    return int(cumulative_flew_away / 4)  # 조금 이상함, 나중에 수정 필요

# 홈 페이지 라우트
@app.route('/', methods=['GET', 'POST'])
def home():
    search_query = request.args.get('search')  # 검색 쿼리 가져오기

    image_names = os.listdir(app.config['UPLOAD_FOLDER'])
    image_names_filtered = [file for file in image_names if file.lower().endswith('.jpg')]
    image_names_sorted = sorted(image_names_filtered)

    # 검색 쿼리가 있는 경우 필터링
    if search_query:
        search_results = [image_name for image_name in image_names_sorted if search_query in image_name]
    else:
        search_results = image_names_sorted

    images_by_date = group_images_by_date(search_results)

    loaded_data = {}
    with open('/Users/yoonmo/Desktop/bee 2/data.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            key, value = line.strip().split(': ')
            loaded_data[key] = value

    flew_away_by_date = {}
    for date, images in images_by_date.items():
        flew_away_by_date[date] = calculate_flew_away(images, loaded_data)

    return render_template('index.html', images_by_date=images_by_date, flew_away_by_date=flew_away_by_date, loaded_data=loaded_data)

@app.route('/details/<date>', methods=['GET'])
def details(date):
    image_names = os.listdir(app.config['UPLOAD_FOLDER'])
    image_names_filtered = [file for file in image_names if file.lower().endswith('.jpg') and file.startswith(date)]
    image_names_sorted = sorted(image_names_filtered)

    loaded_data = {}
    with open('/Users/yoonmo/Desktop/bee 2/data.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            key, value = line.strip().split(': ')
            loaded_data[key] = int(value)

    group_flew_away_data = []
    cumulative_flew_away = 0
    image_groups = [image_names_sorted[i:i + 4] for i in range(0, len(image_names_sorted), 4)]
    
    for group in image_groups:
        if len(group) < 4:
            continue  # 이미지가 4개 미만인 경우 스킵
        img_base_name = group[0][:-6]  # 이미지 파일 이름에서 베이스 이름 추출
        prev_bee = loaded_data.get(f'{img_base_name}_prev_bee', 0)
        now_bee = loaded_data.get(f'{img_base_name}_now_bee', 0)
        flew_away = max(0, prev_bee - now_bee)
        cumulative_flew_away += flew_away
        group_data = {
            'images': group,
            'prev_bee': prev_bee,
            'now_bee': now_bee,
            'flew_away': flew_away,
            'cumulative_flew_away': cumulative_flew_away
        }
        group_flew_away_data.append(group_data)

    total_flew_away = cumulative_flew_away

    return render_template('details.html', group_flew_away_data=group_flew_away_data, total_flew_away=total_flew_away, date=date)

@app.route('/about')
def about():
    return render_template('about.html')

# 연락처 페이지 라우트
@app.route('/contact')
def contact():
    return render_template('contact.html')

def sync_google_drive():
    folder_id = '1W1euK9YTOnxplEsmCK6WahxiHRK6Z7KP'
    json_file = '/Users/yoonmo/Desktop/bee 2/bee1.json'  # 경로를 로컬 경로로 수정

    with open(json_file, 'r') as f:
        credentials_data = json.load(f)

    creds = Credentials.from_service_account_info(credentials_data)
    drive_service = build('drive', 'v3', credentials=creds)

    hash_file_path = '/Users/yoonmo/Desktop/bee 2/downloaded_files_hashes.txt'

    # 기존에 다운로드된 파일 해시값을 로드
    if os.path.exists(hash_file_path):
        with open(hash_file_path, 'r') as hash_file:
            downloaded_files_hashes = set(hash_file.read().splitlines())
    else:
        downloaded_files_hashes = set()

    while True:
        results = drive_service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields='files(id, name, createdTime)',
            orderBy='createdTime desc',
        ).execute()
        files = results.get('files', [])

        for file in files:
            file_name = file['name']

            if file_name.endswith('.npy'):
                print('Processing', file_name)

                request = drive_service.files().get_media(fileId=file['id'])
                io_bytes = io.BytesIO()
                downloader = MediaIoBaseDownload(io_bytes, request)
                done = False

                while not done:
                    status, done = downloader.next_chunk()

                io_bytes.seek(0)
                file_hash = hashlib.md5(io_bytes.getvalue()).hexdigest()

                if file_hash not in downloaded_files_hashes:
                    downloaded_files_hashes.add(file_hash)

                    try:
                        image_data = np.load(io.BytesIO(io_bytes.getvalue()), allow_pickle=True)
                        image_list = image_data.tolist()

                        for i in range(4):
                            image = np.array(image_list[i], dtype=np.uint8)
                            image_file_path = os.path.join(IMAGE_FOLDER, f'{file_name[:-4]}_{i}.jpg')
                            cv2.imwrite(image_file_path, image)

                        with open('/Users/yoonmo/Desktop/bee 2/data.txt', 'a') as data_file:
                            data_file.write(f'{file_name[:-4]}_prev_bee: {int(image_list[4])}\n')
                            data_file.write(f'{file_name[:-4]}_now_bee: {int(image_list[5])}\n')

                        with open(hash_file_path, 'a') as hash_file:
                            hash_file.write(file_hash + '\n')

                        socketio.emit('new_image', {'date': file_name[:6]})
                        print('Saved files for', file_name[:-4])
                    except Exception as e:
                        print(f'Error processing {file_name}: {e}')
                else:
                    print('Skipping', file_name)

        print('Sleeping for 5 seconds')
        time.sleep(5)

if __name__ == '__main__':
    from threading import Thread

    # Google Drive 동기화를 별도의 스레드에서 시작
    drive_sync_thread = Thread(target=sync_google_drive)
    drive_sync_thread.daemon = True
    drive_sync_thread.start()

    # Flask 애플리케이션 시작
    socketio.run(app, debug=True)
