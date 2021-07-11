import requests
import concurrent.futures
from bs4 import BeautifulSoup

url = "https://www.artmajeur.com/en/"
url = 'https://www.saatchiart.com'

urls =[]
for i in range(100):
    urls.append(url)

def runner(url):
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'lxml')
        try:
            title = soup.find('h1').text
            print(title)
        except AttributeError:
            print("FAILED")


with concurrent.futures.ThreadPoolExecutor() as executor:
    runners = executor.map(runner, urls)

for r in runners:
    pass