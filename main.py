from spider_goodtime import exe_crawler, update_json_with_crawler
from gen_ics import sync_ics_with_json

json_file = "events.json"
ics_file = "mycalendar.ics"

results = exe_crawler(wd, USERNAME, PASSWORD, url)
sync_mode = update_json_with_crawler(json_file, results)
sync_ics_with_json(json_file, ics_file, sync_mode)
