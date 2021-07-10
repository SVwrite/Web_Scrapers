import requests
from bs4 import BeautifulSoup
import concurrent.futures

url = 'https://www.emergingartistplatform.com/browse?Collection=Sculptures&page='
url ='https://www.emergingartistplatform.com/product-page/abstract-01-raphael-d'

r = requests.get(url)
soup = BeautifulSoup(r.text, 'lxml')
image = soup.find('div', class_='main-media-image-wrapper-hook')
image = image.find('div', id='get-image-item-id')
print(image.get('href'))
# for im in image:
#     if im.get('data-hook') == 'product-image':
#         image_loc = im.get('src')
#         break
# print(image_loc)
