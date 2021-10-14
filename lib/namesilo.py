import xmltodict
import requests
import time
import json
from wasabi import Printer
from . import sql
try: from . import settings
except: import settings

msg = Printer()

def q_dns_namesilo(api_key, domain_name, device_id, app_id): #pulls DNS records from namesilo API
    url_start = 'https://www.namesilo.com/apibatch/dnsListRecords?version=1&type=xml&key='
    url_domain = '&domain='
    url = url_start + api_key + url_domain + domain_name
    r = None
    while r is None:
        try:
            r = requests.get(url)
        except Exception as e:
            msg.fail(settings.timeprefix() + str(e) + "\n")
            with open("error.log", "a") as logfile:
                logfile.write(settings.timeprefix() + str(e) + "\n")
            sql.mysql_log(device_id, app_id,"HIGH","ERROR",str(e))
            time.sleep(60)
            pass
        if r.status_code != 200:
            string = (f'status code = {r.status_code()}')
            msg.fail(f'{settings.timeprefix()}{string}')
            with open("error.log", "a") as logfile:
                logfile.write(f'{settings.timeprefix()}{string}' + "\n")
            sql.mysql_log(device_id, app_id,"HIGH","ERROR",string)
            time.sleep(60)
            r = None
    try:
        dictionary = xmltodict.parse(r.text)
        connected = dictionary['namesilo']['reply']['code'] == '300'
    except Exception as e:
        with open(time.strftime("xml_parse_record-%Y_%m_%d-%H%M%S.xml"), 'x') as errorfile:
            errorfile.write(r.text)
        string = f"XML Parse Error: dumping xml data to file - {e}"
        msg.fail(f"{settings.timeprefix()}{string}")
        sql.mysql_log(device_id, app_id,"HIGH","ERROR",string)
        connected = False
        time.sleep(60)
            
    try:
        if(connected):
            resource = dictionary['namesilo']['reply']['resource_record']
    except KeyError as ke:
        with open(time.strftime("json_resource_record-%Y_%m_%d-%H%M%S.json"), 'x') as errorfile:
            errorwrite = json.dump(dictionary,errorfile, indent=4)
        string = f"KeyError: dumping json data to file - {ke}"
        msg.fail(f"{settings.timeprefix()}{string}")
        sql.mysql_log(device_id, app_id,"HIGH","ERROR",string)
        connected = False
        time.sleep(60)

    return(connected,dictionary,resource)

def u_dns_db(device_id, sql_dns_list, app_id, dictionary, connected, resource, domain_name): #updates DB if new record in DNS/DNS Modified
    
    if connected:
        a = {}
        sql_dns_list_rrid = []
        ns_dns_list_rrid = []

        for i in range(len(sql_dns_list)):
            sql_dns_list_rrid.append(sql_dns_list[i]['rrid'])
        for i in range(len(resource)):
            try: ns_dns_list_rrid.append(resource[i]['record_id'])
            except: pass
        
        for i in range(len(resource)):
            a['record'] = dictionary['namesilo']['reply']['resource_record'][i]['record_id']
            a['host'] = dictionary['namesilo']['reply']['resource_record'][i]['host']
            a['ip'] = dictionary['namesilo']['reply']['resource_record'][i]['value']
            a['type'] = dictionary['namesilo']['reply']['resource_record'][i]['type']

            #check if record exists and update db if changed.
            if a['record'] in sql_dns_list_rrid:
                i = sql_dns_list_rrid.index(a['record'])
                if a['host'] != sql_dns_list[i]['host']:
                    msg.good(f"{settings.timeprefix()}{a['record']} host changed to {a['host']}")
                    sql.u_dns_list(a['record'],dns_host = a['host'])

                if a['ip'] != sql_dns_list[i]['ip']:
                    msg.good(f"{settings.timeprefix()}{a['record']} - {a['host']} dns ip changed to {a['ip']}")
                    sql.u_dns_list(a['record'],ip = a['ip'])

                if a['type'] != sql_dns_list[i]['type']:
                    msg.good(f"{settings.timeprefix()}{a['record']} - {a['host']} dns type changed to {a['type']}")
                    sql.u_dns_list(a['record'],dns_type = a['type'])
                
            else:
                sql.i_dns_list(a['host'],a['record'],a['ip'],a['type'],domain_name,app_id)
            
        for i in range(len(sql_dns_list_rrid)):
            if sql_dns_list_rrid[i] not in ns_dns_list_rrid:
                sql.d_dns_list(sql_dns_list_rrid[i])
                msg.info(f"{settings.timeprefix()}{sql_dns_list_rrid[i]} not in dns server")

def host_namesilo(host):
    host = host[0:-(len(host)-host.find(".prosrv.top"))]
    return(host)

def u_dns_namesilo(new_ip,old_ip,api_key,device_id,app_id):
    rrid_list = sql.q_dns_list(old_ip)
    msg.divider(f'{settings.timeprefix()[:-2]}:')
    for i in range(len(rrid_list)):      
    
        rrid = rrid_list[i]['rrid']
        domain = rrid_list[i]['domain']
        host = rrid_list[i]['host']
        host = host_namesilo(host)

        update_url = 'https://www.namesilo.com/apibatch/dnsUpdateRecord?version=1&type=xml&key='+api_key+'&domain='+domain+'&rrid='+rrid+'&rrhost='+host+'&rrvalue='+new_ip+'&rrttl=3600'
        r = requests.get(update_url)
        r_s = r.status_code

        while r_s != 200:
            string = f"{settings.timeprefix()}Unable to connect to namesilo, retrying in 60 seconds"
            sql.mysql_log(device_id, app_id,"HIGH","ERROR",string)
            time.sleep(60)
            update_url = 'https://www.namesilo.com/apibatch/dnsUpdateRecord?version=1&type=xml&key='+api_key+'&domain='+domain+'&rrid='+rrid+'&rrhost='+host+'&rrvalue='+new_ip+'&rrttl=3600'
            r = requests.get(update_url)
            r_s = r.status_code
        
        xml = xmltodict.parse(r.text)
        try:
            rrid = xml['namesilo']['reply']['record_id']
        except KeyError: 
            rrid = None

        status = xml['namesilo']['reply']['code']
        detail = xml['namesilo']['reply']['detail']
        msg.good(f"{status} -- {detail} -- {host}")

        if status != '300':
            string = "Status: "+str(status)+" Detail: "+str(detail)
            sql.mysql_log(device_id, app_id,"HIGH","ERROR",string)
