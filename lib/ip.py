import requests
import time
from wasabi import Printer
try: from . import sql
except: import sql
try: from . import settings
except: import settings

msg = Printer()

def check(dbuser,device_id,app_id):
    old_ip = sql.q_ip()
    curr_ip = requests.get('https://api.ipify.org')
    while curr_ip.status_code != 200:
        time.sleep(30)
        string = "unable to connect to ipify.org, waiting 10 seconds"
        msg.fail(f'{settings.timeprefix()}{string}')
        sql.mysql_log(device_id, app_id,"HIGH","ERROR",string)
        curr_ip = requests.get('https://api.ipify.org')
    if old_ip != curr_ip.text:
        sql.u_ip(curr_ip.text,dbuser)
        return(True,old_ip,curr_ip.text)
    else:
        return(False,curr_ip.text)
