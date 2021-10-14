import mysql.connector
import os
import json
from wasabi import Printer

msg = Printer()
cwd = os.getcwd()
jsonconf = cwd + '/config.json'

with open(jsonconf, 'r') as datajson:
    data = json.load(datajson)

host = data['SQL']['sql_host']
user = data['SQL']['sql_user']
passwd = data['SQL']['sql_passwd']
db = data['SQL']['sql_db']    

def mysql_log(device_id, app_name, LOG_LEVEL, LOG_TYPE, string):
    
    main = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=db
    )

    c = main.cursor()
    connected = main.is_connected()
    if connected:
        #SQL INSERT LOG
        sql = ("INSERT INTO main.Logs (DEVICE_ID,APP_NAME,LOG_LEVEL,LOG_TYPE,STRING) VALUES (%s,%s,%s,%s,%s)")
        val = (device_id,app_name,LOG_LEVEL,LOG_TYPE,string)
        c.execute(sql,val)
        main.commit()

        main.close()


def q_appconfig(APP_ID):
            
    main = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=db
    )
    c = main.cursor(dictionary=True)
    connected = main.is_connected()
    if connected:
        sql = ("SELECT PARAM_ID, VALUE FROM main.APP_PARAM ap WHERE APP_ID = %s")
        value = (APP_ID,)
        c.execute(sql,value)
        x = {}
        for row in c:
            PARAM_ID = row['PARAM_ID']
            VALUE = row['VALUE']
            x[PARAM_ID] = VALUE
        main.close()
    return(x)

def u_appconfig(PARAM_ID,APP_ID,DATA,USER):     
    main = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=db
    )
    c = main.cursor()
    connected = main.is_connected()
    if connected:
        sql = ('UPDATE main.APP_PARAM SET VALUE=UPPER(%s),MOD_USER=%s WHERE PARAM_ID=%s AND APP_ID=%s')
        value = (DATA, USER, PARAM_ID, APP_ID)
        c.execute(sql,value)
        main.commit()
        main.close()

def q_globalconfig(PARAM_ID):
        
    main = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=db
    )
    c = main.cursor(dictionary=True)
    connected = main.is_connected()
    if connected:
        sql = ('SELECT PARAM_ID, VALUE FROM main.GLOBAL_PARAM ap WHERE PARAM_ID=%s')
        value = (PARAM_ID, )
        c.execute(sql,value)
        r = c.fetchone()
        value = r['VALUE']
        main.close()

        return(value)

def q_in_globalconfig(sql_in):
        
    main = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=db
    )
    c = main.cursor(dictionary=True)
    connected = main.is_connected()
    if connected:
        sql_in_sql = ', '.join(['%s'] * len(sql_in))
        sql = "SELECT PARAM_ID, VALUE FROM main.GLOBAL_PARAM ap WHERE PARAM_ID IN ({0})".format(sql_in_sql)
        value = sql_in
        c.execute(sql,value)
        x = {}
        for row in c:
            PARAM_ID = row['PARAM_ID']
            VALUE = row['VALUE']
            x[PARAM_ID] = VALUE
        main.close()
        return(x)

def u_globalconfig(PARAM_ID,DATA,USER):     
    main = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=db
    )
    c = main.cursor()
    connected = main.is_connected()
    if connected:
        sql = ('UPDATE main.GLOBAL_PARAM SET VALUE=UPPER(%s),MOD_USER=%s WHERE PARAM_ID=%s')
        value = (DATA, USER, PARAM_ID)
        c.execute(sql,value)
        main.commit()
        main.close()

def q_dns_list(*where):
            
    main = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=db
    )
    c = main.cursor(dictionary=True)
    connected = main.is_connected()
    if connected:
        if where: sql = ("SELECT HOST,RRID,IP,`TYPE`,`DOMAIN` FROM main.namesilo WHERE IP = %s")
        else: sql = ("SELECT HOST,RRID,IP,`TYPE`,`DOMAIN` FROM main.namesilo")
        if where:
            value = where 
            c.execute(sql, value)
        else: c.execute(sql, )
        a = []
        b = {}
        for row in c:
            b['host'] = row['HOST']
            b['rrid'] = row['RRID']
            b['ip'] = row['IP']
            b['type'] = row['TYPE']
            b['domain'] = row['DOMAIN']
            a.append(b.copy())
        main.close()
    return(a)

def u_dns_list(RRID,**kwargs):
    main = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=db
    )
    c = main.cursor()
    connected = main.is_connected()

    try: ip = kwargs['ip']
    except: ip = False
    try: dns_host = kwargs['dns_host']
    except: dns_host = False
    try: dns_type = kwargs['dns_type']
    except: dns_type = False

    if connected:
        if ip:
            sql = "UPDATE main.namesilo	SET IP = %s WHERE RRID=%s"
            val = (ip,RRID)
        if dns_host:
            sql = "UPDATE main.namesilo	SET HOST = %s WHERE RRID=%s"
            val = (dns_host,RRID)
        if dns_type:
            sql = "UPDATE main.namesilo	SET TYPE = %s WHERE RRID=%s"
            val = (dns_type,RRID)            
    c.execute(sql,val)
    main.commit()
    main.close()


def i_dns_list(HOST,RRID,IP,TYPE,DOMAIN,USER):     
    main = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=db
    )
    c = main.cursor()
    connected = main.is_connected()
    if connected:
        sql = ('INSERT INTO main.namesilo (Host,RRID,IP,`TYPE`,`Domain`,`User`)	VALUES (%s,%s,%s,%s,%s,%s)')
        value = (HOST, RRID, IP, TYPE, DOMAIN, USER)
        c.execute(sql,value)
        main.commit()
        main.close()

def d_dns_list(RRID):     
    main = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=db
    )
    c = main.cursor()
    connected = main.is_connected()
    if connected:
        sql = ('DELETE FROM main.namesilo WHERE RRID= %s')
        value = (RRID, )
        c.execute(sql,value)
        main.commit()
        main.close()

def q_ip():
    main = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=db
    )
    c = main.cursor(dictionary=True)
    connected = main.is_connected()
    if connected:
        sql = ("select IP from main.IP_Addr ia where type = 'LAST_KNOWN_IP'")
        c.execute(sql, )
        r = c.fetchone()
        value = r['IP']
        main.close()
    return(value)

def u_ip(curr_ip,dbuser):
    main = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=db
    )
    c = main.cursor()
    sql = "UPDATE main.IP_Addr SET IP = %s, USER = %s WHERE TYPE = 'LAST_KNOWN_IP'"
    val = (curr_ip,dbuser)
    c.execute(sql,val)
    main.commit()
    #msg.good(c.rowcount + " IP updated")
    main.close()
