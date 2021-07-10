import os
from packets import dbmanip as db


# from packets.global_vars import image_pool
# from packets.TheMiner import TheMiner

class TheAuthour:

    @ staticmethod
    def write_artwork_price_image(**kwargs):
        # It'll get the bundle as argumets

        #    artwork_title=None, artist_name=None, year=None, price=None, Dimensions=None, Medium=None,
        #     Type=None, Support=None, Frame=None, Signature=None, Authenticity=None, About=None,
        #      platform=None, image_addr=None, seller_id=None, artist_id=None, url =url, technique = technique)

        # Getting artwork bundle
        # Passing kwargs by unpacking them.
        artwork_ds = ArtworkDS(**kwargs)
        artwork_bundle = artwork_ds.artwork_bundle()

        artwork_write = db.Artwork()
        artwork_id = artwork_write.insert_data_artwork(*artwork_bundle)

        # Getting price bundle. Writing price data
        price_bundle = artwork_ds.price_bundle(artwork_id)
        # print(f"PRICE BUNDLE :: {price_bundle}")
        writer = db.Price()
        writer.insert_data_prices(*price_bundle)

        # Getting image bundle. Writing image data (images table)
        image_bundle = artwork_ds.image_bundle()
        writer = db.Images()
        writer.insert_data_images(*image_bundle)

    @staticmethod
    def write_seller(*args):
        # args = [url, platform, seller_name, location = None, Website ]
        # Running data through SellerData class of dataStructures.
        seller = SellerDS(*args)
        bundle = seller.seller_bundle()
        # bundle = [url, Seller_name, Location =None, Website = url]
        writer = db.Sellers()
        writer.insert_data_sellers(*bundle)
        # SELLER_INFO has been updated within insert_data_sellers() function.

    @staticmethod
    def write_artist(*args):
        # Running the data through dataStructure ArtistData
        artist = ArtistDS(*args)
        bundle = artist.artist_bundle()
        # bundle = [name, born, country, about]
        writer = db.Artist()
        # Create artist table if it doesn't already exist
        writer.create_table_artist()
        writer.insert_data_artists(*bundle)
        # ARTIST_INFO has been updated by insert_data_artists() function.


class SellerDS:
    def __init__(self, url, platform, seller, location, website):
        self.url = url
        self.platform_id = self.platform_id_maker(platform)
        self.seller = seller
        self.location = location
        self.website = website
        self.type_affirm()

    def type_affirm(self):
        if self.url is not None:
            if len(self.url) > 255:
                self.url = str(self.url)[0:255]

        if self.seller is not None:
            if len(str(self.seller)) > 255:
                self.seller = str(self.seller)[0:255]

        if self.location is not None:
            if len(str(self.location)) > 255:
                self.location = str(self.location)[0:255]

        if self.website is not None:
            if len(str(self.website)) > 255:
                self.website = str(self.website)[0:255]

    def seller_bundle(self):
        if self.url is not None:
            bundle = [self.url, self.platform_id, self.seller, self.location, self.website]
            return bundle
        else:
            print("ERROR : LINK TO SELLER'S PAGE IS NOT FOUND.")
            # The code should break here.

    def platform_id_maker(self, platform):
        platform = str(platform).strip().upper()
        col_names = ['Null', 'ARTSPER', 'KAZOART', 'ARTSY', 'SINGULART', 'ARTMAJEUR', 'SAATCHIART',
                     'EMERGINGARTISTPLATFOM']
        return col_names.index(platform)


class ArtistDS:
    def __init__(self, name, born, country, about):
        # self.url = url
        self.artist_name = name
        self.born = born
        self.country = country
        self.about = about
        self.type_affirm()

    def type_affirm(self):
        if self.artist_name is not None:
            if len(self.artist_name) > 255:
                self.artist_name = self.artist_name[0:255]

        if self.born is not None:
            if type(self.born) != int:
                try:
                    self.born = int(str(self.born))
                except ValueError:
                    self.born = None

        if self.country is not None:
            if len(self.country) > 255:
                self.country = self.country[0:255]


    def artist_bundle(self):
        if self.artist_name is not None:
            bundle = [self.artist_name, self.born, self.country, self.about]
            return bundle
        else:
            print("FATAL ERROR :: Artist's name not found.")
            # Code should break here.


class ArtworkDS:
    def __init__(self, artwork_title=None, artist_name=None, year=None, price=None, Dimensions=None, Medium=None,
                 Type=None, Support=None, Frame=None, Signature=None, Authenticity=None, About=None,
                 platform=None, image_addr=None, seller_id=None, artist_id=None, url=None, technique=None):

        self.artwork_title = artwork_title
        self.artist = artist_name
        self.year = year
        self.price = price
        self.Dimensions = Dimensions
        self.Medium = Medium
        self.technique = technique
        self.Type = Type
        self.Support = Support
        self.Frame = Frame
        self.Signature = Signature
        self.Authenticity = Authenticity
        self.About = About
        self.platform = platform
        self.platform_id = self.platform_id_maker(platform)

        self.image_loc = None
        self.seller_id = seller_id
        self.artist_id = artist_id
        self.url = url

        # for image processing
        self.image_addr = image_addr
        self.type_affirm()

    def type_affirm(self):

        if self.artwork_title is not None:
            if len(self.artwork_title) > 255:
                self.artwork_title = self.artwork_title[0:255]

        if self.artist is not None:
            if len(self.artist) > 255:
                self.artist = self.artist[0:255]

        if self.year is not None:
            if type(self.year) != int:
                try:
                    self.year = int(str(self.year))
                except ValueError:
                    self.year = None

        if self.price is not None:
            if type(self.price) != float:
                try:
                    self.price = float(str(self.price))
                except ValueError:
                    self.price = None

        if self.Dimensions is not None:
            if len(self.Dimensions) > 255:
                self.Dimensions = self.Dimensions[0:255]
        if self.Medium is not None:
            if len(self.Medium) > 255:
                self.Medium = self.Medium[0:255]

        if self.technique is not None:
            if len(self.technique) > 255:
                self.technique = self.technique[0:255]

        if self.Type is not None:
            if len(self.Type) > 255:
                self.Type = self.Type[0:255]

        if self.Support is not None:
            if len(self.Support) > 255:
                self.Support = self.Support[0:255]

        if self.Frame is not None:
            if len(self.Frame) > 255:
                self.Frame = self.Frame[0:255]

        if self.Signature is not None:
            if len(self.Signature) > 255:
                self.Signature = self.Signature[0:255]

        if self.Authenticity is not None:
            if len(self.Authenticity) > 255:
                self.Authenticity = self.Authenticity[0:255]

        if self.seller_id is not None:
            if type(self.seller_id) is not int:
                try:
                    self.seller_id = int(str(self.seller_id))
                except ValueError:
                    self.seller_id = None

        if self.artist_id is not None:
            if type(self.artist_id) is not int:
                try:
                    self.artist_id = int(str(self.artist_id))
                except ValueError:
                    self.artist_id = None

        if self.url is not None:
            if len(self.url) > 255:
                self.url = self.url[0:255]

    def platform_id_maker(self, platform):
        platform = str(platform).strip().upper()
        col_names = ['Null', 'ARTSPER', 'KAZOART', 'ARTSY', 'SINGULART', 'ARTMAJEUR', 'SAATCHIART',
                     'EMERGINGARTISTPLATFOM']
        return col_names.index(platform)

    def artwork_bundle(self):
        """ARTWORK_TITLE, ARTIST, YEAR, MEDIUM, TECHNIQUE, TYPE, DIMENSION, SUPPORT, FRAME, SIGNATURE,
         AUTHENTICITY, ABOUT, IMAGE_LOC,ARTIST_ID
        """
        # Seller_id removed from bundle

        if self.artist_id is not None:
            return [self.artwork_title, self.artist, self.year, self.Medium, self.technique, self.Type, self.Dimensions,
                    self.Support, self.Frame, self.Signature, self.Authenticity, self.About, self.image_loc,
                    self.artist_id]
        else:
            print("FATAL ERROR: ARTIST_ID MISSING.")
            print(f"ARTIST_ID = {self.artist_id}")
            # Code should break here.

    # Artwork_id is obtained after the artwork is written in the dB
    def price_bundle(self, artwork_id):
        # PRICE BUNDLE = [ artwork_id, self.platform, seller_id, self.price, self.url]
        bundle = [artwork_id, self.platform, self.seller_id, self.price, self.url]

        if artwork_id is not None and self.price is not None and self.seller_id is not None:
            return bundle
        else:
            print("FATAL ERROR: ARTWORK_ID OR, SELLER_D OR PRICE MISSING.")
            print(f"ARTWORK_ID = {artwork_id}, Price = {self.price}")
            # Code should break here.

    def image_bundle(self):
        # """IMAGE_URL, PAGE_URL, PATH"""
        # Generating filename.
        path = self.img_path_maker(self.image_addr)
        bundle = [self.image_addr, self.url, path]
        return bundle

    def img_path_maker(self, url):
        if url is None:
            return None
        MEDIA_BASE_DIR = os.path.join(os.getcwd(), 'Resources')
        MEDIA_BASE_DIR = os.path.join(MEDIA_BASE_DIR, 'MEDIA')
        # if not os.path.exists(MEDIA_BASE_DIR):
        #     os.makedirs(MEDIA_BASE_DIR)

        fn = os.path.basename(url)
        file_name = os.path.join(MEDIA_BASE_DIR, self.platform)
        if not os.path.exists(file_name):
            try:
                os.makedirs(file_name)
            except FileExistsError:
                pass
        file_name = os.path.join(file_name, fn)

        return file_name

        # # Add tuple of url and path to image_pool so that we can process it later.
        # if len(image_pool) <= 500:
        #     image_pool.append((file_name, url))
        # else:
        #     TheMiner.download_images()
        #     image_pool.clear()
        # # print(file_name)
        # return str(file_name)

# class imageData:
#     def __init__(self):
#         pass

# Takes url, returns a tuple of file_name and url
