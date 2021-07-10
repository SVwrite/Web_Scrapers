import concurrent.futures
# import re
import time

# Importing data structures
from packets.websiteds import Website
from packets.dataStructures import TheAuthour

from packets.TheMiner import TheMiner
from packets import dbmanip as db
from packets.global_vars import SELLER_INFO, ARTIST_INFO, visited, KEY_INFO


class Kazoart:
    # Kazoart does not have separate sellers. The seller will be concluded to be Kazoart itself.
    # Make an entry for it as soon as the function starts and save it in the dB. SELLER, LOCATION, WEBSITE,
    # ID(generated)
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
            artist_thumbnails = soup.find('div', class_='artists-thumbnails')
            artist_thumbnails = artist_thumbnails.find_all('div', class_='artists-thumbnails__item')
            for artist in artist_thumbnails:
                self.artist_listings.append(str(artist.a['href']).strip())

    def get_artist_data(self, soup, url):
        # Called by self.get_artwork_listings_slave()
        # Pick name, born, country, about

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
            # pack = [name, born, country, about]
            # self.write_artist_data(*artist_data_pack)
            KEY_INFO[url] = db.Artist.key_maker(artist_data_pack)
            TheAuthour.write_artist(*artist_data_pack)

    # ________________________________________
    # _____________ARTWORK LISTINGS___________

    def get_artwork_listings_slave(self, url):
        d = 1

        def recurrent(i_url, depth):
            soup = TheMiner.fetch_page(i_url)
            if soup is not None:
                product_list = soup.find('div', class_='product-list-wrapper')
                product_list = product_list.find_all('div', class_='grid-item')
                for product in product_list:
                    item_price = str(product.find('div', class_='grid-item-price').text).strip().upper()
                    # Discard the data that does not have a price.
                    if not item_price == "SOLD":
                        product_link = str(product.a['href']).strip()
                        # Discarding urls that do not take us to paintings and sculptures. (RULE : 1)
                        if "/sculpture/" in product_link or "/painting/" in product_link:
                            if product_link not in self.artwork_listings:
                                self.artwork_listings.append(product_link)

                # Get artist data if depth is "1", if depth is more than "1" ignore this block.
                # To pick the artist's data, from the first page of the listings.
                if depth == 1:
                    # Calling the function to fetch the artist data, and return artist_id
                    self.get_artist_data(soup, i_url)

                next_page = soup.find('div', class_='page-browser')
                if next_page is not None:
                    next_page = next_page.find('div', class_='page-browser-numbers')
                    next_page = next_page.find_all('a', class_='page-browser-item ')
                    for next_ in next_page:
                        next_ = self.website.domain + str(next_['href'])
                        depth += 1
                        recurrent(next_page, depth)

        recurrent(url, d)

    def get_artwork_listings_master(self):
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
                # Process and create the bundle here.
                bundle = [seller_url, self.website.platform, 'KAZoART', None, seller_url]
                # Writing to db.
                TheAuthour.write_seller(*bundle)

                if seller_url in SELLER_INFO.keys():
                    seller_id = SELLER_INFO.get(seller_url)
                else:
                    print("FATAL ERROR :: Seller_id not found.")
        else:
            print("FATAL ERROR :: Seller_id not found.")
        # Let's return seller_id, even if it's None.
        return seller_id

        # ________________________________________

    # _____________ARTWORK DATA___________

    # Does major mining operations.
    def get_artwork_data_slave(self, url):
        soup = TheMiner.fetch_page(url)
        if soup is not None:

            # Field initiation :: Artwork_title, artist, price, seller_id :: (picked),
            # medium, type, dimension, frame, authenticity, about  :: year, support, signature
            # artist_id, Image_loc = None

            seller_id = None
            artist = None
            artwork = None
            price = None

            # Material to be added to technique
            technique = ""

            # Medium must always have "Painting" or "Sculpture" (RULE :: 2)
            if "/painting/" in str(url):
                medium = "Painting"  # (painting or sculpture)
            elif "/sculpture/" in str(url):
                medium = "Sculpture"
            else:
                # So that url leaks don't break the code.
                medium = None

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

            seller_url = str(soup.find('div', class_='product-artist').a.get('href')).strip()
            # We want the code to break if this entry is not found so that we can fix it.
            # THE PAGE MUST HAVE A SELLER.

            # Seller_id
            seller_id = self.get_seller_id(seller_url)

            # Artist_id
            artist_url = seller_url
            artist_id = self.get_artist_id(artist_url)

            # Continue fetching data only if seller_id, artist_id and medium are found. (RULE :: 3, 4)
            if seller_id is not None and artist_id is not None and medium is not None:
                A = soup.h1
                B = A.find('div', class_='product-artist')
                artist = str(B.a.text).strip()
                # Artist
                # print(artist)

                artwork = str(A.find('div', class_='product-name').text).strip()
                # Artwork
                # print(artwork)

                price = str(soup.find('div', class_='product-price').find('div', class_='p-price-container').text).strip()
                temp = ""
                for i in price:
                    if i.isdigit():
                        temp += i
                    if i == ".":
                        temp += i
                price = float(temp)
                # Price
                # print(price)

                product_details_desc = soup.find('div', class_='product-details_desc')
                product_details = product_details_desc.find_all('div', class_='tech-item')

                for detail in product_details:
                    label = str(detail.find('div', class_='tech-label').text).strip().upper()
                    value = str(detail.find('div', class_='tech-value').text).strip()
                    # print(label)
                    # print(value)
                    # For KAZoART, technique(info) goes under Medium, and Material(info) goes under Technique
                    if label == 'TECHNIQUE':
                        technique += " "
                        technique += value
                        technique.strip()
                    elif label == 'TYPE':
                        type_ = value
                    elif label == 'MATERIAL':
                        technique += " "
                        technique = value
                        technique.strip()
                    elif label == 'DIMENSIONS':
                        dimensions = value
                    elif label == 'FRAMING':
                        frame = value
                    elif label == 'QUALITY GUARANTEE':
                        authenticity = value

                    # if that is not here, it'll throw errors.
                    # elif label == ''

                try:
                    about = str(product_details_desc.find('div', class_='desc text-1').text).strip()
                except AttributeError:
                    about = None

                image_loc = soup.find('div', class_='product-left').find('div', class_='img-wrapper').img.get('src')
                # print(image_loc)

                # self, artwork_title=None, artist_name=None, year=None, price=None, Dimensions=None, Medium=None,
                #     Type=None, Support=None, Frame=None, Signature=None, Authenticity=None, About=None,
                #      platform=None, image_addr=None, seller_id=None, artist_id=None)

                artwork_bundle = {"artwork_title": artwork, "artist_name": artist, "year": year, "price": price,
                                  "Medium": medium, "Type": type_, "Dimensions": dimensions, "Support": support,
                                  "Frame": frame, "Signature": signature, "Authenticity": authenticity,
                                  "About": about, "platform": self.website.platform, "image_addr": image_loc,
                                  "seller_id": seller_id, "artist_id": artist_id, "url": url, "technique": technique}

                TheAuthour.write_artwork_price_image(**artwork_bundle)
                # self.write_artwork_data(**artwork_bundle)
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
