from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from hashlib import  md5
import  requests,sqlite3


class ResponseCache:
    
    
    EXPIRE = 1
    BASE_DIR  =  Path(__file__).resolve().parent
    CACHE_FOLDER =  Path(BASE_DIR,"cache")
    DB_FOLDER  = Path(BASE_DIR,"cache.db")
    
    def __init__(self,url:str) -> None:
        self.url   = url
        
        
    def connector(self,commit:bool =False):
        sql =  sqlite3.connect(ResponseCache.DB_FOLDER)
        cursor  =  sql.cursor()
        return cursor if not commit else (sql,cursor)
        
    def create_db(self,):
        query =  """CREATE TABLE IF NOT EXISTS  cache (
            link TEXT UNIQUE,
            HASH TEXT UNIQUE,
            date  timestamp);"""
        sql,cursor  = self.connector(commit=True)
        cursor.execute(query)
        sql.commit()
        
    
    def insert(self,query : str,*args : tuple):
        sql,cursor  =  self.connector(commit=True)
        cursor.execute(query,args)
        sql.commit()
        
        
    def select(self,query,*args):
        cursor =  self.connector(commit=False)
        cursor.execute(query,args)
        result = cursor.fetchall()
        return  result[0]  if  None or len(result) !=0 else None
    

    def update(self,query,*args):
        sql,cursor  =  self.connector(commit=True)
        cursor.execute(query,args)
        sql.commit()

    def save_html(self,hash_,data):
        file =  Path(ResponseCache.CACHE_FOLDER,hash_)
        with open(file,"w") as f:
            f.write(str(data))
    
    def load_html(self,hash_:str) -> str:
        file  =  Path(ResponseCache.CACHE_FOLDER,hash_)
        with open(file,"r") as fp:
            return fp.read() 
        
        
    def link_2_hash(self,link:str ):
        hash =  md5(link.encode("utf-8")).hexdigest()
        return hash

    
    def get_cache(self,url:str):
        query =  "SELECT * FROM  cache WHERE link = ?; "
        exist  = self.select(query,url)
        if exist:
            now =  datetime.now()
            link   =  exist[0]
            hash_  =  exist[1]
            db_date  = datetime.strptime(exist[2],"%Y-%m-%d %H:%M:%S.%f") 
            date_dif =  int((now-db_date).seconds/60)
            if   date_dif <= ResponseCache.EXPIRE:
                print("from cache .......")
                raw  = self.load_html(hash_)
                return  raw
            else : return False
        else: return None
            
    def new_cache(self,url,raw): 
        now =  datetime.now() 
        hash_  =  self.link_2_hash(url)
        query =  f"INSERT OR REPLACE INTO cache (link,hash,date) VALUES (?,?,?);"     
        self.insert(query,url,hash_,now)
        self.save_html(hash_,raw)
        return raw


def get_html(url:str,refer:str = None):
    header = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}
    response  = requests.get(url,headers=header)
    return  response.content if  response.status_code  ==  200 else None
        
          
    
def get(url:str,refer:str = None):
    cacher  = ResponseCache(url)
    cached_raw  =  cacher.get_cache(url)
    if cached_raw:
        return  cached_raw
    
    else:
        raw =  get_html(url)
        if raw: 
            cacher.new_cache(url,raw)
            print("from website")
            return raw
if __name__ == "__main__":
    """remove # from those two lines for once to create database then comment them out forever   """
    # create_db =  ResponseCache("link")
    # create_db.create_db()
    
    url  = "https://httpbin.org/"
    data = get(url)
    if data:
        soup = BeautifulSoup(data,"html.parser")
        print(soup.title.text.strip())