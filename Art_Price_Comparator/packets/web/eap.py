# EMERGING ARTIST PLATFORM
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import requests
from bs4 import BeautifulSoup
import concurrent.futures
# import re
import time

# Importing data structures
from packets.websiteds import Website
from packets.dataStructures import TheAuthour

from packets.TheMiner import TheMiner, gbp as rate
from packets import dbmanip as db
from packets.global_vars import SELLER_INFO, ARTIST_INFO, visited, KEY_INFO





class EAP:
    # NOTES ABOUT THE SITE
    # emergingartistsplatform is different from KAZoART and artsper because it doesn't follow the pattern of,
    # artist_listings -> artwork listings (artist_data) [since artist's bio page contains the artwork listings] ->
    # major mining ops.
    # Insted, here we'll have to fetch artwork_listings -> artwork_data -> (seller_data, artist_data)

    def __init__(self, website):
        self.website = website
        self.artist_listings = []
        self.artwork_listings = []
        self.active_pages = [1]

    @staticmethod
    def key_maker(artist_url):
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        visited.discard(artist_url)
        soup = BeautifulSoup(driver.page_source, artist_url)
        if soup is not None:

            n_c = soup.find_all('h2', class_='font_2')
            # Artist's name
            try:
                name = n_c[0].text.strip()
            except IndexError:
                print(n_c)
                name = None
            # print(name)
            # If an error occurs here, its because the page layout has changed and thus the code needs to be fixed

            if name is not None:
                # Country
                try:
                    country = n_c[1].text.strip()
                except AttributeError:
                    country = None

                # About
                try:
                    text = soup.find_all('p', class_='font_8')
                    about = ""
                    for t in text:
                        about += t.text.strip()
                        about += " "
                    # print(about)
                except AttributeError:
                    about = None
                except TypeError:
                    about = None
                # About will either be found and be some text or be None.
                # print(about)

                artist_data_pack = [name, None, country, about]
                # artist_data_pack = [name, born, country, about]
                # pack = [name, born, country, about]
                # Updating KEY_INFO dictionary.
                KEY_INFO[artist_url] = db.Artist.key_maker(artist_data_pack)
                key = KEY_INFO.get(artist_url)
                # Updating the dB with artist listings.
                TheAuthour.write_artist(*artist_data_pack)

                # key = db.Artist.key_maker(artist_data_pack)
                # pack = [name, born, country, about]
                driver.quit()
                return key
            else:
                driver.quit()
                return None


        else:
            return None

    # ___________ ARTISTS____________________


    # ________________________________________
    # _____________ARTWORK LISTINGS___________

    def get_artwork_listings_slave(self, url):
        # Picks the listings of all the artworks.
        # Artist's data will be picked on artwork_data collection point
        print("Finding page with maximum listings, on www.emergingartistplatform.com\n This might take a while...")
        # active_pages = [1]

        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)

        def page_finder(data):
            page = data[0]
            step = data[1]
            url_ = data[2]
            start = page
            fail_safe = 0
            last_listing = 0

            while (page - start) <= step:
                try:
                    if max(self.active_pages) > page:
                        break
                    url1 = url_ + str(page)
                    driver.get(url1)
                    soup_ = BeautifulSoup(driver.page_source, 'lxml')

                    listings_ = soup_.find('div', class_='_1hM3_ jw2qu')
                    listings_ = listings_.find_all('li')
                    print(f"Number of listings : {len(listings_)} on page {page}")
                    if len(listings_) > last_listing:
                        last_listing = len(listings_)
                    elif last_listing == len(listings_):
                        return page
                    page += 1

                    fail_safe = 0

                except AttributeError:
                    # print("B")
                    fail_safe += 1
                    if fail_safe >= 5:
                        print(f"PAGE FAILED TO LOAD : {page}")
                        break

            if page == start:
                return None
            else:
                return page - 1

        steps = 10
        thread = [(i, steps, url) for i in range(500, 0, -steps)]
        # print(thread)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(page_finder, thread)

        for result in results:
            if result is not None:
                # print(result)
                self.active_pages.append(result)

        print(self.active_pages)
        max_page = max(self.active_pages)
        driver.quit()
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        # max_page = 20

        url = url + str(max_page)
        print(url)

        while True:
            try:
                # This website does not bode well with headers.
                driver.get(url)
                soup = BeautifulSoup(driver.page_source, 'lxml')
                listings = soup.find('div', class_='_1hM3_ jw2qu')
                listings = listings.find_all('li')
                for listing in listings:
                    link = listing.find('a', class_='_34sIs').get('href')
                    if link not in self.artwork_listings:
                        self.artwork_listings.append(link)
                break
            except AttributeError:
                pass
        driver.quit()


    def get_artwork_listings_master(self):
        # Takes the list artwork listings and form it, for each url,
        # 1.
        # 2. Picks artwork(product) listings
        self.get_artwork_listings_slave(self.website.start_url)

    # Gets artist data as well through slave -> get_artist_data -> write_artist_data
    def get_artist_id(self, artist_url):
        # We go to artist page to pick data we need to make the ARTIST_INFO key.

        artist_id = None
        if artist_url in KEY_INFO.keys():
            # print("\n\n\n\nA:\n\n\n\n")
            key = KEY_INFO[artist_url]
            if key in ARTIST_INFO.keys():
                artist_id = ARTIST_INFO[key]
                return artist_id

        # Key maker here, writes the artist data in the db. Makes it much simpler. Nah?
        key = self.key_maker(artist_url)
        if key is not None and artist_url is not None:
            if key in ARTIST_INFO.keys():
                artist_id = ARTIST_INFO.get(key)
                return artist_id
                # print(artist_id)
            else:
                print("FATAL ERROR :: Artist_id not found.")
        else:
            # If it ever comes to here, the page will not have an Artist
            print("FATAL ERROR :: Artist_id not found. Artist_url broken")
        # Let's return None here, and not pick rest of the data if the artist_id is not found.
        # Artist id is used in artworks table only.
        return artist_id

    # ________________________________________
    # _____________SELLERS____________________

    def get_seller_id(self, seller_url) -> int:
        # Fetches seller_data, writes it in db, and returns seller_id.
        # bundle = [seller_url, self.website.platform, 'KAZoART', None, url]
        seller_id = None

        if seller_url is not None:
            if seller_url in SELLER_INFO.keys():
                seller_id = SELLER_INFO.get(seller_url)
                # print(seller_id)
            else:
                # If code reaches here then the entry for seller doesn't already exists. Let's call get_seller_data
                # again with seller_url
                # GET_SELLER_DATA IS NOT ACTIVE FOR THIS SITE.
                # self.get_seller_data(seller_url)
                # wait for a second to make sure that transaction is smooth. Activate this line if errors are thrown.
                # time.sleep(1)
                # Try to fetch seller data again.
                if seller_url in SELLER_INFO.keys():
                    seller_id = SELLER_INFO.get(seller_url)
                else:
                    # Make a Kazoart style bundle, and write it to obtain a seller_id.
                    # [seller_url, platform_id(from name), Seller's name, Location, website]
                    bundle = [seller_url, self.website.platform, 'EMERGINGARTISTPLATFOM', None, seller_url]
                    # Writing to db.
                    TheAuthour.write_seller(*bundle)
                    # This should generate the seller_id we so desperately desire.
                    # time.sleep(1)
                if seller_url in SELLER_INFO.keys():
                    seller_id = SELLER_INFO.get(seller_url)
                else:
                    print("FATAL ERROR :: Seller_id not found.")
        else:
            print("FATAL ERROR :: Seller_id not found.")
        # Let's return seller_id, even if it's None. This will stop the get_artwork_Data_slave from gathering
        # data beyond rule 3 check .
        return seller_id

    # def get_seller_data(self, url):
    #     # Caller :: get_artwork_data_slave and get_seller_id
    #     visited.discard(url)
    #     soup = TheMiner.fetch_page(url)
    #
    #     if soup is not None:
    #
    #         # Seller's Name
    #         print(seller_name)
    #         # Code will break if seller's name is not found
    #
    #         # Location
    #         try:
    #             print(location)
    #         except AttributeError:
    #             location = None
    #
    #         # Website
    #         try:
    #             print(website)
    #         except AttributeError:
    #             website = None
    #         except TypeError:
    #             website = None
    #
    #         bundle = [url, self.website.platform, seller_name, location, website]
    #         print(bundle)
    #         TheAuthour.write_seller(*bundle)

    # ________________________________________

    # _____________ARTWORK DATA___________

    # Does major mining operations.
    def get_artwork_data_slave(self, url, driver):

        driver.get(url)
        soup = BeautifulSoup(driver.page_source, url)
        if soup is not None:

            # Field initiation ::

            artwork = None
            price = None
            type_ = None
            dimensions = None
            frame = None
            authenticity = None
            about = None
            artist_id = None
            image_loc = None
            year = None
            support = None
            signature = None
            # Material to be added to technique
            technique = ""

            seller_id = None
            artist = None
            medium = None

            # Medium must always have "Painting" or "Sculpture" (RULE :: 2)
            # if "/painting/" in str(url):
            #     medium = "Painting"  # (painting or sculpture)
            # elif "/sculpture/" in str(url):
            #     medium = "Sculpture"
            # else:
            #     # So that url leaks don't break the code.
            #     medium = None

            # Seller_id
            try:
                seller_url = soup.find('div', class_='WncCi').find('a')['href']
                seller_id = self.get_seller_id(seller_url)
            except AttributeError or TypeError:
                # Seller doesn't have a page.
                try:
                    seller_url = soup.find('div', class_='WncCi').text.strip()
                    if seller_url in SELLER_INFO.keys():
                        seller_id = SELLER_INFO.get(seller_url)
                    else:
                        # Make a Kazoart style bundle, and write it to obtain a seller_id.
                        # [seller_url, platform_id(from name), Seller's name, Location, website]
                        bundle = [seller_url, self.website.platform, 'EMERGINGARTISTPLATFOM', None, None]
                        # Writing to db.
                        TheAuthour.write_seller(*bundle)
                        # This should generate the seller_id we so desperately desire.
                        # time.sleep(1)
                        seller_id = SELLER_INFO.get(seller_url)
                except AttributeError:
                    pass

            # We'll let the seller name be seller_url if the url is not found.

            # Artist_id
            try:
                artist_url = soup.find('div', class_='WncCi').a.get('href')
                if str(artist_url).endswith(".com"):
                    artist_url = re.sub('.com', "", artist_url)
                    artist_url = re.sub('emergingartistplatform', 'emergingartistplatform.com', artist_url)
                artist_id = self.get_artist_id(artist_url)

            except AttributeError:
                try:
                    artist_url = soup.find('div', class_='WncCi').text.strip()
                    country = None
                    a = soup.find_all('pre')
                    for b in a:
                        if b.get('data-hook') == 'description':
                            p = b.find_all('p')
                            for j in p:
                                if 'Country' in j.text or 'country' in j.text or 'COUNTRY' in j.text:
                                    title = j.text.split(":")
                                    country = title[-1].strip()

                    artist_data_pack = [artist_url, None, country, None]
                    # artist_data_pack = [name, born, country, about]
                    # pack = [name, born, country, about]
                    # Updating KEY_INFO dictionary.
                    KEY_INFO[artist_url] = db.Artist.key_maker(artist_data_pack)
                    key = KEY_INFO.get(artist_url)
                    # Updating the dB with artist listings.
                    TheAuthour.write_artist(*artist_data_pack)
                    artist_id = ARTIST_INFO[key]
                except AttributeError:
                    artist_id = None

            # Continue fetching data only if seller_id, artist_id and medium are found. (RULE :: 3, 4)
            if seller_id is not None and artist_id is not None:
                try:
                    a = soup.find_all('span')
                    t = ""
                    for b in a:
                        if b.get('data-hook') == "formatted-primary-price":
                            # print(b.text)
                            for p in b.text:
                                if str(p).isnumeric() or str(p) == ".":
                                    t += p
                    price = float(t) * rate
                    # print(price)
                    # Price
                    # print(price)
                except AttributeError:
                    price = None
                except ValueError:
                    price = None

                # RULE : 5
                if price is not None:

                    # Find artist, artwork, year, type_(N/A), dimensions, support, frame, signature, authenticity,
                    # about, image_loc(actual url of the image), and technique

                    # Wish the code to break if either Artist's name or Artwork's name are not found.
                    # Artist
                    artist = soup.find('div', class_='WncCi').text.strip()
                    # print(artist)

                    # Artwork
                    a = soup.find_all('pre')
                    for b in a:
                        if b.get('data-hook') == 'description':
                            p = b.find_all('p')
                            for j in p:
                                if 'Title' in j.text or 'title' in j.text or 'TITLE' in j.text:
                                    title = j.text.split(":")
                                    artwork = title[-1].strip()
                                    if len(artwork) >= 255:
                                        artwork = artwork[0:255]
                                    # print(artwork)

                                if 'Date' in j.text:
                                    date = j.text.split(":")
                                    year = date[-1].strip()
                                    # print(year)

                                if 'Size' in j.text:
                                    dimensions = j.text.split(":")
                                    dimensions = dimensions[-1].strip()
                                    # print(dimensions)

                                if 'Medium' in j.text:
                                    technique = j.text.split(":")
                                    technique = technique[-1].strip()
                                    # print(technique)

                                if len(j.text.split(":")) == 1 and about is None:
                                    about = j.text[-1].strip()

                    # Medium (RULE : 3)
                    if "Sculptures" in self.website.start_url:
                        medium = "Sculpture"
                    else:
                        medium = "Painting"

                    # image_loc
                    image = soup.find('div', class_='main-media-image-wrapper-hook')
                    image = image.find('div', id='get-image-item-id')
                    image_loc = image.get('href')

                    # print(image_loc)

                    artwork_bundle = {"artwork_title": artwork, "artist_name": artist, "year": year, "price": price,
                                      "Medium": medium, "Type": type_, "Dimensions": dimensions, "Support": support,
                                      "Frame": frame, "Signature": signature, "Authenticity": authenticity,
                                      "About": about, "platform": self.website.platform, "image_addr": image_loc,
                                      "seller_id": seller_id, "artist_id": artist_id, "url": url,
                                      "technique": technique}

                    TheAuthour.write_artwork_price_image(**artwork_bundle)
                else:
                    print(f"Skipping {url}\n PRICE : {price}")
            else:
                print(f"Skipping : {url}\nSeller_id = {seller_id}, Artist_id = {artist_id}, medium = {medium}")
        else:
            print(f"Soup not returned for {url}")

    def get_artwork_data_master(self):
        # while True:
        #     if len(self.artwork_listings) == 0:
        #         break
        #     sir = []
        #     for i in range(50):
        #         if len(self.artwork_listings) > 0:
        #             sir.append((self.artwork_listings.pop()))
        #         else:
        #             break
        #
        #     with concurrent.futures.ThreadPoolExecutor() as executor:
        #         results = executor.map(self.get_artwork_data_slave, sir)
        #     for result in results:
        #         print("AA")
        #         # pass
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        for link in self.artwork_listings:
            self.get_artwork_data_slave(link, driver)
        driver.quit()


    def miner(self):

        # self.get_artist_listings()
        # print(kazoart.artist_listings)
        # print(len(self.artist_listings))

        self.get_artwork_listings_master()
        # get_artwork_listings_master -> get_artwork_listings_slave
        # We're still not done with artist data
        print(len(self.artwork_listings))

        self.get_artwork_data_master()

        # DATA COLLECTION COMPLETED FOR THIS MODULE.
        # DOWNLOADING IMAGES NOW.
        print("downloading images now.")
        TheMiner.sir_image_manager(chunk_size=100)


def main():
    sellers = db.Sellers()
    sellers.read_data_sellers()
    artists = db.Artist()
    artists.read_artist_data()

    agent = Website('https://www.emergingartistplatform.com',
                    'https://www.emergingartistplatform.com/browse?Collection=Paintings&page=',
                    "EMERGINGARTISTPLATFOM")
    eap = EAP(agent)
    eap.miner()



    agent = Website('https://www.emergingartistplatform.com',
                    'https://www.emergingartistplatform.com/browse?Collection=Sculptures&page=',
                    "EMERGINGARTISTPLATFOM")
    eap = EAP(agent)
    eap.miner()

    # sellers = db.Sellers()
    # sellers.read_data_sellers()



if __name__ == "__main__":
    main()
