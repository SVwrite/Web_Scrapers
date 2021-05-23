#This scrapper will scrape a website that is not behind a login screen(initially)
# Then on that site, it'll go to all the webpages, and record their title and url



import requests
from bs4 import BeautifulSoup
import re 
import csv



# req = 'https://svwrite.blogspot.com/'
visited =[]
pattern = r"<a href=[\"\']([a-zA-Z0-9\.\/\:\-]*)[\"\']>"

def input_module():
    req = input("Enter the blogspot url: ")
    return req



def get_requests(req : str) -> requests:
    global visited
    if req not in visited:
        r = requests.get(req)
        visited.append(req)
        return r
    return None


def name_processor(title):
    title = '_'.join(title.split())
    file_name = title+ '.csv'
    # print(file_name)
    return str(file_name)


def extractor(articles, file_name):
    
    with open(file_name, 'w', encoding='UTF-16', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Page_Name','Link'])

    for article in articles:
        a_tag =article.h3.a
        url = re.match(pattern,str(a_tag))
        # print(url.group(1))
        url= url.group(1)
        
        header = a_tag.text
        print(f"\tHeading : {header}\n\turl : {url}")
        data = [header,url]

        print(file_name)
        
        with open(file_name, 'a', encoding='UTF-16', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)


def caller(req):
    r= get_requests(req)
    soup = BeautifulSoup(r.text, 'lxml')
    # print(soup.prettify())

    title = soup.title.text
    # print(title)

    if r.status_code == 200 :
        print(f"\n\tThe blogsite named \"{title}\" is found.")
        print("\tIt has following blogs::\n\t-------------------------")

    articles = soup.findAll('article')
    return articles, title



#Bruteforcing all urls on a page.
# urls = re.findall(pattern, r.text)
# print(urls)


def reader(file_name):
    with open(file_name, 'r', encoding='UTF-16') as file:
        reader = csv.reader(file)
        for row in reader:
            print(row)



def main():
    req = input_module()
    
    articles, title = caller(req)
    file_name = name_processor(title)
    extractor(articles, file_name)

   

if __name__=="__main__":
    main()