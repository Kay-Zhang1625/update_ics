import re
import json
import time
import os
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import datetime

# 載入帳號密碼
USERNAME = os.environ.get("CRAWLER_USERNAME")
PASSWORD = os.environ.get("CRAWLER_PASSWORD")

# Selenium 設定
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-dev-shm-usage")
wd = webdriver.Chrome(options=chrome_options)

url ='https://17fit.com/account/login?show_fb=1&show_line=1&show_17fit=1&success_url=https%3A%2F%2Fgoodtime.17fit.com%2Fauthorization%2Fjwt%3Fsuccess_url%3Dhttps%3A%2F%2Fgoodtime.17fit.com%2Fstudios%3FopenExternalBrowser%3D1&fail_url=https%3A%2F%2Fgoodtime.17fit.com%2Fstudios%3FopenExternalBrowser%3D1&cancel_url=https%3A%2F%2Fgoodtime.17fit.com%2Fstudios%3FopenExternalBrowser%3D1'

def exe_crawler(wd, USERNAME, PASSWORD, url):
    try:
        wd.get(url)
        time.sleep(2)

        # 1. 輸入帳號
        username_input = wd.find_element(By.CSS_SELECTOR, 'input.st-mb-0.st-text-black.st-p-3.st-w-full')
        username_input.send_keys(USERNAME)

        # 2. 點擊「下一步」按鈕
        next_btn = wd.find_element(By.TAG_NAME, "button")
        next_btn.click()
        time.sleep(2)

        # 3. 輸入密碼
        password_input = wd.find_element(By.CSS_SELECTOR, 'input[type="password"].st-mb-0.st-text-black.st-p-3.st-w-full')
        password_input.send_keys(PASSWORD)

        # 4. 點擊「登入」按鈕
        login_btn = wd.find_element(By.TAG_NAME, "button")
        login_btn.click()
        time.sleep(3)

        if "login_success" in wd.current_url:
            print("登入成功！")

        # 5. 進入課程頁面
        wd.get("https://goodtime.17fit.com/my-class")
        time.sleep(2)
        html = wd.page_source

        # 6. 取得課程資訊
        soup = BeautifulSoup(html, "html.parser")
        records = soup.find('div', id='unfinish').select(".row.record")

        courses = []
        for record in records:
            cols = record.select('.col-xs-8 > .col-sm-3.col-xs-12')
            raw_date = cols[0].get_text(strip=True)
            raw_time = cols[1].get_text(strip=True)
            title = cols[3].get_text(strip=True)

            # 資料清洗
            date = re.findall(r'\d{4}-\d{2}-\d{2}', raw_date)[0]
            time_list = re.findall(r'\d{2}:\d{2}', raw_time)
            start_time, end_time = time_list

            course = {
                'date': date,
                'start_time': start_time,
                'end_time': end_time,
                'title': title
            }
            courses.append(course)

        return courses

    except Exception as e:
        print("錯誤：", e)
    finally:
        wd.quit()

def event_key(event):
    return f"{event['date']}|{event['start_time']}|{event['title']}"

def update_json_with_crawler(json_path, crawler_events):
    global sync_mode

    if not os.path.exists(json_path):
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(crawler_events, f, indent=2)
        sync_mode = "init"
        print("已建立 json 資料。")
    else:
        with open(json_path, "r", encoding="utf-8") as f:
            json_events = json.load(f)

        now = datetime.now()
        future_json_events = [e for e in json_events if datetime.strptime(f"{e['date']} {e['start_time']}", '%Y-%m-%d %H:%M') > now]
        future_json_keys = set(event_key(e) for e in future_json_events)
        crawler_keys = set(event_key(e) for e in crawler_events)
        new_events = [e for e in crawler_events if event_key(e) not in future_json_keys]
        cancelled_events = [e for e in future_json_events if event_key(e) not in crawler_keys]

        updated = False

        # 1. 先判斷取消（replace）
        if cancelled_events:
            # 只保留歷史事件 + crawler_events
            history_events = [e for e in json_events if datetime.strptime(f"{e['date']} {e['start_time']}", '%Y-%m-%d %H:%M') <= now]
            json_events = history_events + crawler_events
            updated = True
            sync_mode = "replace"
            print(f"發現 {len(cancelled_events)} 筆已取消事件，json 資料已更新。")
        # 2. 若無取消事件，再判斷是否有新事件（append）
        elif new_events:
            json_events.extend(new_events)
            updated = True
            sync_mode = "append"
            print(f"發現 {len(new_events)} 筆新事件，json 資料已更新。")
        else:
            sync_mode = None
            print("json 資料與上次相同，無更新。")

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_events, f, indent=2)

    return sync_mode
