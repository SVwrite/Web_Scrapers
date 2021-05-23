import requests
from bs4 import BeautifulSoup
# import re
import os
import time

class Book:
    def __init__(self, title= None, author = None, publisher = None, year =None, url = None, formats = None):
        self.title = title
        self.author = author
        self.publisher = publisher
        self.year = year
        self.url = url
        self.formats = formats


    def PrintDetails(self) -> None:
        print(f"\n\tTitle : {self.title}\n\tAuthor : {self.author}\n\tYear : {self.year}")
        print(f"\tPublisher : {self.publisher}\n\tAvailable format: {self.formats}")


    def geturl(self) -> str:
        return self.url



def ProductName()-> str:
    product = input("\n\tWhat's the title of the book ? : ")
    z_lib_books = 'https://1lib.in/s/'
    url = z_lib_books + product
    return url


def HtmlFetch(url :str) -> BeautifulSoup:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    return soup 


def ZlibBookDetailsExtracter(soup : BeautifulSoup) -> Book:
    book ={}
    
    all_searches = soup.find('div', id='searchResultBox')
    
    all_searches = all_searches.find_all('table', class_='resItemTable')

    # print(all_searches)
    # searches = all_searches[0]
    
    for i in range(4):
        search = all_searches[i]
        title = search.h3.a.text
        url = 'https://1lib.in/' + search.h3.a['href']

        
        author = search.find('div', class_='authors')
        if author:
            author = author.text
        
        publisher = search.find('div', title = "Publisher")
        if publisher:
            publisher = publisher.text

        year = search.tr.find('div', class_='bookProperty property_year')
        if year:
            year = year.find('div', class_='property_value')
            if year:
                year = year.text
        
        format = search.find('div', class_='bookProperty property__file')
        format = format.find('div', class_='property_value').text
        
        b = Book(title, author, publisher, year, url, format)
        yield b


def ZlibDownloadExtractor(url :str) :
    #Returns avail book formats and download urls
    soup = HtmlFetch(url)
    formats = soup.find('div', class_='btn-group')
    formats = formats.find('button', id='btnCheckOtherFormats')
    print(formats.prettify())


def download(url):
    r = requests.get(url, allow_redirects=False)
    print(r.headers.get('content-type'))
    open('Book_name.pdf', 'wb').write(r.content)
    # print(r.text)



def main():
    soup = HtmlFetch(ProductName())
    
    books = list(ZlibBookDetailsExtracter(soup))
    books[0].PrintDetails()
    # for book in books:
    #     book.PrintDetails()
    
    # url = books[0].geturl()
    # ZlibDownloadExtractor(url)
    # download('https://1lib.in/dl/3485511/701625')

if __name__=="__main__":
    main()