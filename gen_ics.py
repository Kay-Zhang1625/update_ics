import os
import uuid
import json
from icalendar import Calendar, Event
from datetime import datetime, timezone, timedelta

def init_ics(json_file, ics_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        events = json.load(f)

    cal = Calendar()
    cal.add('prodid', '-//My Calendar Product//mxm.dk//')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'My Calendar')
    cal.add('x-wr-timezone', 'Asia/Taipei')

    tz = timezone(timedelta(hours=8))
    for e in events:
        event = Event()
        event.add('summary', e['title'])
        start_dt = datetime.strptime(f"{e['date']} {e['start_time']}", '%Y-%m-%d %H:%M').replace(tzinfo=tz)
        end_dt = datetime.strptime(f"{e['date']} {e['end_time']}", '%Y-%m-%d %H:%M').replace(tzinfo=tz)
        event.add('dtstart', start_dt)
        event.add('dtend', end_dt)
        event.add('dtstamp', datetime.now(timezone.utc))
        event.add('uid', str(uuid.uuid4()))
        cal.add_component(event)

    with open(ics_file, 'wb') as f:
        f.write(cal.to_ical())

    print(f"已建立 ics 檔: {ics_file}")

def sync_ics_with_json(json_path, ics_path, sync_mode):
    """
    sync_mode: "replace"（全面重建）或 "append"（只加新事件）或 None（不做事）
    """
    # 1. 讀取 json 所有事件
    with open(json_path, 'r', encoding='utf-8') as f:
        all_events = json.load(f)
    now = datetime.now()

    # 2. 依 sync_mode 處理
    if sync_mode == "init" or sync_mode == "replace":
        # 全面重建：歷史事件 + json 內所有未來事件
        cal = Calendar()
        cal.add('prodid', '-//My Calendar Product//mxm.dk//')
        cal.add('version', '2.0')
        cal.add('x-wr-calname', 'My Calendar')
        cal.add('x-wr-timezone', 'Asia/Taipei')

        for e in all_events:
          event = Event()
          event.add('summary', e['title'])
          tz = timezone(timedelta(hours=8))
          start_dt = datetime.strptime(f"{e['date']} {e['start_time']}", '%Y-%m-%d %H:%M').replace(tzinfo=tz)
          event.add('dtstart', start_dt)
          end_dt = datetime.strptime(f"{e['date']} {e['end_time']}", '%Y-%m-%d %H:%M').replace(tzinfo=tz)
          event.add('dtend', end_dt)
          event.add('dtstamp', datetime.now(timezone.utc))
          event.add('uid', str(uuid.uuid4()))
          cal.add_component(event)

        with open(ics_path, 'wb') as f:
            f.write(cal.to_ical())
        print("ICS has been created.")

    elif sync_mode == "append":
        # 只新增新事件到 ics
        # 讀取現有 ics
        try:
            with open(ics_path, 'rb') as f:
                cal = Calendar.from_ical(f.read())
        except FileNotFoundError:
            cal = Calendar()
            cal.add('prodid', '-//My Calendar Product//mxm.dk//')
            cal.add('version', '2.0')
            cal.add('x-wr-calname', 'My Calendar')
            cal.add('x-wr-timezone', 'Asia/Taipei')


        # 取得現有事件 key
        existing_keys = set()
        for component in cal.walk():
            if component.name == "VEVENT":
                title = str(component.get('summary'))
                start_dt = component.get('dtstart').dt
                key = f"{title}|{start_dt.strftime('%Y-%m-%d %H:%M')}"
                existing_keys.add(key)

        # 新增 json 中未來且尚未存在的事件
        tz = timezone(timedelta(hours=8))
        for e in all_events:
            key = f"{e['title']}|{e['date']} {e['start_time']}"
            start_dt = datetime.strptime(f"{e['date']} {e['start_time']}", '%Y-%m-%d %H:%M')
            if key not in existing_keys and start_dt > now:
                event = Event()
                event.add('summary', e['title'])
                event.add('dtstart', start_dt.replace(tzinfo=tz))
                end_dt = datetime.strptime(f"{e['date']} {e['end_time']}", '%Y-%m-%d %H:%M').replace(tzinfo=tz)
                event.add('dtend', end_dt)
                event.add('dtstamp', datetime.now(timezone.utc))
                event.add('uid', str(uuid.uuid4()))
                cal.add_component(event)
                print(f"新增事件到 ICS: {e['title']}({e['date']} {e['start_time']})")
        with open(ics_path, 'wb') as f:
            f.write(cal.to_ical())
        print("ICS 已 append 新事件。")

    else:
        print("ICS 無須更新。")
