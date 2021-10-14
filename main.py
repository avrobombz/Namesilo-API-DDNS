import os
import json
import time
from lib import settings
from lib import sql
from lib import namesilo
from lib import ip
from wasabi import Printer

cwd = os.getcwd()
jsonconf = cwd + '/config.json'

msg = Printer()

with open(jsonconf, 'r') as datajson:
    data_2 = json.load(datajson)
APP_ID = data_2['APP_DATA']['app_id']
msg.divider(f"running {APP_ID} ")

try:
    while True:
        #------------------------pull config
        seconds = int(sql.q_appconfig(APP_ID)['SECONDS'])
        api_key = sql.q_appconfig(APP_ID)['API_KEY']
        domain = sql.q_appconfig(APP_ID)['DOMAIN']
        device_id = sql.q_appconfig(APP_ID)['DEVICE_ID']

        #------------------------pull DNS log via API and store results
        q_dns_namesilo = namesilo.q_dns_namesilo(api_key,domain,device_id,APP_ID)
        #------------------------pull DB DNS log via SQL and store results
        sql_dns_list = sql.q_dns_list()

        #storage slotting
        connected = q_dns_namesilo[0]
        dictionary = q_dns_namesilo[1]
        resource = q_dns_namesilo[2]

        if connected: #------------------------Do checks
            ipr = ip.check(device_id,device_id,APP_ID) #------------------------Check if Local IP has changed
            namesilo.u_dns_db(device_id,sql_dns_list,APP_ID,dictionary,connected,resource, domain)
            
            if ipr[0]:#ip[0]------------------------If Local IP has changed, update DNS where domains have old_ip
                old_ip = ipr[1]
                curr_ip = ipr[2]
                string = f'IP has changed from {old_ip} to {curr_ip}'
                msg.warn(f'{settings.timeprefix()}{string}')
                sql.mysql_log(device_id, APP_ID,"LOW","WARN",string)
                msg.warn(f'{settings.timeprefix()}Performing update to DNS')
                namesilo.u_dns_namesilo(curr_ip,old_ip,api_key,device_id,APP_ID)
                #------------------------Pull Fresh DNS afer update
                q_dns_namesilo = namesilo.q_dns_namesilo(api_key,domain,device_id,APP_ID)
                connected = q_dns_namesilo[0]
                dictionary = q_dns_namesilo[1]
                resource = q_dns_namesilo[2]

            #------------------------Sync DB to DNS
                namesilo.u_dns_db(device_id,sql_dns_list,APP_ID,dictionary,connected,resource, domain)
                    
            #------------------------Print pulled records
                msg.info(f'{settings.timeprefix()}# of records in DNS:DB | {len(resource)}:{len(sql_dns_list)}')
                msg.info(f'{settings.timeprefix()}{string}')
                sql.mysql_log(device_id, APP_ID,"LOW","WARN",string)
        else:
            msg.fail(f"{settings.timeprefix()}Unable to connect or there was an error, will try again in {seconds} seconds")
        time.sleep(seconds)
except Exception as e:
    print(e)
    with open("error.log", "a") as logfile:
        logfile.write(settings.timeprefix() + str(e) + "\n")
    sql.mysql_log(device_id, APP_ID,"HIGH","ERROR",str(e))    
