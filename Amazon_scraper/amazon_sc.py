import requests
from bs4 import BeautifulSoup
import re




def HtmlRequests(url :str) -> BeautifulSoup:
    print(f"\n\n\tPinging : {url}")
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    return soup


def AsoupParser(soup: BeautifulSoup) -> None:
    ps = soup
    print(ps.prettify())


def GsoupParser(soup : BeautifulSoup) -> str:
    ps = soup.find_all('h3')        #Picking all the products here
    p =ps[0]                
    url_pat = r'(http(s)?:\/\/[a-zA-Z0-9\.\-\/]*)'    # &, =, _ were added later
    url = re.search(url_pat, p.parent['href'])


    print(f"{p.parent['href']}\n\n")
    print(f"{url.group(1)}\n\n")
    
    return url.group(1)


def main():

    google_search = 'https://www.google.com/search?q=jbl+headphonesC100Si+amazon'
    amazon_search = 'https://amazon.in/s?k=jbl+headphones'
    # url = amazon_search
    url = google_search


    soup = HtmlRequests(url)
    
    # AsoupParser(soup)
    url = GsoupParser(soup)
    soup = HtmlRequests(url)
    # AsoupParser(soup)


if __name__=="__main__":
    main()