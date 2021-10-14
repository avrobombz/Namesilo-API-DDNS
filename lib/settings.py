import time

def timeprefix(): #create timestamp for use in output
    prefix = time.strftime('%Y_%m_%d-%H:%M:%S - ') 
    return(prefix)
