from json import JSONDecodeError

from packets.global_vars import visited, image_pool
from packets import dbmanip as db
from selenium import webdriver

from stem.control import Controller
from stem import Signal
import requests
import os
from bs4 import BeautifulSoup
import concurrent.futures


class TheMiner:

    def __init__(self):
        pass

    @staticmethod
    def ghost_sessions():

        def renew_conncetion():
            with Controller.from_port(port=9051) as controller:
                controller.authenticate(password="shreyansh")
                controller.signal(Signal.NEWNYM)

        def get_tor_session():
            renew_conncetion()

            session = requests.session()
            session.proxies = {'http': 'socks5://127.0.0.1:9050',
                               'https': 'socks5://127.0.0.1:9050'}
            return session
            # Tor uses the 9050 port as the default socks port

        session = get_tor_session()
        r = session.get('http://httpbin.org/ip').json()
        lastip = r.get("origin")
        print(lastip)
        lastip = lastip.strip(".")

        while True:
            # renew_conncetion()
            try:
                session = get_tor_session()
                r = session.get('http://httpbin.org/ip').json()
                newip = r.get("origin")
                # print(newip)
                newip = newip.strip(".")
                if newip[2] != lastip[2]:
                    break
                lastip = newip
            except JSONDecodeError:
                pass

        return session


    @staticmethod
    def conversion_rate(c1):
        query = f'https://www.xe.com/currencyconverter/convert/?Amount=1&From={str(c1)}&To=USD'
        r = requests.get(query)
        # print(r.status_code)
        soup = BeautifulSoup(r.text, 'lxml')
        try:
            rate = soup.find('p', class_='result__BigRate-sc-1bsijpp-1 iGrAod')
            print(f"1 {c1} : {rate.text}")
            tr = ""
            for r in rate.text:
                if str(r).isnumeric() or str(r) == ".":
                    tr += r
            rate = float(tr)
            return rate
        except:
            print(f"Failed to fetch conversion rate for {c1}")

    @staticmethod
    def fetch_page_headless(urls):
        if urls not in visited:
            visited.add(urls)
            try:
                driver = webdriver.Firefox()
                driver.get(urls)
                soup = BeautifulSoup(driver.page_source, 'lxml')
                driver.quit()
                print(f"FETCHING: {urls}")
                return soup
            except requests.exceptions.RequestException:
                print(f"FAILED TO FETCH: {urls}")
                return None

    @staticmethod
    def fetch_page(urls, ghost=False):
        if urls not in visited:
            visited.add(urls)
            try:
                if ghost is False:
                    s = requests.Session()
                    head = ({
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                        'Accept-Language': 'en-US, en;q=0.5'})
                    s.headers.update(head)
                else:
                    print("Using ghosts. This might take some time...")
                    s = TheMiner.ghost_sessions()
                    head = ({
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                        'Accept-Language': 'en-US, en;q=0.5'})
                    s.headers.update(head)
                r = s.get(urls)

                soup = BeautifulSoup(r.text, 'lxml')
                print(f"FETCHING: {urls}")
                return soup
            except requests.exceptions.RequestException:
                print(f"FAILED TO FETCH: {urls}")
                return None

    @staticmethod
    def download_engine(tup):
        # Return True if image is downloaded and False if not
        path = tup[0]
        url = tup[1]
        if not os.path.exists(path):
            try:
                s = requests.Session()
                head = ({
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                    'Accept-Language': 'en-US, en;q=0.5'})
                s.headers.update(head)
                r = s.get(url, allow_redirects=True, stream=True)

                # r = requests.get(url, allow_redirects=True, stream=True)
                print(r.headers.get('content-type'))
                f = open(path, 'wb')
                for chunk in r.iter_content(chunk_size=255):
                    if chunk:
                        f.write(chunk)
                f.close()
                return True
            except TimeoutError:
                return False
        else:
            return True

    @staticmethod
    def download_images():
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = [executor.submit(TheMiner.download_engine, tup) for tup in image_pool]
            # results = [executor.submit(TheMiner.download_engine, tup) for tup in image_pool]

        for future in concurrent.futures.as_completed(results):
            result = future.result()

    @staticmethod
    def sir_image_manager(chunk_size=1000):
        images = db.Images()
        image_data = images.read_image_data()
        # Read image_data gives a list of tuples (page_url , image_url, path)

        while len(image_data) > 0:
            sir = []
            for i in range(chunk_size):
                if len(image_data) > 0:
                    sir.append(image_data.pop())
                    continue
                break

            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = executor.map(TheMiner.sir_engine, sir)

            for result in results:
                print("Downloading images, adding them to db")
                sir.clear()

    @staticmethod
    def sir_engine(tup):
        page_url = tup[0]
        image_url = tup[1]
        path = tup[2]
        # im = imageData()

        bundle = []

        # Fetching file name (path ) for the image using it's url
        bundle.append(path)
        bundle.append(page_url)
        # print(bundle)
        # Download the image. Calling download_engine with a tuple (path, url)
        downloaded = TheMiner.download_engine((bundle[0], image_url))

        # If image has been downloaded, it's location will be updated. If not, it won't be.
        if downloaded:
            # Update image location
            artwork_update_agent = db.Price()
            artwork_update_agent.update_image(*bundle)


# We fill fetch the conversion rate once.
gbp = TheMiner.conversion_rate("GBP")
eur = TheMiner.conversion_rate("EUR")
