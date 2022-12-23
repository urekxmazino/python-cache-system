from bs4 import BeautifulSoup
import requests
from cache import ResponseCache


"""live test """
link  = "https://httpbin.org/"
cacher =  ResponseCache(link)
cached_page  =  cacher.get_cache(link)
if cached_page:
    print("from cache")
    data =  cached_page
else :
    
    data = requests.get(link).content
    cacher.create_cache(link,data)
if data:
    soup = BeautifulSoup(data,"html.parser")
    print(soup.title.text.strip())