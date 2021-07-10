import requests
from bs4 import BeautifulSoup


def artist_artsper():
    url ='https://www.artsper.com/us/contemporary-artists/spain/7900/miguel-guia'
    # url = 'https://www.artsper.com/us/contemporary-artists/france/18910/kiko'

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')

    A = soup.find('div', id ='biography')
    #Artist's name
    name = A.h1.text
    print(name)

    #Born
    B = A.find('div', class_='sub-title col-sm-9 col-xs-12')
    bo = B.find('span', class_='birthday-date').text
    born = ""
    for b in bo:
        if b.isdigit():
            born+=b
    print(born)

    #Country
    country = B.span.text
    print(country)

    #About
    about = A.find('div', class_='col-sm-9 col-xs-12 biography').text.strip()
    ab = about.split("  ")
    about = ''
    for a in range(len(ab)-1):
        b = ab[a]
        about = about + "\n" + b.strip()
    about = about.strip()
    print(about)



def seller_artsper():
