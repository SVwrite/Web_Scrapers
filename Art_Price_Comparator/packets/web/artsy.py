import concurrent.futures
# import re
import re
import time

import requests

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from lxml import etree
# Importing data structures
from packets.websiteds import Website
from packets.dataStructures import TheAuthour

from packets.TheMiner import TheMiner, eur as rate
from packets import dbmanip as db
from packets.global_vars import SELLER_INFO, ARTIST_INFO, visited, KEY_INFO


# option = Options()
# option.headless = False
# driver = webdriver.Firefox(options=option)
# driver.get('https://google.co.in')


class Artsy:
    # NOTES ABOUT THE SITE
    def __init__(self, website):
        self.website = website
        self.first_prod_list = []
        self.artist_listings = []
        self.artwork_listings = []

    def link_maker(self, rel_url):
        url = self.website.domain + rel_url
        return url

    # ___________ ARTISTS____________________

    # Gets artist data as well through slave -> get_artist_data -> write_artist_data
    def get_artist_id(self, artist_url):
        # We go to artist page to pick data we need to make the ARTIST_INFO key.

        artist_id = None
        if artist_url in KEY_INFO.keys():
            key = KEY_INFO.get(artist_url)
            if key in ARTIST_INFO.keys():
                artist_id = ARTIST_INFO.get(key)
            return artist_id
        else:
            # self.artist_id_slave (key_maker) returns the artist_id
            artist_id = self.artist_id_slave(artist_url)
            return artist_id

    # The artist_id_slave calls the get_artist data to write the artist data in turn creating the key.
    # Returns artist id

    def artist_id_slave(self, artist_url):
        visited.discard(artist_url)
        soup = TheMiner.fetch_page(artist_url)
        if soup is not None:
            self.get_artist_data(soup, artist_url)
            # Getting the key from KEY_INFO
            if artist_url in KEY_INFO.keys():
                key = KEY_INFO.get(artist_url)
                # Getting artist_id using the key from ARTIST_INFO
                if key in ARTIST_INFO.keys():
                    artist_id = ARTIST_INFO.get(key)
                    return artist_id
                else:
                    print("ARTIST_ID_SLAVE : Artist id not in ARTIST_INFO")
                    return None
            else:
                print("ARTIST_ID_SLAVE : Could not find artist_id")
                return None

        else:
            print("ARTIST_ID_SLAVE : Soup not returned")
            return None

    def get_artist_listings(self):
        # Here the aim is to pick all the product listings -> Artist pages ( artist_listings)
        listy = []

        def recurr(url):
            soup = TheMiner.fetch_page(url)
            if soup is not None:
                try:
                    container = soup.find('div', class_=re.compile(r'LoadingArea__Container-sc-1cnoyb0-2\.*'))
                    artist_thumbnails = container.find_all('div',
                                                           class_=re.compile(r'GridItem__ArtworkGridItem-l61twt-3\.*'))
                    # print(container.prettify())
                    for artist in artist_thumbnails:
                        arti = artist.div.a['href']
                        if self.website.domain in arti:
                            artist = arti
                        else:
                            artist = self.link_maker(arti)
                        if artist not in self.first_prod_list:
                            self.first_prod_list.append(artist)
                except AttributeError:
                    print("Something went wrong for url {}")

                try:
                    next_pages = soup.find('nav', class_=re.compile(r'Box-sc-15se88d-0 Text-sc-18gcpao-0 ibHUpM\.*'))
                    next_pages = next_pages.find_all('a', class_=re.compile(r'Link-oxrwcw-0\.*'))
                    for a in next_pages:
                        link = self.link_maker(a['href'])
                        if link not in listy:
                            listy.append(link)
                except AttributeError:
                    pass

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    beta = executor.map(recurr, listy)
                for alpha in beta:
                    pass

        recurr(self.website.start_url)

        # Now we have an initial list of the products.
        def gal(url):
            soup_ = TheMiner.fetch_page(url)
            if soup_ is not None:
                try:
                    artist_url = soup_.find('div',
                                            class_=re.compile(
                                                r'Box-sc-15se88d-0 GridColumns__Cell-sc-1g9p6xx-1 cviiXL\.*'))
                    artist_url = artist_url.find('a', class_=re.compile(r'Box-sc-15se88d-0 Flex-cw39ct-0\.*'))['href']

                    if self.website.domain in artist_url:
                        pass
                    else:
                        artist_url = self.link_maker(artist_url)
                    if artist_url not in self.artist_listings:
                        self.artist_listings.append(artist_url)

                except AttributeError:
                    pass
                except TypeError:
                    pass
        # Threads fetching the artist pages.
        # print(f"LEN(FIRST PROD LIST) {len(self.first_prod_list)}\n LISTY = {len(listy)}")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(gal, self.first_prod_list)
        for trigger in results:
            pass

    def get_artist_data(self, soup, url):
        # Called by self.get_artwork_listings_slave()
        # Pick name, born, country, about
        # dom = etree.HTML(str(soup))

        # Name : Pick artist's name here
        A = soup.find_all('div', class_=re.compile(r'Box-sc-15se88d-0 GridColumns__Cell-sc-1g9p6xx-1\.*'))
        name = soup.find('h1').text.strip()
        # print(name)
        # If an error occurs here, its because the page layout has changed and thus the code needs to be fixed

        if name is not None:
            try:
                # Pick artist's country here.
                B = A[1].find('h2').text.strip().split(",")
                country = B[0].strip()
                if country == "American":
                    country = "USA"
                elif country == "Japanese":
                    country = "Japan"
                elif "French" in country:
                    country = "France"
                elif "Argentine" in country:
                    country = "Argentina"
                elif "Dutch" in country:
                    country = "Netherlands"
                elif "Indian" in country:
                    country = "India"
                elif "Pakistani" in country:
                    country = "Pakistan"
                elif "Italian" in country:
                    country = "Italy"
                elif "English" in country:
                    country = "UK"
                elif "Chinese" in country:
                    country = "China"
                elif "Hispanic" in country:
                    country = "Spain"
                elif "German" in country:
                    country = "Germany"
                elif "Spanish" in country:
                    country = "Spain"
                elif "Russian" in country:
                    country = "Russia"
                elif "British" in country:
                    country = "UK"
                elif "Mexican" in country:
                    country = "Mexico"
                elif "Brazilian" in country:
                    country = "Brazil"
                elif "Canadian" in country:
                    country = "Canada"
                elif "Belgian" in country:
                    country = "Belgium"
                elif "Israeli" in country:
                    country = "Israel"
                elif "Venezuelan" in country:
                    country = "Venezuela"
                elif "Polish" in country:
                    country = "Poland"
                else:
                    for i in country:
                        if str(i).isnumeric():
                            country = None
                # print(country)

                try:
                    born = str(B[-1]).strip().split("–")
                    born = born[0]
                    t = ""
                    for b in born:
                        if b.isnumeric():
                            t += b
                    born = int(t)
                except ValueError:
                    born = None
                # print(born)
            except AttributeError:
                born = None
                country = None

            try:
                about = None
                # Pick artist's description here.
                about_block = soup.find_all('div', class_=re.compile(r'Box-sc-15se88d-0 Text-sc-18gcpao-0\.*'))
                for a in about_block:
                    if a.text.strip() == 'Bio':
                        # print("A")
                        about = a.nextSibling.text.strip()
                        break
                # print(about)
            except AttributeError:
                about = None

            artist_data_pack = [name, born, country, about]
            # pack = [name, born, country, about]
            # Updating KEY_INFO dictionary.
            KEY_INFO[url] = db.Artist.key_maker(artist_data_pack)
            # Updating the dB with artist listings.
            TheAuthour.write_artist(*artist_data_pack)
            # print("A")

    # ________________________________________
    # _____________ARTWORK LISTINGS___________

    def get_artwork_listings_slave(self, url):
        # Runs on artist_listings.

        soup = TheMiner.fetch_page(url)
        if soup is not None:

            # Gather a list of all the products.
            main_ = soup.find('main', id='main')
            main_ = main_.find('div', class_=re.compile(r'Box-sc-15se88d-0\.*'))
            # print(main.prettify())
            main_ = main_.find('div', class_=re.compile(r'Box-sc-15se88d-0 Shelf__Container-sc-1kdkue-0\.*'))
            # print(main.prettify())
            try:
                main1 = main_.find('div', class_=re.compile(r'Box-sc-15se88d-0 FullBleed-g9qwfe-0\.*'))
                product_list = main1.find_all('li')
            except AttributeError:
                try:
                    main1 = main_.find('div', class_=re.compile(r'Box-sc-15se88d-0 FullBleed-g9qwfe-0\.*'))
                    product_list = main1.find_all('li')
                    # print("REGEX")
                except AttributeError:
                    product_list = None

            if product_list is not None:
                # print(product_list)
                for product in product_list:
                    # All the products here are "Available for Sale."
                    if self.website.domain not in product.a['href']:
                        product_link = self.link_maker(product.a['href'])
                    else:
                        product_link = product.a['href']

                    if product_link not in self.artwork_listings:
                        # print(product_link)
                        self.artwork_listings.append(product_link)

                # Sending the soup to fetch artist's data, make artist listings.
                self.get_artist_data(soup, url)

    def get_artwork_listings_master(self):
        # Takes the list artwork listings and form it, for each url,
        # 1. Picks artist's data
        # 2. Picks artwork(product) listings
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.get_artwork_listings_slave, self.artist_listings)

        for result in results:
            pass
        # TEMP:
        # for link in self.artist_listings:
        #     self.get_artwork_listings_slave(link)

    # ________________________________________
    # _____________SELLERS____________________

    def get_seller_id(self, seller_url) -> int:
        # Fetches seller_data, writes it in db, and returns seller_id.
        # bundle = [seller_url, self.website.platform, 'KAZoART', None, url]
        # print("GET SELLER ID")
        seller_id = None

        if seller_url is not None:
            if seller_url in SELLER_INFO.keys():
                seller_id = SELLER_INFO.get(seller_url)
                return seller_id
                # print(seller_id)
            else:
                # If code reaches here then the entry for seller doesn't already exists. Let's call get_seller_data
                # with seller_url
                self.get_seller_data(seller_url)
                # Try to fetch seller data again.
                if seller_url in SELLER_INFO.keys():
                    seller_id = SELLER_INFO.get(seller_url)
                    # If it is not a url, get_seller_data will fail to make an entry.In that case we move to the next part.
                else:
                    # Make a Kazoart style bundle, and write it to obtain a seller_id.
                    # bundle = [seller_url, platform, Seller's name, location, website]
                    bundle = [seller_url, self.website.platform, seller_url, None, seller_url]
                    # Writing to db.
                    TheAuthour.write_seller(*bundle)
                    # This should generate the seller_id we so desperately desire.
                    # time.sleep(1)
                if seller_url in SELLER_INFO.keys():
                    # This will always run, unless the program is failing unexpectedly.
                    seller_id = SELLER_INFO.get(seller_url)
                else:
                    print("FATAL ERROR :: Seller_id not found.")
        else:
            print("FATAL ERROR :: Seller_id not found.")
        # Let's return seller_id, even if it's None. This will stop the get_artwork_Data_slave from gathering
        # data beyond rule 3 check .
        return seller_id

    def get_seller_data(self, url):
        # Caller :: get_artwork_data_slave and get_seller_id
        # We get to here only after we do not find the seller's info in SELLER_INFO
        # print("GET SELLER DATA")

        visited.discard(url)
        soup = TheMiner.fetch_page(url)

        if soup is not None:
            # print("GET SELLER DATA: SOUP RETURNED")

            seller_name = None
            try:
                # Seller's Name

                seller_box = soup.find('div', id='jumpto--PartnerHeader')
                seller_name = seller_box.h1.text.strip()

                # print(seller_name)
                # Code will break if seller's name is not found
            except AttributeError:
                pass

            if seller_name is not None:
                # print(f"SELLER NAME : {seller_name}")
                # Location
                try:
                    # Location is not available here.
                    location = ""
                    locatio = seller_box.h1.nextSibling()
                    # print(type(locatio))
                    try:
                        location = locatio.text
                    except AttributeError:
                        for l in locatio:
                            location += l.text
                            location += " "
                    # print(location)
                except AttributeError:
                    location = None
                except TypeError:
                    location = None

                # Website
                try:
                    website = soup.find_all('a')
                    for web in website:
                        if "http" in str(web.get('href')):
                            website = web.get('href')
                            print(web.get('href'))
                            break
                    # print(website)
                except AttributeError:
                    website = None
                except IndexError:
                    website = None

                bundle = [url, self.website.platform, seller_name, location, website]
                # print(bundle)
                TheAuthour.write_seller(*bundle)

        # ________________________________________

    # _____________ARTWORK DATA___________

    # Does major mining operations.
    def get_artwork_data_slave(self, url):
        # print("ARTWORK DATA SLAVE STARTS")
        soup = TheMiner.fetch_page(url)
        # print("A")
        if soup is not None:
            # print("ARTWORK DATA SLAVE GETS SOUP")
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
            technique = None

            seller_id = None
            artist = None
            medium = None

            # Medium must always have "Painting" or "Sculpture" (RULE :: 2)
            # print("A.1")

            # Seller_url
            seller_url = None
            seller_box = soup.find_all('div',
                                       re.compile(r'Box-sc-15se88d-0 Flex-cw39ct-0 BorderBoxBase-sc-1072ama-0\.*'))
            for se in seller_box:
                if se.get('data-test') == 'aboutTheWorkPartner':
                    try:
                        seller_url = se.find('a')['href']
                        if self.website.domain not in seller_url:
                            seller_url = self.link_maker(seller_url)
                    except TypeError:
                        seller_url = se.next.next.next.next.text
            # print(seller_url)

            # seller_id
            if seller_url is not None:
                seller_id = self.get_seller_id(seller_url)

            # artist url
            artist_url = None
            artist_box = soup.find_all('div',
                                       re.compile(r'Box-sc-15se88d-0 Flex-cw39ct-0 BorderBoxBase-sc-1072ama-0\.*'))
            for ar in artist_box:
                if ar.get('data-test') == 'artistInfo':
                    try:
                        artist_url = ar.find('a')['href']
                        if self.website.domain not in artist_url:
                            artist_url = self.link_maker(artist_url)
                    except TypeError:
                        pass
            # print(artist_url)

            artist_id = self.get_artist_id(artist_url)
            # print(f"Seller id {seller_id} \nArtist id {artist_id}")
            # except AttributeError:
            #     pass

            # Medium
            try:
                medium = soup.find('dl', class_='Box-sc-15se88d-0 Flex-cw39ct-0 bKPevV').dd.text.strip()
                if "SCULPTURE" in str(medium).upper():
                    medium = "Sculpture"
                elif "PAINTING" in str(medium).upper():
                    medium = "Painting"
                else:
                    medium = None
            except AttributeError:
                pass
            # print(f"Medium {medium}")

            # Continue fetching data only if seller_id, artist_id and medium are found. (RULE :: 3, 4)
            if seller_id is not None and artist_id is not None and medium is not None:

                try:
                    price = soup.find_all('div', class_=re.compile(r'Box-sc-15se88d-0 Text-sc-18gcpao-0\.*'))
                    for p in price:
                        if p.get('data-test') == 'SaleMessage':
                            price = p.text
                            break

                    temp = ""
                    for i in price:
                        if i == "-":
                            break
                        if i.isdigit():
                            temp += i
                        if i == ".":
                            temp += i

                    price = float(temp) * rate
                    # Price
                    # print(price)
                except AttributeError:
                    price = None
                except ValueError:
                    price = None
                except TypeError:
                    price = None

                # RULE : 5
                if price is not None:

                    # Find artist, artwork, year, type_, dimensions, support, frame, signature, authenticity,
                    # about, image_loc(actual url of the image), and technique

                    # Wish the code to break if either Artist's name or Artwork's name are not found.
                    # Artist
                    artist_name = soup.find_all('div', class_=re.compile(r'Box-sc-15se88d-0'))
                    for a in artist_name:
                        if a.get('data-test') == 'artworkSidebar':
                            artist_ = a.find_all('div', class_=re.compile(r'Box-sc-15se88d-0 Text-sc-18gcpao-0\.*'))
                            for a in artist_:
                                if len(a.text.strip()) != 0:
                                    artist = a.text
                                    # print(artist)
                                    break
                            break
                    # print(artist)

                    # Artwork
                    artwork_block = soup.find('h1').text.split(",")
                    artwork = artwork_block[0].strip()
                    try:
                        year = artwork_block[-1].strip()
                        t = ""
                        for y in year:
                            if str(y) == "-":
                                break
                            if str(y).isnumeric():
                                t += y
                        year = int(t)
                    except ValueError:
                        year = None

                    # type(unique or what)
                    try:
                        type_ = soup.find('h1').nextSibling.nextSibling.nextSibling.text.strip()
                    except AttributeError:
                        pass

                    # Dimensions
                    try:
                        dimensions = soup.find('h1').nextSibling.nextSibling.find_all('div')
                        for dim in dimensions:
                            if 'cm' in dim.text:
                                dimensions = dim.text.strip()
                    except AttributeError:
                        pass

                    # Technique
                    try:
                        technique = soup.find('h1').nextSibling.text.strip()
                        # print(technique)

                    except AttributeError:
                        pass

                    # Support, frame, sign, auth, about
                    # frame, auth , sign

                    try:
                        bundle = soup.find_all('div', class_=re.compile(
                            r'Box-sc-15se88d-0 Flex-cw39ct-0 BorderBoxBase-sc-1072ama-0 BorderBox-sc-18mwadn-0 StackableBorderBox-sc-1odyc7i-0\.*'))
                        for b in bundle:
                            if b.get('data-test') == 'aboutTheWorkPartner':
                                bud = b.nextSibling
                                # print(bud.prettify())
                                break
                        bundle = bud.find_all('dl')
                        for dl in bundle:

                            if dl.next.text.strip() == 'Signature':
                                signature = dl.dd.text.strip()
                                continue

                            if dl.dt.text.strip() == 'Certificate of authenticity':
                                authenticity = dl.dd.text.strip()
                                continue

                            if dl.dt.text.strip() == 'Frame':
                                frame = dl.dd.text.strip()
                                continue
                    except AttributeError:
                        pass

                    try:
                        about = soup.find('div', class_='Box-sc-15se88d-0 Text-sc-18gcpao-0  gPzDV').find(
                            'div', class_='ReadMore__Container-sc-1bqy0ya-0 guOJdN'
                        ).p.text.strip().split("  ")

                        t = ""
                        for a in about:
                            t += a.strip()
                            t += " "
                        about = t
                    except AttributeError:
                        about = None

                    # Image location
                    try:
                        image_loc = soup.find_all('div', class_='Box-sc-15se88d-0')
                        for loc in image_loc:
                            if loc.get('data-test') == 'artworkImage':
                                image_loc = loc.find('img').get('src')
                                break
                    except AttributeError:
                        pass

                    artwork_bundle = {"artwork_title": artwork, "artist_name": artist, "year": year, "price": price,
                                      "Medium": medium, "Type": type_, "Dimensions": dimensions, "Support": support,
                                      "Frame": frame, "Signature": signature, "Authenticity": authenticity,
                                      "About": about, "platform": self.website.platform, "image_addr": image_loc,
                                      "seller_id": seller_id, "artist_id": artist_id, "url": url,
                                      "technique": technique}
                    # print(artwork_bundle)

                    TheAuthour.write_artwork_price_image(**artwork_bundle)
                else:
                    pass
                    # print(f"Skipping {url}\n PRICE : {price}")
            else:
                pass
                # print(f"Skipping : {url}\nSeller_id = {seller_id}, Artist_id = {artist_id}, medium = {medium}")
        else:
            pass
            # print(f"SOUP not returned {soup}")

    def get_artwork_data_master(self):
        # i = 0
        # for link in self.artwork_listings:
        #     i += 1
        #     # print(f"VISITING ARTWORK LISTING : {i}")
        #     self.get_artwork_data_slave(link)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.get_artwork_data_slave, self.artwork_listings)
        for result in results:
            pass

    def miner(self):
        # Miner's track : We land on artwork listings page. We pick the listings from there.
        # We pick the Sellers and Artists from artwork pages.
        # From artwork pages we fetch the artwork for sale for artists listed.

        self.get_artist_listings()
        # print(kazoart.artist_listings)
        # print(self.artist_listings)
        # print("ARTIST LISTINGS")
        # print(len(self.artist_listings))
        # time.sleep(10)

        # That the pages where we discarded the links can be visited as well
        for link in self.first_prod_list:
            visited.discard(link)

        self.get_artwork_listings_master()
        # get_artwork_listings_master -> get_artwork_listings_slave -> get_artist_data -> write_artist_data
        # So we're done with artist data.
        # print(f"ARTWORK LISTINGS, {len(self.artwork_listings)}")
        # print(len(self.artwork_listings))
        # time.sleep(10)

        self.get_artwork_data_master()

        # DATA COLLECTION COMPLETED FOR THIS MODULE.
        # DOWNLOADING IMAGES NOW.
        TheMiner.sir_image_manager()


def main():
    # Creating SELLER_INFO === To be used with artwork entry
    sellers = db.Sellers()
    sellers.read_data_sellers()

    # Creating ARTIST_INFO === To be used with artwork entry
    artists = db.Artist()
    artists.read_artist_data()

    webagent = Website('https://www.artsy.net',
                       'https://www.artsy.net/collection/new-and-noteworthy-artists?additional_gene_ids%5B0%5D=painting&additional_gene_ids%5B1%5D=sculpture',
                       'ARTSY')
    artsy = Artsy(webagent)
    artsy.miner()

    time.sleep(10)
    # driver.quit()


if __name__ == "__main__":
    main()
