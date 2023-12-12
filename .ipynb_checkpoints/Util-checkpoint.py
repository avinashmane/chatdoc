# class Util:
import logging
import json

def setLogger(logFile=None,level=logging.INFO):
    # level = logging.INFO if level is None else 
    from imp import reload

    # jupyter notebook already uses logging, thus we reload the module to make it work in notebooks
    # http://stackoverflow.com/questions/18786912/get-output-from-the-logging-module-in-ipython-notebook
    reload(logging)
    logging.basicConfig( level=level,
                    format='%(asctime)s:%(levelname)s:%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
                    
    if logFile:
        logger = logging.getLogger()
        fhandler = logging.FileHandler(filename=logFile, mode='a')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                                     ,datefmt='%Y-%m-%d %H:%M:%S')
        fhandler.setFormatter(formatter)
        logger.addHandler(fhandler)
        logger.setLevel(level)
        
    logging.info("Logger file: "+logFile if logFile else "None")

def readTbl(t):
    from dataLayer import readData
    return readData(t)

def copyFile(src,destPath):
    if ".zip" in src:
        import zipfile,os
        with zipfile.ZipFile(src) as zf:
            for dashName in zf.namelist():
                try:
                    zf.extract(dashName, path=destPath)
                except(e):
                    print(e)
                else:
                    print("Copied {} to {}".format(src,destPath))
    else:
        import shutil
        try:
            shutil.copy(src,destPath)
        except(err):
            print(err)
        else:
            print("Copied {} to {}".format(src,destPath))

def stripL30cloud(inputSeries):
    return inputSeries.str.replace(
        "\(([Cc]lou|[Rr]ed\ ?)\w*\)","",regex=True).str.rstrip(" "
        )
def getDateFromYQW(y,q,w,weekdayOffset=5):
    startDate = datetime(year=int(y), month=1+3*(int(q)-1), day=1)
    weekday=startDate.weekday()
    return (startDate + timedelta(days=  - weekday + weekdayOffset + (int(w)-0)* 7))


# def toStr(obj,precision=1):
#   pass

### Save Load
import pickle
import gzip


def save(object, filename, bin = 1):
	"""Saves a compressed object to disk
	"""
	file = gzip.GzipFile(filename, 'wb')
	file.write(pickle.dumps(object, bin))
	file.close()


def load(filename):
	"""Loads a compressed object from disk
	"""
	file = gzip.GzipFile(filename, 'rb')
	buffer = ""
	while 1:
		data = file.read()
		if data == "":
			break
		buffer += data
	object = pickle.loads(buffer)
	file.close()
	return object
  

def json_load(filename):
    with open(filename,"r") as f:
        return json.load(f)
    
def json_dump(obj,filename):
    with open(filename,"w") as f:
        return json.dump(obj,f,indent=2)
    
import pickle

def obj_load(filename):
    try:
        with open(filename,"rb") as file:
            return pickle.load(file)
    except:
        print(f"error in obj_load({filename})")    

def obj_dump(obj,filename):
    try:
        with open(filename,"wb") as file:
            return pickle.dump(obj,file)
    except:
        print(f"{obj} error in obj_dump()")       
        
import yaml, os
def yaml_load(filename):
    try:
        with open(filename,"r") as f:
            return yaml.load(os.path.expandvars("\n".join(f.readlines())),yaml.BaseLoader)
    except:
        input=filename
        return yaml.loads(input)
        
def yaml_dump(obj,filename):
    try:
        with open(filename,"w") as file:
            return yaml.dump(obj,file)
    except Exception as e:
        print(f"{e!r} error in yaml_dump()")       

def yaml_append(obj,filename):
    try:
        with open(filename,"a") as file:
            return yaml.dump(obj,file)
    except Exception as e:
        print(f"{e!r} error in yaml_dump()")       
        
        
        
from ploomber.io import serializer, unserializer

@serializer(fallback='joblib', defaults=['.csv', '.txt'])
def my_serializer(obj, product):
    pass


@unserializer(fallback='joblib', defaults=['.csv', '.txt'])
def my_unserializer(product):
    pass
