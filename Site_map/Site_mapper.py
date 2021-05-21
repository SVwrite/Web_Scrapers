import re
from typing import Pattern
import requests
from bs4 import BeautifulSoup

# What we need from each page?
# title, url (identifier) and connections (ie, to what pages is it alredy connected)
# links has to be a list.
# We can also use title as identifier, but links are certain to be unique, titles might not be. For now, lets use links
# So the connections will be a list, of all the urls, found on the page. 


#-----------------------------------------------------------------------------------------------------
class Page:
    #This class is to have three paramenters - titles, url (identifier) and connections(all links on that page)
    # A function to display page data. 
    
    def __init__(self, title, url, connections):
        print(f"\n\tAdding : {title}")
        self.title = title
        self.url = url
        self.connections = connections
        
    
    # This display function should take in the url, identify the page, and display it's data.
    def page_display_data(self):
        print(f"\n\tPage Title: {self.title}")
        print(f"\tPage Address: {self.url}")
        # print("\n\tConnections: ")
        # for connection in self.connections:
        #     print(f"\t{connection}")


class Crawler:

    def __init__(self, website) -> None:
        self.website = website
        self.visited = []
        self.site_map =[] # List of class<Page> objects
        self.crawl(website.url)
  

    def get_page(self, url):
        if url not in self.visited:
            try:
                r = requests.get(url)
                self.visited.append(url)
                return BeautifulSoup(r.text, 'lxml')   
            except requests.exceptions.RequestException:
                return None
        return None
    
    
    def extractor(self, soup):
        pages =[]
        # print(soup.prettify())
        links = soup.find_all('a')
        for link in links:
            # print(re.match(self.pattern, link['href']))
            if link['href'] not in pages and re.match(self.website.pattern, link['href']):
                pages.append(link['href'])
                # print(link['href'])

        title = soup.find(self.website.title_tag).text
        # print(title)

        return pages, title


    def crawl(self,url):            #It'll get url from it's callers. First call on you.
        soup = self.get_page(url)
        if soup != None:
            connections, title = self.extractor(soup)
            self.site_map.append(Page(title, url, connections))
            
            #Instead of going full length, we're trying to stop at 20 pages. But break applied at 20 pages,
            #acts at 62 pages.
            # if len(self.site_map) >= 20:
            #     print(f"Length of Site_map : {len(self.site_map)}")
                # return  
            for connection in connections:
                self.crawl(connection)

    
    def show_data(self):
        print(f"\n\tTotal Number of pages : {len(self.site_map)}")
        for page in self.site_map:
            page.page_display_data()






class Website:
    #This class will standardize the data that is needed to crawl a website.
    # Primarily to crawl through a website, we'll need to differentiate between internal and external links
    # This will contain the home_url, and site pattern.
    def __init__(self, url, url_pattern, titletag) -> None:
        self.url = url
        self.pattern = url_pattern  
        self.title_tag = titletag



def main():
    # btv = Website('https://www.increaseimmunity.org/', '.*increase.*', 'title')
    #The line above is for demonstration purposes only. Please do not use the crawler on any websites without taking 
    #due permissions from the owners.
    
    crawler = Crawler(btv)
    crawler.show_data()


if __name__ == "__main__":
    main()

