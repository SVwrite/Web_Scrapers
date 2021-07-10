import concurrent.futures
import re

from packets.TheMiner import TheMiner
from packets.dataStructures import ArtistData, ArtworkData, SellerData
from packets.global_vars import visited, SELLER_INFO
from packets import dbmanip as db
from packets.websiteds import Website



class Artsper1:
    # Kazoart does not have separate sellers. The seller will be concluded to be Kazoart itself.
    # Make an entry for it as soon as the function starts and save it in the dB. SELLER, LOCATION, WEBSITE,
    # ID(generated)
    def __init__(self, website):
        self.website = website
        self.artist_listings = []
        self.artwork_listings = []

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

            artist_data_pack = [url, name, None, country, about]
            self.write_artist_data(*artist_data_pack)

    def write_artist_data(self, *args) -> None:
        # Running the data through dataStructure ArtistData seems redundant as of now. Passing bundle directly to
        # dbmaip class
        bundle = [*args]
        # bundle = [url, name, born, country, about]

        writer = db.Artist()
        # Create artist table if it doesn't already exist
        writer.create_table_artist()
        writer.insert_data_artists(*bundle)
        # ARTIST_INFO has been updated by insert_data_artists() function.

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
                        self.artwork_listings.append(product_link)

                # Get artist data if depth is "1", if depth is more than "1" ignore this block.
                if depth == 1:
                    # Calling the function to fetch the artist data, and return artist_id
                    self.get_artist_data(soup, i_url)

                next_page = soup.find('div', class_='page-browser')
                if next_page is not None:
                    next_page = next_page.find('div', class_='page-browser-next').a
                    if next_page is not None:
                        next_page = self.website.domain + str(next_page['href'])
                        depth += 1
                        recurrent(next_page, depth)

        recurrent(url, d)

    def get_artwork_listings_master(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.get_artwork_listings_slave, self.artist_listings)

        for result in results:
            pass

    # Gets artist data as well through slave -> get_artist_data -> write_artist_data

    # ________________________________________
    # _____________SELLERS____________________

    def write_seller_data(self, *args):
        bundle = [*args]
        # bundle = [url, Seller_name, Location =None, Website = url]

        # Just like the artist class in dataStructures, sellers also seems redundant as of now.
        writer = db.Sellers()
        writer.insert_data_sellers(*bundle)
        # SELLER_INFO has been updated within insert_data_sellers() function.

    def get_seller_data(self, url):
        bundle = [url, 'KAZoART', None, url]
        self.write_seller_data(*bundle)

    # ________________________________________
    # _____________ARTWORK DATA___________

    # Handles artworks, prices, images
    def write_artwork_data(self, **kwargs):
        # kwargs is a dictionary here.

        # self, artwork_title=None, artist_name=None, year=None, price=None, Dimensions=None, Medium=None,
        #     Type=None, Support=None, Frame=None, Signature=None, Authenticity=None, About=None,
        #      platform=None, image_addr=None, seller_id=None, artist_id=None)

        # Getting artwork bundle
        # Passing kwargs by unpacking them.
        artwork_ds = ArtworkData(**kwargs)
        artwork_bundle = artwork_ds.artwork_bundle()

        artwork_write = db.Artwork()
        artwork_id = artwork_write.insert_data_artwork(*artwork_bundle)

        # Getting price bundle. Writing price data
        price_bundle = artwork_ds.price_bundle(artwork_id)
        self.write_price_data()

        # Getting image bundle. Writing image data (images table)
        image_bundle = artwork_ds.image_bundle(artwork_id)
        self.write_image_data(image_bundle)

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

            # Field initiation :: Artwork_title, artist, price, seller_id :: (picked),
            # medium, type, dimension, frame, authenticity, about  :: year, support, signature
            # artist_id, Image_loc = None

            seller_id = None
            artist = None
            artwork = None
            price = None

            # Material to be added to medium
            material = None

            medium = None  # (painting or sculpture)
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
            if seller_url is not None:
                if seller_url in SELLER_INFO:
                    seller_id = SELLER_INFO.get(seller_url)
                    print(seller_id)
                else:
                    self.get_seller_data(seller_url)
                    if seller_url in SELLER_INFO:
                        seller_id = SELLER_INFO.get(seller_url)
                    else:
                        if seller_id is None:
                            print("SIRE THE MATRIX HAS GLITCHED. ENTRY NOT IN SELLER_INFO. WE SHALL BREAK.")
            else:
                if seller_id is None:
                    print("SIRE THE MATRIX HAS GLITCHED. ENTRY NOT IN SELLER_INFO. WE SHALL BREAK.")

            # Artist_id
            if seller_url is not None:
                if seller_url in ARTIST_INFO:
                    artist_id = ARTIST_INFO.get(seller_url)
                    print(artist_id)
                else:
                    if artist_id is None:
                        print("SIRE THE MATRIX HAS GLITCHED. ENTRY NOT IN ARTIST_INFO. WE SHALL BREAK.")
            else:
                # If it ever comes to here, the page will not have a Seller/Artist
                if artist_id is None:
                    print("SIRE THE MATRIX HAS GLITCHED. ENTRY NOT IN ARTIST_INFO. WE SHALL BREAK.")

            A = soup.h1
            B = A.find('div', class_='product-artist')
            artist = str(B.a.text).strip()
            # Artist
            print(artist)

            artwork = str(A.find('div', class_='product-name').text).strip()
            # Artwork
            print(artwork)

            price = str(soup.find('div', class_='product-price').find('div', class_='p-price-container').text).strip()
            temp = ""
            for i in price:
                if i.isdigit():
                    temp += i
            price = int(temp)
            # Price
            print(price)

            product_details_desc = soup.find('div', class_='product-details_desc')
            product_details = product_details_desc.find_all('div', class_='tech-item')

            for detail in product_details:
                label = str(detail.find('div', class_='tech-label').text).strip().upper()
                value = str(detail.find('div', class_='tech-value').text).strip()
                print(label)
                print(value)

                if label == 'TECHNIQUE':
                    medium = value
                elif label == 'TYPE':
                    type_ = value
                elif label == 'MATERIAL':
                    # We don't need material. Adding material to medium??
                    material = value
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

            # If material is None, we don't add it to medium.
            if material is not None:
                # If medium is None, we make it a string before adding material to it.
                if medium is None:
                    medium = ""
                else:
                    medium += " "
                medium += material

            # self, artwork_title=None, artist_name=None, year=None, price=None, Dimensions=None, Medium=None,
            #     Type=None, Support=None, Frame=None, Signature=None, Authenticity=None, About=None,
            #      platform=None, image_addr=None, seller_id=None, artist_id=None)

            artwork_bundle = {"artwork_title": artwork, "artist_name": artist, "year": year, "price": price,
                              "Medium": medium, "Type": type_, "Dimensions": dimensions, "Support": support,
                              "Frame": frame, "Signature": signature, "Authenticity": authenticity,
                              "About": about, "image_addr": image_loc, "seller_id": seller_id,
                              "artist_id": artist_id}

            self.write_artwork_data(**artwork_bundle)

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


class Artsper:

    def __init__(self, website):
        self.listing_pages = []
        self.website = website
        self.artist_listing = []
        self.artwork_listing = []
        # Start mining
        # self.artsper_mine()

    def get_listing_pages(self, url):
        print("Fetching All Listing pages")
        soup = TheMiner.fetch_page(url)
        # Pop out the url from visited so that it can be used again while fetching artists.
        visited.remove(url)
        self.listing_pages.append(url)
        listings = soup.find('div', class_="paginator")
        listings = listings.find_all('a')
        for lis in listings:
            u = self.website.url_maker(lis['href'])
            # Dealing with sites that throw the scraper on french webpages of the artworks.!!
            if "oeuvres-d-art-contemporain" in u:
                re.sub("oeuvres-d-art-contemporain", "contemporary-artworks", u)
            if u not in self.listing_pages:
                self.listing_pages.append(u)

    # self.get_artists :: Caller : self.artsper_mine
    # Calls : TheMiner.fetch_page
    # Populates self.artist_listings with the links for artist's pages.
    # On these pages, the info of the artist and the links for the artworks is available.
    def get_artists(self):
        print("Fetching Artist listing")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # soups = executor.map(TheMiner.fetch_page, self.listing_pages)
            soups = [executor.submit(TheMiner.fetch_page, url) for url in self.listing_pages]

        for future in concurrent.futures.as_completed(soups):
            soup = future.result()
            if soup is not None:
                figures = soup.find_all('figure')
                for figure in figures:
                    self.artist_listing.append(figure.a['href'])
        # Clearing listing_pages list
        self.listing_pages.clear()

    # self.get_artist_data() :: Caller : self.get_artworks() (:: Secondary Caller : self.artsper_mine())
    # Calls : dataStructures.ArtistData
    # writes artist data to the db and returns nothing
    def get_artist_data(self, soup, url):
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     soups = executor.map(TheMiner.fetch_page, self.artist_listing)

        # for soup in soups:

        # PICKING ARTIST DATA
        try:

            A = soup.find('div', id='biography')
            # Artist's name
            name = A.h1.text.strip()
            # print(name)
        except:
            name = None

        try:
            # Born
            A = soup.find('div', id='biography')
            B = A.find('div', class_='sub-title col-sm-9 col-xs-12')
            bo = B.find('span', class_='birthday-date').text
            born = ""
            for b in bo:
                if b.isdigit():
                    born += b
            # print(born)
        except:
            born = None
        try:
            # Country
            A = soup.find('div', id='biography')
            B = A.find('div', class_='sub-title col-sm-9 col-xs-12')
            country = B.span.text.strip()
            # print(country)
        except:
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
        except:

            about = None

        # Writing artist data.
        # The following portion of code needs to be consistent across all the website modules.
        # Just extract the name, born, country and about for the artist and then repeat this portion.

        artist_data = ArtistData(url = url, name=name, born=born, country=country, about=about)

        a_bundle = artist_data.artist_bundle()
        artist_db_agent = db.Artist()
        artist_db_agent.create_table_artist()
        artist_db_agent.insert_data_artists(*a_bundle)

    def get_artworks_master(self, url):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            soups = executor.map(TheMiner.fetch_page, self.artist_listing)

    # Caller :: self.artsper_mine ()
    # Gets artwork listings.!!
    def get_artworks_slave(self, url):
        print("Fetching Artwork listings")
        # print(self.artist_listing)
        listy = []
        # for link in self.artist_listing:
        #     visited.discard(link)


        for soup in soups:


        # This block picks the urls of pages for artists who have listings on more than one pages.
        try:
            listings = soup.find('div', class_="paginator")
            listings = listings.find_all('a')
            for l in listings:
                if l not in listy:
                    ur = self.website.url_maker(l['href'])
                    listy.append(ur)
                    # print(ur)
        except AttributeError:
            # For Artists who do not have a second listings page. They'll throw an AttributeError
            pass

        # We grab the links of all the artworks from all the first pages here.
        self.get_artist_data(soup)
        try:
            artwork = soup.find('div', class_="catalog")
            artwork = artwork.find_all('figure')
            for art in artwork:

                # If listing is sold, don't pick it up.
                try:
                    sold = art.find('p', class_='price soldout sold').text
                    sold = True
                except AttributeError:
                    sold = False

                url = art.a['href']
                if 'oeuvres-d-art-contemporain' in url:
                    url = re.sub('oeuvres-d-art-contemporain', 'contemporary-artworks', url)
                if url not in self.artwork_listing and not sold:
                    la = str(url).split('/')
                    if 'painting' in la or 'sculpture' in la:
                        self.artwork_listing.append(url)

        except AttributeError:
            pass

        # This block is for capturing artwork listings from second, third or later pages. FROM LISTY the list
        with concurrent.futures.ThreadPoolExecutor() as executor:
            soups = executor.map(TheMiner.fetch_page, listy)
        for soup in soups:
            if soup is not None:
                try:
                    artwork = soup.find('div', class_="catalog")
                    artwork = artwork.find_all('figure')
                    try:
                        for art in artwork:
                            # If listing is sold, don't pick it up.
                            try:
                                sold = art.find('p', class_='price soldout sold').text
                                sold = True
                            except AttributeError:
                                sold = False

                            url = art.a['href']
                            if 'oeuvres-d-art-contemporain' in url:
                                url = re.sub('oeuvres-d-art-contemporain', 'contemporary-artworks', url)
                            if url not in self.artwork_listing and not sold:
                                la = str(url).split('/')
                                if 'painting' in la or 'sculpture' in la:
                                    self.artwork_listing.append(url)

                    except AttributeError:
                        pass
                except AttributeError:
                    pass

        # Clearing artist listings
        listy.clear()
        self.artist_listing.clear()

    # seller_info :: Caller : get_art_data_core
    # Writes seller info to the db and returns seller_id
    def seller_info(self, soup):

        seller_bundle =[]
        # Seller name
        # Seller's website
        # Seller's location
        # Return seller_id, seller_bundle
        # Write data to table seller's in db.
        try:
            A = soup.find('div', id = 'top-seller')
            B = A.find('a')
            seller_name = str(B.text).strip()
            location = str(A.find('p', class_='subtitle')).strip()
            # if seller and location are already recorded in the global seller variable, we fetch the seller_id and
            # return it .
            seller_name = "_".join([seller_name, location])
            if seller_name in SELLER_INFO.keys():
                seller_id = SELLER_INFO(seller_name)
                print(f"We have a seller for seller id {seller_id}, named {seller_name}")
                return seller_id, None
            link = B['href']
            if 'galeries-d-art' in str(link):
                link = re.sub('galeries-d-art', 'art-galleries', link)

        except AttributeError:
            link = None
        except TypeError:
            link = None
        if link is not None:
            # Moving to seller page now.!!
            # Read the name and location before moving to the next page.
            soup = TheMiner.fetch_page(link)
            # visited.discard(link)
            if soup is not None:
                try:
                    A = soup.find('div', id = 'top-seller')
                    seller_name = A.h1.text.strip()
                    # print(seller_name)
                except AttributeError:
                    return 1, seller_bundle
                try:
                    location = A.find('p', class_="subtitle").text.strip()
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

                seller_bundle.append(seller_name)
                seller_bundle.append(location)
                seller_bundle.append(website)
                return 0, seller_bundle

        return 1, seller_bundle

    def get_art_data_core(self, url):
        platform = self.website.platform
        artist_name = None
        artwork_title = None
        year = None
        price = None
        Dimensions = None
        Medium = None
        Type = None
        Support = None
        Frame = None
        Signature = None
        Authenticity = None
        About = None
        image_addr = None
        seller_id = None

        soup = TheMiner.fetch_page(url)
        if soup is not None:
            # Data to be picked here.
            # Artist's name, artwork's name, year, Artwork description, Price, Dimensions, Medium(Sculpture/Painting)
            # Type (Copies or Unique), Frame, Support, Authenticity, Website, Image (12)

            seller_id_trigger, seller_bundle = self.seller_info(soup)
            # Seller_id_trigger could be 0, 1 or a real id.(real id comes with bundle =None)
            # seller_id_trigger 0 comes with some data in bundle
            # seller_id 1_trigger comes with no data in the bundle
            if seller_bundle is None:
                seller_id = seller_id_trigger

            # THIS FOLLOW BLOCK OF CODE NEEDS TO BE CONSISTENT ACROSS ALL THE WEBSITE MODULES.
            # Get seller bundle
            elif seller_id_trigger == 0:
                seller_ds = SellerData(*seller_bundle)
                s_bundle = seller_ds.seller_bundle()
                # Write data to table "sellers"
                s_agent = db.Sellers()
                s_agent.create_table_sellers()
                seller_id = s_agent.insert_data_sellers(*s_bundle)
                # Writing the seller_info for quick use and reduce the number of clicks
                seller_name = seller_bundle[0]
                location = seller_bundle[1]
                SELLER_INFO["_".join([seller_name, location])] = seller_id

            else:
                seller_id = seller_id_trigger

            try:
                A = soup.find('section', id='informations')
                B = A.find('div', class_='relative')

                try:
                    ## ARTIST'S NAME
                    artist_name = B.find('span', class_='primary-title').text.strip()
                    # print(artist_name)
                except:
                    artist_name = None
                try:
                    ## ARTWORK'S NAME
                    C = B.find('span', class_='secondary-title').text.strip()
                    artwork_ = C.split(',')
                    artwork_title = ""
                    for a in range(len(artwork_)-1):
                        if a == 0:
                            artwork_title = artwork_[a]
                            continue
                        artwork_title = artwork_title + ", " + artwork_[a].strip()
                    # print(artwork_title)

                    # ARTWORK YEAR
                    year = C.split(',')[-1].strip()
                    # print(year)
                except:
                    artwork_title = None
                    year = None
                try:
                    # PRICE
                    price = A.find('p', class_='media-price price').text.strip()
                    number = ''
                    for p in price:
                        if p == '-':
                            break
                        if p.isdigit():
                            number += str(p)
                    price = int(number)
                    # print(price)
                except:
                    price = None

                try:
                    # Image url
                    B = A.find('div', id='img-container')
                    image_addr = B.find('img', id='img_original')['data-src']
                    # print(image_addr)
                except:
                    image_addr = None
            except:
                artist_name = None
                artwork_title = None
                year = None
                price = None
                image_addr = None

            try:
                D = soup.find('div', id='tabs-description').ul
                # Contains:: image, dimensions, medium, type, Frame, Support, authenticity, signature
                E = D.find_all('li')
                Dimensions = None
                Medium = None
                Type = None
                Support = None
                Frame = None
                Signature = None
                Authenticity = None
                About = None

                for e in E:
                    a = e.text
                    # Dimensions
                    if 'Dimensions' in a and 'About the artwork' not in a and 'Support' not in a:
                        Dimensions = e.find('p', class_='pull-right').strong.text.strip() + ' (Height x Width x Depth)'
                        dim = True
                        # print(Dimensions)
                        continue

                    # Medium (Sculpture/Painting)
                    if 'Medium' in a and 'About the artwork' not in a:
                        Medium = e.find('p', class_='pull-right').a.text.strip()
                        # print(Medium)
                        continue

                    # Type
                    if 'Type' in a and 'About the artwork' not in a:
                        Type = e.find('p', class_='pull-right text-right').text.strip().split('  ')[0]
                        # print(Type)
                        continue

                    # Support (base)
                    if 'Support' in a and 'About the artwork' not in a:
                        try:
                            f = e.find('p', class_='pull-right text-right').text.strip().split('  ')
                            Support = f[0] + '. ' + f[1].strip('\n')
                            f = e.find('p', class_='pull-right text-right').strong.text.strip().strip('\n')
                            Support += f
                        except IndexError:
                            Support = e.find('p', class_='pull-right text-right').text.strip()
                        # print(Support)
                        continue

                    # Framing
                    if 'Framing' in a and 'About the artwork' not in a:
                        Frame = e.find('p', class_='pull-right').text.strip()
                        # print(Frame)
                        continue

                    # Signature
                    if 'Signature' in a and 'About the artwork' not in a:
                        Signature = e.find('p', class_='pull-right').text.strip()
                        # print(Signature)
                        continue

                    # Authenticity
                    if 'Authenticity' in a and 'About the artwork' not in a:
                        Authenticity = e.find('p', class_='pull-right text-right').text.strip()
                        # print(Authenticity)
                        continue

                    # Artwork Description
                    if 'About the artwork' in a:
                        About = e.find('p', class_="marg-bot-10")
                        if About is not None:
                            a = e.find('div', class_="description-catalog see-more text-justify").text.strip()
                            About = About.text.strip()
                            About += a
                        else:
                            About = e.find('p', class_='').text.strip()
                        continue
                        # print(About)
            except:
                # Make all the fields Null
                Dimensions = None
                Medium = None
                Type = None
                Support = None
                Frame = None
                Signature = None
                Authenticity = None
                About = None

            result = {"artwork_title": artwork_title, "artist_name": artist_name,  "year": year, "price": price,
                      "Dimensions": Dimensions, "Medium": Medium, "Type": Type, "Support": Support, "Frame": Frame,
                      "Signature": Signature, "Authenticity": Authenticity, "About": About, 'platform': platform,
                      "image_addr": image_addr, "seller_id": seller_id}

            artwork_item = ArtworkData(**result)
            # Downloading images will be done at the end, after every 100, or so instances, we'll write the
            # data from image pool to a db [ image_url and artwork_id ]
            # And download the entire pool of images at the end of the execution.
            # The function for downlaoding the images will have to pick a set of 100 images, the function
            # is with TheMiner in module dataStructures. That function is called by ArtworksData (in datastructures)
            # DON'T THREAD ANYTHING WITH DATA DOWNLOAD FUNCTION AS IT ITSELF IS LAUNCHED ON THREAD (STUPID).
            art_bund = artwork_item.artwork_bundle()

            # WRITING ARTWORK
            dbartwork_agent = db.Artwork()
            dbartwork_agent.create_table_artwork()
            artwork_id = dbartwork_agent.insert_data_artwork(*art_bund)

            # Writing image-info
            # image_addr = result[13]
            image_bundle = artwork_item.image_bundle(artwork_id)
            dbimage_agent = db.Images()
            dbimage_agent.create_table_images()
            # dbimage_agent.insert_data_images(image_addr, artwork_id)
            dbimage_agent.insert_data_images(*image_bundle)

            # Price bundle can only be created once the artwork is written in the db
            price_bund = artwork_item.price_bundle(artwork_id)

            # WRITING PRICES
            dbprice_agent = db.Price()
            dbprice_agent.create_table_prices()
            dbprice_agent.insert_data_prices(*price_bund)

            # return result

    def get_art_data_shell(self):

        # Pick chunks of 2000  artwork listings and run in a loop until its empty.
        while len(self.artwork_listing) > 0:
            sir_temporary_list = []
            for i in range(10000):
                if len(self.artwork_listing) == 0:
                    break
                sir_temporary_list.append(self.artwork_listing.pop())

            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = executor.map(self.get_art_data_core, sir_temporary_list)

            for result in results:

                print("Writing an instance to db")

    def artsper_mine(self):

        self.get_listing_pages(self.website.start_url)
        # get_listing_pages simply fetches the url of all the pages that are to be added to self.listing_pages

        self.get_artists()
        # Get artists fetches the links for the artists, and appends them to self.artist_listing
        # Deletes self.listing_pages
        print(len(self.artist_listing))

        # self.get_artist_data()
        # Don't have to call it here. It is being called internally by the self.get_artworks function.
        # Fetches the data of the artists and stores them in db.

        self.get_artworks()
        # Fetches the listings for all the artworks and makes a list self.artwork_listing
        # Deletes self.artist_listing
        print(len(self.artwork_listing))

        self.get_art_data_shell()





def main():
    # art_page_url = 'https://www.artsper.com/us/contemporary-artworks/painting/1147236/les-deux-freres'
    art_page_url = "https://www.artsper.com/in/contemporary-artworks/painting/189196/candy-zinzin-de-lespace"
    artsperpainters = Website('https://www.artsper.com',
                              'https://www.artsper.com/us/contemporary-artists/youngtalents/painters?',
                              "ARTSPER")

    a = Artsper(artsperpainters)
    # print(a.get_art_data_core(art_page_url))
    a.seller_info(TheMiner.fetch_page(art_page_url))

if __name__ == "__main__":
    main()