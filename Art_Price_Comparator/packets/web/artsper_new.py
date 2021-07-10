import concurrent.futures
import re
import time

# Importing data structures
from packets.websiteds import Website
from packets.dataStructures import TheAuthour

from packets.TheMiner import TheMiner
from packets import dbmanip as db
from packets.global_vars import SELLER_INFO, ARTIST_INFO, visited, KEY_INFO


class Artsper:

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
        url = self.website.start_url

        def recur(i_url, depth):
            soup = TheMiner.fetch_page(i_url)
            if soup is not None:
                figures = soup.find_all('figure')
                for figure in figures:
                    self.artist_listings.append(str(figure.a['href']).strip())

            if depth == 1:
                next_ = []
                listings = soup.find('div', class_="paginator")
                listings = listings.find_all('a')
                for lis in listings:
                    u = self.website.url_maker(lis['href'])
                    # Dealing with sites that throw the scraper on french webpages of the artworks.!!
                    if "oeuvres-d-art-contemporain" in u:
                        re.sub("oeuvres-d-art-contemporain", "contemporary-artworks", u)
                    if u not in next_:
                        next_.append(u)
                for link in next_:
                    recur(link, depth+1)

        recur(url, 1)

    def get_artist_data(self, soup, url):
        # Called by self.get_artwork_listings_slave()
        # Pick name, born, country, about

        # PICKING ARTIST DATA
        A = soup.find('div', id='biography')
        # Artist's name
        name = A.h1.text.strip()
        # print(name)
        # Code should break if the name goes missing

        try:
            # Born
            A = soup.find('div', id='biography')
            B = A.find('div', class_='sub-title col-sm-9 col-xs-12')
            bo = B.find('span', class_='birthday-date').text
            born = ""
            for b in bo:
                if b.isdigit():
                    born += b

            born = int(born)
            # print(born)
        except AttributeError:
            born = None

        try:
            # Country
            A = soup.find('div', id='biography')
            B = A.find('div', class_='sub-title col-sm-9 col-xs-12')
            country = B.span.text.strip()
            # print(country)
        except AttributeError:
            country = None

        try:
            # About
            A = soup.find('div', id='biography')
            about = A.find('div', class_='col-sm-9 col-xs-12 biography').text.strip()
            ab = about.split("  ")
            about = ''
            for a in range(len(ab) - 1):
                b = ab[a]
                about = about + "\n" + b.strip()
            about = about.strip()
            # print(about)
        except AttributeError:
            about = None

        artist_data_pack = [name, born, country, about]
        KEY_INFO[url] = db.Artist.key_maker(artist_data_pack)
        TheAuthour.write_artist(*artist_data_pack)

    def get_artist_id(self, artist_url):
        # We go to artist page to pick data we need to make the ARTIST_INFO key.
        # print(f"\n\n\n\nARTIST_ID_GET:\n{artist_url}\n{KEY_INFO}\n\n\n\n")

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
    # _____________ARTWORK LISTINGS___________

    def get_artwork_listings_slave(self, url):
        # Called by master.
        d = 1

        def recurrent(i_url, depth):
            soup = TheMiner.fetch_page(i_url)
            if soup is not None:

                artwork = soup.find('div', class_="catalog")
                artwork = artwork.find_all('figure')
                for art in artwork:
                    # If listing is sold, don't pick it up.
                    try:
                        sold = art.find('p', class_='price soldout sold').text
                        sold = True
                    except AttributeError:
                        sold = False

                    link = art.a['href']
                    if 'oeuvres-d-art-contemporain' in link:
                        link = re.sub('oeuvres-d-art-contemporain', 'contemporary-artworks', link)
                    if link not in self.artwork_listings and not sold:
                        la = str(link).split('/')
                        if 'painting' in la or 'sculpture' in la:
                            self.artwork_listings.append(link)

                if depth == 1:
                    # Calling the function to fetch the artist data, and return artist_id
                    self.get_artist_data(soup, i_url)
                    # This block picks the urls of pages for artists who have listings on more than one pages.
                    # And launches the code to pick the artwork_listings and artist data
                    try:
                        next_ = []
                        listings = soup.find('div', class_="paginator")
                        listings = listings.find_all('a')
                        for li in listings:
                            ur = self.website.url_maker(li['href'])
                            next_.append(ur)
                            # print(ur)
                        for ur in next_:
                            recurrent(ur, depth+1)
                    except AttributeError:
                        # For Artists who do not have a second listings page. They'll throw an AttributeError
                        pass

        recurrent(url, d)

    def get_artwork_listings_master(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.get_artwork_listings_slave, self.artist_listings)

        for result in results:
            pass

    # Gets artist data as well through slave -> get_artist_data -> write_artist_data

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
                    bundle = [seller_url, self.website.platform, 'ARTSPER', None, seller_url]
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
        # Caller :: get_artwork_data_slave
        visited.discard(url)
        soup = TheMiner.fetch_page(url)

        # print("A")
        if soup is not None:
            # print("B")

            A = soup.find('div', id='top-seller')
            seller_name = A.h1.text.strip()
            # print(seller_name)
            # Code will break if seller's name is not found

            try:
                location = A.find('p', class_="subtitle").text.strip().split(',')
                location = location[-1].strip()
                # print(location)
            except AttributeError:
                location = None
            try:
                website = str(soup.find('ul', id="websites").a['href']).strip()
                # print(website)
            except AttributeError:
                website = None
            except TypeError:
                website = None

            bundle = [url, self.website.platform, seller_name, location, website]
            # print(bundle)
            TheAuthour.write_seller(*bundle)

    # ________________________________________
    # _____________ARTWORK DATA___________

    def write_price_data(self, price_bundle):
        # Called by write_artwork_data, as it is the class that generates the artwork_id.
        writer = db.Price()
        writer.insert_data_prices(*price_bundle)

    def write_image_data(self, image_bundle):
        # Called by write_artwork_data, as it is the class that generates the artwork_id.
        writer = db.Images()
        writer.insert_data_images(*image_bundle)

    # Does major mining operations.
    def get_artwork_data_slave(self, url):
        soup = TheMiner.fetch_page(url)
        if soup is not None:

            # Field initiation :: Artwork_title, artist, price, seller_id ,
            # medium, type, dimension, frame, authenticity, about  :: year, support, signature
            # artist_id, Image_loc = None

            seller_id = None
            artist = None
            artwork = None
            price = None
            medium = None  # (painting or sculpture)
            technique = ""  # Material and style
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


            try:
                # PRICE
                A = soup.find('section', id='informations')
                price = str(A.find('p', class_='media-price price').text).strip()
                number = ''
                for p in price:
                    if p == '-':
                        break
                    if p.isdigit():
                        number += str(p)
                    if p == ".":
                        number += str(p)

                price = float(number)
                # print(price)
            except AttributeError:
                pass
            except TypeError:
                pass

            # Rule : 5
            if price is not None:

                # Seller_id
                try:
                    seller_url = soup.find('div', id='top-seller').find('a').get('href')
                    if 'galeries-d-art' in str(seller_url):
                        seller_url = re.sub('galeries-d-art', 'art-galleries', seller_url)

                    # If seller_url is found.
                    seller_id = self.get_seller_id(seller_url)
                except AttributeError:
                    # seller_id = None
                    # There are pages where the seller has no other page. Then we make the url ourselves.

                    seller_url = soup.find('div', id='top-seller').find('p', class_='highlight-title').text
                    seller_url = str(seller_url).strip()

                    if seller_url in SELLER_INFO:
                        seller_id = SELLER_INFO[seller_url]
                    else:
                        location = soup.find('div', id='top-seller').find('p', class_='subtitle').text.strip().split(
                            ',')
                        location = str(location[-1]).strip()

                        seller_name = seller_url

                        bundle = [seller_url, self.website.platform, seller_name, location, None]

                        # We write the seller info directly and fetch the seller_id
                        TheAuthour.write_seller(*bundle)
                        seller_id = SELLER_INFO[seller_url]

                # Artist_id
                try:
                    artist_url = soup.find('section', id='informations').find('div', class_='relative').a.get('href')
                    if "oeuvres-d-art-contemporain" in artist_url:
                        re.sub("oeuvres-d-art-contemporain", "contemporary-artworks", artist_url)
                    artist_id = self.get_artist_id(artist_url)
                except AttributeError:
                    artist_id = None
                    print("\n\n\n\n\n")
                    print(url)
                    print("\n\n\n\n\n")
                    time.sleep(50)

                # Medium must always have "Painting" or "Sculpture" (RULE :: 2)
                la = str(url).split('/')
                if 'painting' in la:
                    medium = "Painting "  # (painting or sculpture)
                elif 'sculpture' in la:
                    medium = "Sculpture"
                else:
                    # So that url leaks don't break the code.
                    medium = None

                # IF either the seller id or artist_id are missing, escape the rest. (Rule : 3)
                # If medium is neither Paintings, not Sculptures. We don't fetch data. ( Rule : 2)
                if seller_id is not None and artist_id is not None and medium is not None:
                    # ______________________________MAIN DATA FETCHING________________________
                    A = soup.find('section', id='informations')
                    B = A.find('div', class_='relative')

                    # ARTIST'S NAME
                    artist = B.find('span', class_='primary-title').text.strip()
                    # print(artist)

                    # ARTWORK'S NAME
                    C = B.find('span', class_='secondary-title').text.strip()
                    artwork_ = C.split(',')
                    artwork_title = ""
                    for a in range(len(artwork_) - 1):
                        if a == 0:
                            artwork_title = artwork_[a]
                            continue
                        artwork_title = artwork_title + ", " + artwork_[a].strip()
                    artwork = artwork_title
                    # print(artwork)

                    try:
                        # ARTWORK YEAR
                        year = C.split(',')[-1].strip()
                        # print(year)
                    except IndexError:
                        pass
                        # year = None

                    try:
                        # Image url
                        B = A.find('div', id='img-container')
                        image_loc = B.find('img', id='img_original')['data-src']
                        # print(image_loc)
                    except AttributeError:
                        pass

                    # Contains:: image, dimensions, medium, type, Frame, Support, authenticity, signature
                    try:
                        D = soup.find('div', id='tabs-description').ul
                        E = D.find_all('li')

                        for e in E:
                            a = e.text
                            # Dimensions
                            if 'Dimensions' in a and 'About the artwork' not in a and 'Support' not in a:
                                dimensions = e.find('p', class_='pull-right').strong.text.strip()
                                dim = True
                                # print(dimensions)
                                continue

                            # Medium (Sculpture/Painting) and Technique
                            if 'Medium' in a and 'About the artwork' not in a:
                                technique = e.find('p', class_='pull-right').text.split("   ")
                                # print(technique)
                                temp = ""
                                for t in technique:
                                    if t != "":
                                        temp += t.strip()
                                        temp += " "
                                # medium = medium[0]
                                # technique = medium[1]
                                technique = temp
                                # print(technique)
                                continue

                            # Type
                            if 'Type' in a and 'About the artwork' not in a:
                                type_ = e.find('p', class_='pull-right text-right').text.strip().split('  ')[0]
                                # print(type_)
                                continue

                            # Support (base)
                            if 'Support' in a and 'About the artwork' not in a:
                                try:
                                    f = e.find('p', class_='pull-right text-right').text.strip().split('  ')
                                    support = f[0] + '. ' + f[1].strip('\n')
                                    f = e.find('p', class_='pull-right text-right').strong.text.strip().strip('\n')
                                    support += f
                                except IndexError:
                                    support = e.find('p', class_='pull-right text-right').text.strip()
                                # print(support)
                                continue

                            # Framing
                            if 'Framing' in a and 'About the artwork' not in a:
                                frame = e.find('p', class_='pull-right').text.strip()
                                # print(frame)
                                continue

                            # Signature
                            if 'Signature' in a and 'About the artwork' not in a:
                                signature = e.find('p', class_='pull-right').text.strip()
                                # print(signature)
                                continue

                            # Authenticity
                            if 'Authenticity' in a and 'About the artwork' not in a:
                                authenticity = e.find('p', class_='pull-right text-right').text.strip()
                                # print(authenticity)
                                continue

                            # Artwork Description
                            if 'About the artwork' in a:
                                about = e.find('p', class_="marg-bot-10")
                                if about is not None:
                                    a = e.find('div', class_="description-catalog see-more text-justify").text.strip()
                                    about = about.text.strip()
                                    about += a
                                else:
                                    about = e.find('p', class_='').text.strip()
                                continue
                                # print(about)
                    except AttributeError:
                        pass

                        # self, artwork_title=None, artist_name=None, year=None, price=None, Dimensions=None, Medium=None,
                        #     Type=None, Support=None, Frame=None, Signature=None, Authenticity=None, About=None,
                        #      platform=None, image_addr=None, seller_id=None, artist_id=None)

                    artwork_bundle = {"artwork_title": artwork, "artist_name": artist, "year": year, "price": price,
                                  "Medium": medium, "Type": type_, "Dimensions": dimensions, "Support": support,
                                  "Frame": frame, "Signature": signature, "Authenticity": authenticity,
                                  "About": about, "platform": self.website.platform, "image_addr": image_loc,
                                  "seller_id": seller_id, "artist_id": artist_id, "url": url, "technique" : technique}
                    # print(artwork_bundle)
                    TheAuthour.write_artwork_price_image(**artwork_bundle)
                else:
                    print(f"SELLER ID :: {seller_id},\nARTIST ID :: {artist_id}")
            else:
                # If the price is not available, we skip the entire process.
                print(f"PRICE NOT FOUND : {price} at {url}")
        else:
            print(f"\n\n\n\n\nURL DIDN'T RETURN : {url}\n\n\n\n\n")
            # time.sleep(20)

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
        # # get_artwork_listings_master -> get_artwork_listings_slave -> get_artist_data -> write_artist_data
        # # So we're done with artist data.
        print(len(self.artwork_listings))
        #
        self.get_artwork_data_master()

        # DATA COLLECTION COMPLETED FOR THIS MODULE.
        # DOWNLOADING IMAGES NOW.
        TheMiner.sir_image_manager()


def main():

    # Creating SELLER_INFO === To be used with artwork entry
    sellers = db.Sellers()
    sellers.read_data_sellers()
    # sellers.__del__()
    # Trying to close the connection here throws error. Maybe putting it in a function works.

    # Creating ARTIST_INFO === To be used with artwork entry
    artists = db.Artist()
    artists.read_artist_data()
    # artists.__del__()

    artsperpainters = Website('https://www.artsper.com',
                              'https://www.artsper.com/us/contemporary-artists/youngtalents/sculptors-artists',
                              "ARTSPER")
    artsper = Artsper(artsperpainters)
    artsper.miner()

    artsperpainters = Website('https://www.artsper.com',
                              'https://www.artsper.com/us/contemporary-artists/youngtalents/painters',
                              "ARTSPER")
    
    artsper = Artsper(artsperpainters)
    artsper.miner()




if __name__ == "__main__":
    main()
