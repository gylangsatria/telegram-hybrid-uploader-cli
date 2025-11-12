from telethon.sync import TelegramClient
from dotenv import load_dotenv
from tqdm import tqdm
import requests
import os
import time

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
group_target = int(os.getenv("GROUP_TARGET"))

client = TelegramClient('bot', api_id=api_id, api_hash=api_hash)
client.start(bot_token=bot_token)

def upload_bot_api(full_path):
    with open(full_path, 'rb') as f:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendDocument",
            data={'chat_id': group_target},
            files={'document': f}
        )
    return response.status_code == 200, response.text

def upload_telethon(full_path):
    try:
        client.send_file(group_target, full_path)
        return True, "sent via Telethon"
    except Exception as e:
        return False, str(e)

def upload_folder(folder_path):
    print(f"🚀 Starting hybrid upload from: {folder_path}")
    
    all_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            all_files.append(full_path)

    for full_path in tqdm(all_files, desc="Uploading files", unit="file"):
        size_bytes = os.path.getsize(full_path)
        size_mb = size_bytes / (1024 * 1024)
        start = time.time()

        if size_mb <= 50:
            success, info = upload_bot_api(full_path)
            method = "Bot API"
        else:
            success, info = upload_telethon(full_path)
            method = "Telethon"

        end = time.time()
        elapsed = end - start
        kbps = (size_bytes * 8) / 1024 / elapsed if elapsed > 0 else 0

        if success:
            print(f"Uploaded: {os.path.basename(full_path)} via {method} — {size_mb:.2f} MB in {elapsed:.2f}s (~{kbps:.2f} kbps)")
            with open("upload.log", "a") as log:
                log.write(f"{full_path} | {size_mb:.2f} MB | {elapsed:.2f}s | {kbps:.2f} kbps | {method}\n")
        else:
            print(f"Failed: {os.path.basename(full_path)} — {info}")
            with open("error.log", "a") as err:
                err.write(f"{full_path} — {info}\n")

upload_folder("/media")

