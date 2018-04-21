import json
import requests

def get_servers(url):
    result = requests.get(url)
    return json.loads(result.text)['data']
    
    
#deg fetch_servers():

def process_severs():
    url = "http://172.17.0.241:8080/api/v1.0/backend/user_list_servers/"
	
    data = get_servers(url)
	renders = []
	for da in data:
        if da['name'][:6] == 'Render':
	        renders.append(da)
	

if __name__ == "__main__":
   