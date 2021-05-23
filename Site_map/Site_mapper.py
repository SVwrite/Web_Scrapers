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
            print(f"Pinging : {url}")
            try:
                r = requests.get(url)
                self.visited.append(url)
                return BeautifulSoup(r.text, 'lxml')   
            except requests.exceptions.RequestException:
                return None
        return None
    
    
    def extractor(self, soup):
        pages =[]
       
        links = soup.find_all('a')
        # print(links[0])
        for link in links:
            # print(link)
            try:
                # print(re.match(self.website.pattern, link['href']))
                if self.website.isabsolute == False:
                    url = (self.website.base_url+link['href']).strip("./")
                else:
                    url = link['href'].strip("./")
                
                if url not in pages and re.match(self.website.pattern, link['href']):  #If link not recorded and internal
                    #Checking if the link is not broken. 
                    match = re.findall(r"http", url)
                    if not len(match) > 1:
                        pages.append(url)
                    
            except KeyError:
                pass
        try:        
            title = soup.find(self.website.title_tag).text
        except AttributeError:
            title = "No Title Found, for this page"

        return pages, title

    #It'll get url from it's callers. First call on you.
    def crawl(self,url): 
        # #It'll stop execution after first 20 pages.
        # if len(self.site_map) >=20:
        #     return           
        soup = self.get_page(url)
        if soup != None:
            connections, title = self.extractor(soup)
            self.site_map.append(Page(title, url, connections))
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
    def __init__(self, url, url_pattern, titletag, base_url =None, isabsolute = True) -> None:
        self.url = url
        self.pattern = url_pattern  
        self.title_tag = titletag
        self.isabsolute = isabsolute

        #Find the base_url, to be used in cases where the links are relative
        matches = re.match(r"((https|http)?(\:\/\/)?[a-zA-Z0-9\.\-]*(com|net|or|io|ai|(\.co\.in)))", url)
        # print(matches.group(1), url)
        self.base_url = matches.group(1)



def main():

    # btv = Website('https://www.increaseimmunity.org/', '.*increase.*', 'title')
    askgif = Website('https://www.askgif.com', '.*\/shopping\/*', 'title', isabsolute= False)
    #The line above is for demonstration purposes only. Please do not use the crawler on any websites without taking 
    #due permissions from the owners.
    
    # crawler = Crawler(btv)
    crawler = Crawler(askgif)
    crawler.show_data()


if __name__ == "__main__":
    main()

