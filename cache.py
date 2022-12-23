from pathlib import Path
from datetime import datetime
from hashlib import  md5
import os

class ResponseCache:
    # time in minutes
    EXPIRE = 20
    BASE_DIR  =  Path(__file__).resolve().parent
    CACHE_DIR =  Path(BASE_DIR,"cache")
    
    def __init__(self,url:str) -> None:
        self.url   = url

    def save_html(self,hash_,data):
        file =  Path(ResponseCache.CACHE_DIR,hash_)
        with open(file,"w",encoding="utf-8") as f:
            f.write(str(data))
    
    def load_html(self,file_path:str) -> str:
        with open(file_path,"r",encoding="utf-8") as fp:
            return fp.read().encode("utf-8")
        
    def link_2_hash(self,link:str ):
        hash =  md5(link.encode("utf-8")).hexdigest()
        return hash
    
    def get_file_date(self,file_path):
        try:
            modified =  os.path.getmtime(file_path)
            modified_date  =  datetime.fromtimestamp(modified)
            return modified_date
        except: return False
    
    def file_path(self,hash):
        return Path(ResponseCache.CACHE_DIR,hash).resolve()
    
    def compare(self,modified_date) ->  int:
        now  = datetime.now()
        date_dif =  int((now-modified_date).seconds/60)
        return True if date_dif <= ResponseCache.EXPIRE else False
    
    def create_cache(self,url,raw): 
        hash_  =  self.link_2_hash(url)
        self.save_html(hash_,raw)
        
    def get_cache(self,link:str):
        link_hash  =  self.link_2_hash(link)
        file_path  = self.file_path(link_hash)
        if os.path.exists(file_path):
            modified_date  =  self.get_file_date(file_path)
            diffrent =  self.compare(modified_date)
            return self.load_html(file_path) if diffrent else False
        