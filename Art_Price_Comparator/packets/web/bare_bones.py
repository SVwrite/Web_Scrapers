import concurrent.futures
# import re
import time

# Importing data structures
from packets.websiteds import Website
from packets.dataStructures import TheAuthour

from packets.TheMiner import TheMiner
from packets import dbmanip as db
from packets.global_vars import SELLER_INFO, ARTIST_INFO, visited, KEY_INFO


class BareBones:
    # NOTES ABOUT THE SITE
    def __init__(self, website):
        self.website = website
        self.artist_listings = []
        self.artwork_listings = []

    @staticmethod
    def key_maker(artist_url):
        visited.discard(artist_url)
        soup = TheMiner.fetch_page(artist_url)
        if soup is not None:
            artist_resume = soup.find('div', class_='artist-resume').find('div', class_='artist-resume_text')
            name = artist_resume.h1.text.strip()
            print(name)
            # If an error occurs here, its because the page layout has changed and thus the code needs to be fixed

            if name is not None:
                try:
                    country = artist_resume.find('p', class_='location').text.strip().split('\n')
                    country = country[0].split(',')
                    country = country[-1].strip()
                    print(country)
                except AttributeError:
                    country = None

                about = soup.find('div', id='about').text.strip()
                # About will either be found and be some text or be None.
                # print(about)

                artist_data_pack = [name, None, country, about]
                key = db.Artist.key_maker(artist_data_pack)
                # pack = [name, born, country, about]
                return key

        else:
            return None

    # ___________ ARTISTS____________________
    def get_artist_listings(self):
        soup = TheMiner.fetch_page(self.website.start_url)

        if soup is not None:
            artist_thumbnails =
            for artist in artist_thumbnails:
                self.artist_listings.append(artist)

    def get_artist_data(self, soup, url):
        # Called by self.get_artwork_listings_slave()
        # Pick name, born, country, about

        # Name : Pick artist's name here
        print(name)
        # If an error occurs here, its because the page layout has changed and thus the code needs to be fixed

        if name is not None:
            try:
                # Pick artist's country here.
                print(country)
            except AttributeError:
                country = None

            try:
                # Pick birth year here here.
                print(born)
            except AttributeError:
                born = None

            try:
                # Pick artist's description here.
                print(about)
            except AttributeError:
                about = None

            artist_data_pack = [name, born, country, about]
            # pack = [name, born, country, about]
            # Updating KEY_INFO dictionary.
            KEY_INFO[url] = db.Artist.key_maker(artist_data_pack)
            # Updating the dB with artist listings.
            TheAuthour.write_artist(*artist_data_pack)

    # ________________________________________
    # _____________ARTWORK LISTINGS___________

    def get_artwork_listings_slave(self, url):
        d = 1

        def recurrent(i_url, depth):
            soup = TheMiner.fetch_page(i_url)
            if soup is not None:
                # Gather a list of all the products.
                for product in product_list:
                    # Check for price, discard the links that do not have a price.
                    item_price =
                    # Discard the data that does not have a price. (RULE : 6)
                    if not item_price == "SOLD":
                        product_link =
                        # Discarding urls that do not take us to paintings and sculptures. (RULE : 1)
                        if "/sculpture/" in product_link or "/painting/" in product_link:
                            if product_link not in self.artwork_listings:
                                self.artwork_listings.append(product_link)

                # Get artist data if depth is "1", if depth is more than "1" ignore this block.
                # To pick the artist's data, from the first page of the listings.
                if depth == 1:
                    # Calling the function to fetch the artist data, and return artist_id
                    self.get_artist_data(soup, i_url)

                # Find the links to all other pages.
                next_pages =
                for next_page in next_pages:
                    next_page =
                    depth += 1
                    recurrent(next_page, depth)

        recurrent(url, d)

    def get_artwork_listings_master(self):
        # Takes the list artwork listings and form it, for each url,
        # 1. Picks artist's data
        # 2. Picks artwork(product) listings
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.get_artwork_listings_slave, self.artist_listings)

        for result in results:
            pass

    # Gets artist data as well through slave -> get_artist_data -> write_artist_data
    def get_artist_id(self, artist_url):
        # We go to artist page to pick data we need to make the ARTIST_INFO key.

        artist_id = None
        if artist_url in KEY_INFO.keys():
            # print("\n\n\n\nA:\n\n\n\n")
            key = KEY_INFO[artist_url]
            artist_id = ARTIST_INFO[key]
        else:
            key = self.key_maker(artist_url)
            if key is not None and artist_url is not None:
                if key in ARTIST_INFO.keys():
                    artist_id = ARTIST_INFO.get(key)
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
                self.get_seller_data(seller_url)
                # wait for a second to make sure that transaction is smooth. Activate this line if errors are thrown.
                # time.sleep(1)
                # Try to fetch seller data again.
                if seller_url in SELLER_INFO.keys():
                    seller_id = SELLER_INFO.get(seller_url)
                else:
                    # Make a Kazoart style bundle, and write it to obtain a seller_id.
                    bundle = [seller_url, self.website.platform, 'BAREBONES', None, seller_url]
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

    def get_seller_data(self, url):
        # Caller :: get_artwork_data_slave and get_seller_id
        visited.discard(url)
        soup = TheMiner.fetch_page(url)

        if soup is not None:

            # Seller's Name
            print(seller_name)
            # Code will break if seller's name is not found

            # Location
            try:
                print(location)
            except AttributeError:
                location = None

            # Website
            try:
                print(website)
            except AttributeError:
                website = None
            except TypeError:
                website = None

            bundle = [url, self.website.platform, seller_name, location, website]
            print(bundle)
            TheAuthour.write_seller(*bundle)

        # ________________________________________

    # _____________ARTWORK DATA___________

    # Does major mining operations.
    def get_artwork_data_slave(self, url):
        soup = TheMiner.fetch_page(url)
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
            # Medium must always have "Painting" or "Sculpture" (RULE :: 2)
            if "/painting/" in str(url):
                medium = "Painting"  # (painting or sculpture)
            elif "/sculpture/" in str(url):
                medium = "Sculpture"
            else:
                # So that url leaks don't break the code.
                medium = None

            # Seller_id
            seller_url =
            # We'll let it crash at seller_url not found because that is the way of the world.
            seller_id = self.get_seller_id(seller_url)

            # Artist_id
            artist_url =
            artist_id = self.get_artist_id(artist_url)

            # Continue fetching data only if seller_id, artist_id and medium are found. (RULE :: 3, 4)
            if seller_id is not None and artist_id is not None and medium is not None:



                try :
                    price
                    temp = ""
                    for i in price:
                        if i.isdigit():
                            temp += i
                        if i == ".":
                            temp += i
                    price = float(temp)
                    # Price
                    # print(price)
                except AttributeError:
                    price = None
                except ValueError:
                    price = None

                # RULE : 5
                if price is not None:

                    # Find artist, artwork, year, type_, dimensions, support, frame, signature, authenticity,
                    # about, image_loc(actual url of the image), and technique

                    # Wish the code to break if either Artist's name or Artwork's name are not found.
                    # Artist
                    print(artist)

                    # Artwork
                    print(artwork)

                    try:
                        about =
                    except AttributeError:
                        about = None

                    artwork_bundle = {"artwork_title": artwork, "artist_name": artist, "year": year, "price": price,
                                      "Medium": medium, "Type": type_, "Dimensions": dimensions, "Support": support,
                                      "Frame": frame, "Signature": signature, "Authenticity": authenticity,
                                      "About": about, "platform": self.website.platform, "image_addr": image_loc,
                                      "seller_id": seller_id, "artist_id": artist_id, "url": url, "technique": technique}

                    TheAuthour.write_artwork_price_image(**artwork_bundle)
                else :
                    print(f"Skipping {url}\n PRICE : {price}")
            else:
                print(f"Skipping : {url}\nSeller_id = {seller_id}, Artist_id = {artist_id}, medium = {medium}")

    def get_artwork_data_master(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.get_artwork_data_slave, self.artwork_listings)
        for result in results:
            pass

    def miner(self):
        self.get_artist_listings()
        # print(kazoart.artist_listings)
        print(len(self.artist_listings))

        self.get_artwork_listings_master()
        # get_artwork_listings_master -> get_artwork_listings_slave -> get_artist_data -> write_artist_data
        # So we're done with artist data.
        print(len(self.artwork_listings))

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

    kazoart_webagent = Website('https://www.kazoart.com',
                               'https://www.kazoart.com/en/artistes/technique/sculpture?eme=1',
                               "KAZOART")
    kazoart = Kazoart(kazoart_webagent)
    kazoart.miner()

    time.sleep(10)

    kazoart_webagent = Website('https://www.kazoart.com',
                               'https://www.kazoart.com/en/artistes/technique/peintures?eme=1',
                               "KAZOART")
    kazoart = Kazoart(kazoart_webagent)
    kazoart.miner()


if __name__ == "__main__":
    main()
