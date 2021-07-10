# import mysql.connector
import pymysql
from packets.global_vars import SELLER_INFO, ARTIST_INFO
import time


def connection(caller):
    mydb = pymysql.connect(
        host="localhost",
        user="root",
        passwd="4074",
    )

    my_cursor = mydb.cursor()

    my_cursor.execute("CREATE DATABASE IF NOT EXISTS Artwork_Comparator")
    my_cursor.execute("USE Artwork_Comparator")
    print(f"CLASS: {caller} connecting to database...")
    return mydb, my_cursor


def drop_tables():
    mydb, my_cursor = connection("Drop tables")
    my_cursor.execute("DROP TABLE artworks")
    my_cursor.execute("DROP TABLE prices")
    my_cursor.execute("DROP TABLE artists")
    my_cursor.execute("DROP TABLE images")
    my_cursor.execute("DROP TABLE sellers")

    # ---------------------------
    # MySQl datatypes : https://www.w3schools.com/sql/sql_datatypes.asp

    # Closing the connection
    mydb.close()


# drop_tables()

def close_connection(mydb):
    SELLER_INFO.clear()
    mydb.close()


# _______________________________________________________________
# _______________________CLASS ARTWORK_____________________________
class Artwork:
    def __init__(self):
        mydb, my_cursor = connection("Artwork")
        self.mydb = mydb
        self.my_cursor = my_cursor

    def __del__(self):
        print("CLASS:: Artwork, disconnecting from database...")
        self.mydb.close()

    def remove_duplicates(self, artwork_id):
        # Removing duplicates from artwork and prices tables.
        delete_query = """DELETE FROM artworks WHERE ARTWORK_ID = %s"""
        self.my_cursor.execute(delete_query, artwork_id)
        self.mydb.commit()

        # Prices can not have artwork_id as duplicate, as it is PRIMARY KEY
        # delete_query = """DELETE FROM prices WHERE ARTWORK_ID = %s"""
        # self.my_cursor.execute(delete_query, artwork_id)

    def type_test(self, *args):
        values = [*args]
        print("TYPETEST")
        # print(values)
        #
        if type(values[12]) is tuple:
            values[12] = values[12][0]
        if not str(values[2]).isnumeric():
            values[2] = None
        return values

    def create_table_artwork(self):
        self.my_cursor.execute("""CREATE TABLE IF NOT EXISTS artworks (
            
            ARTWORK_TITLE VARCHAR(255),
            ARTIST VARCHAR(255),
            YEAR YEAR,
            MEDIUM VARCHAR(255),
            TECHNIQUE VARCHAR(255),
            TYPE VARCHAR(255),
            DIMENSION VARCHAR(255),
            SUPPORT VARCHAR(255),
            FRAME VARCHAR(255),
            SIGNATURE VARCHAR(255),
            AUTHENTICITY VARCHAR(255),
            ABOUT TEXT,
            IMAGE_LOC VARCHAR(255),
            
            ARTIST_ID INTEGER,
            ARTWORK_ID INTEGER AUTO_INCREMENT PRIMARY KEY)""")
        # 14 entries including ARTWORK_ID
        # Seller id removed .
        # Artist_id new index = 12.

    def insert_data_artwork(self, *args):
        # Returns boolean. True if dim do not match (conclusively). False otherwise.
        def dim(args_, db):
            if args_ is None or db is None:
                # Inconclusive. (Can't eliminate)
                return False

            ar = ""
            for a in args_:
                if str(a).isdigit():
                    ar += a

            d = ""
            for a in db:
                if str(a).isdigit():
                    d += a
            if str(ar).strip().upper() == str(d).strip().upper():
                # Dimension matches. (Can't eliminate.)
                print("Dimensions are a match")
                return False
            return True

        # Returns boolean.
        def med(args_, db):
            if args_ is None or db is None:
                # Inconclusive.
                return False

            if "Painting" in args_ or "painting" in args_:
                args_ = "PAINTING"
            elif "Sculpture" in args_ or "sculpture" in args_:
                args_ = "SCULPTURE"

            if "Painting" in db or "painting" in db:
                db = "PAINTING"
            elif "Sculpture" in db or "sculpture" in db:
                db = "SCULPTURE"

            if str(args_).strip().upper() == str(db).strip().upper():
                print("Medium are a match")
                # Medium matches, can't eliminate
                return False

            # Medium does not match. (conclusively)
            return True

        # Returns boolean.
        def frame(args_, db):
            if args_ is None or db is None:
                # Inconclusive.
                return False
            if str(args_).strip().upper() == str(db).strip().upper():
                # frames match, can't eliminate
                return False
            return True

        # Returns boolean.
        def support(args_, db):
            if args_ is None or db is None:
                # Inconclusive.
                return False
            if str(args_).strip().upper() == str(db).strip().upper():
                # supports match, can't eliminate
                return False
            return True

        # Returns boolean.
        def technique(args_, db):
            if args_ is None or db is None:
                # Inconclusive.
                return False
            if str(args_).strip().upper() == str(db).strip().upper():
                # techniques match, can't eliminate
                return False
            return True

        # Returns boolean.
        def year(args_, db):
            if args_ is None or db is None:
                # Inconclusive.
                return False
            if str(args_).strip().upper() == str(db).strip().upper():
                # years match, can't eliminate
                return False
            return True

        # Returns boolean.
        def artist_id(args_, db):
            if args_ is None or db is None:
                # Inconclusive.
                return False
            if int(args_) == int(db):
                # countries match, can't eliminate
                return False
            return True

        # This function writes "None" for IMAGE_LOC coloumn.
        # data for IMAGE_LOC is not generated yet.
        values = [*args]
        # Args are coming from whatever function is trying to write it, via dataStructure.Artworks
        # args = Artwork_Title(0), Artist(1), Year(2), Medium (3), technique(4), Type(5), Dimension(6), Support(7)
        # Frame(8), Signature(9), Authenticity(10), About(11), Image_loc(12), Artist_id(13)

        # Seller_id (12) removed

        values = self.type_test(*values)  # *values unbundles the data, so that it goes as multiple parameters and not
        # a single parameter like

        insert_query = """INSERT INTO artworks(
                 ARTWORK_TITLE, ARTIST, YEAR, MEDIUM, TECHNIQUE, TYPE, DIMENSION, SUPPORT, FRAME, SIGNATURE,
                  AUTHENTICITY, ABOUT, IMAGE_LOC, ARTIST_ID )
                 VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                 """

        self.my_cursor.execute("""SELECT * FROM artworks
        WHERE ARTWORK_TITLE = %s AND ARTIST = %s""", [str(values[0]), str(values[1])])

        results = list(self.my_cursor.fetchall())
        # We pick all the artworks in the db that have the same artwork_tile and artist's name

        if len(results) > 0:
            # for
            for result in results:
                try:
                    # If "year" not same OR "artist_id" not same, OR "dimension" not same OR "medium" not same, OR
                    # "Frame not same OR "Support" not same , OR "Techique" not same :: We remove result from results.
                    if year(values[2], result[2]) or artist_id(values[13], result[13]) or dim(values[6], result[6]) or \
                            med(values[3], result[3]) or frame(values[8], result[8]) or support(values[7], result[7])\
                            or technique(values[4], result[4]):
                        results.remove(result)

                except IndexError:
                    print("INDEX ERROR OCCURRED : FIX THE INDEX FOR ARTWORK COMPARISONS")
                    print(results)
                    time.sleep(5)
                # except AttributeError:
                #     print("INDEX ERROR OCCURRED")
                #     print(results)
                #     time.sleep(5)

        if len(results) == 0:
            self.my_cursor.execute(insert_query, values)
            self.mydb.commit()

            self.my_cursor.execute("SELECT LAST_INSERT_ID()")
            artwork_id = self.my_cursor.fetchone()
            print(f"ARTWORK ENTRY MADE :: Artwork id = {artwork_id}")
            return artwork_id[0]

        elif len(results) == 1:
            print("ARTWORK ENTRY EXISTS :: ", end="")
            # print(results)
            # Return artwork_id
            artwork_id = results[0][14]
            # print(results)
            print(f"Artwork id = {artwork_id}")

            return artwork_id
        else:
            print("DUPLICATE ENTRIES FOUND. RESOLVING CONFLICT. REMOVING DUPLICATE ENTRIES :: ", end="")
            print(results)
            print(len(results))
            while len(results) > 1:
                result = results.pop(-1)
                artwork_id = result[14]
                self.remove_duplicates(artwork_id)
            # time.sleep(10)
            artwork_id = results[0][14]
            # print(results)
            print(f"Artwork id = {artwork_id}")
            return artwork_id


# _______________________________________________________________
# _______________________CLASS PRICE_____________________________
class Price:

    # TO be called by sir_image_manager in TheMiner.
    def update_image(self, *args):
        values = [*args]
        # args = path, artwork_id
        print(f"Updating IMAGE_LOC in prices")

        update_query = """UPDATE prices
                             SET IMAGE_LOC = %s 
                             WHERE URL = %s
                             """
        self.my_cursor.execute(update_query, [str(values[0]), str(values[1])])
        self.mydb.commit()

    def __init__(self):
        mydb, my_cursor = connection("Price")
        self.mydb = mydb
        self.my_cursor = my_cursor

    def __del__(self):
        print("CLASS:: Price, disconnecting from database...")
        self.mydb.close()

    def create_table_prices(self):
        self.my_cursor.execute("""CREATE TABLE IF NOT EXISTS prices(
            ARTWORK_ID INTEGER, 
            PLATFORM VARCHAR(255),
            SELLER_ID INTEGER,
            PRICE FLOAT(10,2),
            URL VARCHAR(255) PRIMARY KEY,
            IMAGE_LOC VARCHAR(255)
            )""")

        # Total 6 coloumns including the primary key.

    def insert_data_prices(self, *args):
        values = [*args]
        # Values = [artwork_id, platform, seller_id, price, url ]

        # We are assuming that only one website's data will be updated at a time

        insert_query = """INSERT INTO prices(
                    ARTWORK_ID, PLATFORM, SELLER_ID, PRICE, URL)
                         VALUES(%s, %s, %s, %s, %s)
                         """
        update_query = """UPDATE prices
                                 SET PRICE = %s 
                                 WHERE URL = %s
                                 """
        update_bundle = [values[3], values[4]]

        # THIS IS HOW YOU CHANGE THE QUERY STRING DYNAMICALLY.
        # if up_col_p != 100:
        #     up_col_p = col_names[up_col_p]
        # if up_col_s != 'GAGAN':
        #     up_val_s = col_names[up_val_s]
        #
        # if up_col_p != 100 and up_col_s != 'GAGAN':
        #     update_query = f"""UPDATE prices
        #                     SET {up_col} = %s WHERE ARTWORK_ID = %s"""

        # Checking if there is already is an entry
        self.my_cursor.execute("""SELECT * FROM prices
                                WHERE URL = %s""", [str(values[4]).strip()])
        results = list(self.my_cursor.fetchall())

        # If there is no entry for that url
        if len(results) == 0:
            # print(f"Inside the writing block in insert_price_data {results}")
            try:
                self.my_cursor.execute(insert_query, values)
                self.mydb.commit()
            except pymysql.err.IntegrityError:
                # Error is thrown because URL is supposed to be unique.
                # Also this should never occur because we eliminate duplicate product urls by using
                # visited global variable.
                print("FATAL ERROR: Same page being scanned twice, for artwork description.")
        else:
            print("PRICE ENTRY EXISTS. Updating price...")
            self.my_cursor.execute(update_query, update_bundle)
            self.mydb.commit()
            # It means that the particular url for which we are trying to enter the data, already exists.
            # In this case, we must update the price, and not skip it.


# _______________________________________________________________
# _______________________CLASS ARTIST_____________________________

class Artist:
    def __init__(self):
        mydb, my_cursor = connection("Artist")
        self.mydb = mydb
        self.my_cursor = my_cursor

    def __del__(self):
        print("CLASS:: Artist, disconnecting from database...")
        self.mydb.close()

    # Makes a key for ARTIST_INFO dict.
    @staticmethod
    def key_maker(values):
        # key = name_born_COUNTRY
        key = "_".join([str(values[0]).strip(), str(values[1]).strip(), str(values[2]).strip().upper()])
        return key

    def remove_duplicates(self, artist_id):
        delete_query = """DELETE FROM artists WHERE ARTIST_ID = %s"""
        print(f"REMOVING : {artist_id}")
        self.my_cursor.execute(delete_query, artist_id)
        self.mydb.commit()
        print(f"REMOVED : {artist_id}")

    def create_table_artist(self):

        self.my_cursor.execute("""CREATE TABLE IF NOT EXISTS artists(
            NAME VARCHAR(255),
            BORN INTEGER,
            COUNTRY VARCHAR(255),
            ABOUT TEXT,
            ARTIST_ID INTEGER AUTO_INCREMENT PRIMARY KEY
            )""")
        # Total 6 coloumns including the primary key, which will go to artworks table

    def insert_data_artists(self, *args):

        # True returned by either(any) of these comparison functions, eliminates the entry.

        # Returns boolean. True if born does not match (conclusively). False otherwise.
        def born_comp(args_born, db_born):
            if args_born is None or db_born is None:
                # Inconclusive. (Can't eliminate)
                return False
            if str(args_born).strip().upper() == str(db_born).strip().upper():
                # Born matches. (Can't eliminate.)
                return False
            return True

        # Returns boolean.
        def country_comp(args_country, db_country):
            if args_country is None or db_country is None:
                # Inconclusive.
                return False
            if str(args_country).strip().upper() == str(db_country).strip().upper():
                # countries match, can't eliminate
                return False
            return True

        values = [*args]
        # args = name, born, country, about
        # Artist and Artwork are similar in respect that they are both consistent across websites, ie, the data is
        # not site specific.

        # We write look for all the entries with "name".
        # Then we filter out, if the entry and args have the same born field and country then we remove those entries.
        # Make a provision for born == "None", ie, escape it. If values[born] == None, then we don't check further.
        # (implement the same for artworks, check for all the fields together and not one by one.
        insert_query = """INSERT INTO artists(
                                 NAME, BORN, COUNTRY, ABOUT
                                  )
                                 VALUES(%s, %s, %s, %s)
                                 """

        self.my_cursor.execute("""SELECT * FROM artists
                WHERE NAME = %s""", [values[0]])
        # Check if the entry already exists. We fetch all entries with this name. Thereafter we eliminate
        results = list(self.my_cursor.fetchall())

        if len(results) > 0:
            for result in results:
                # if born not same OR country not same, eliminate the entry
                if born_comp(values[1], result[1]) or country_comp(values[2], result[2]):
                    results.remove(result)

        if len(results) == 0:
            try:
                self.my_cursor.execute(insert_query, values)
                self.mydb.commit()
                self.my_cursor.execute("""SELECT LAST_INSERT_ID()""")
                artist_id = self.my_cursor.fetchone()

                # Updating ARTIST_INFO, since a new entry has been made.
                ARTIST_INFO[Artist.key_maker(values)] = int(artist_id[0])

                # No need to return the artist_id
                # return artist_id
            except pymysql.err.IntegrityError:
                # Trying to make duplicate entries.
                print("ARTIST ENTRY EXISTS")
                self.my_cursor.execute("""SELECT * FROM artists
                                WHERE LINK = %s""", [values[0]])
                results = list(self.my_cursor.fetchall())
                if Artist.key_maker(values) not in ARTIST_INFO.keys():
                    ARTIST_INFO[Artist.key_maker(values)] = int(results[0][4])

        elif len(results) == 1:
            print("ARTIST ENTRY EXISTS")
            if values[0] not in ARTIST_INFO.keys():
                ARTIST_INFO[Artist.key_maker(values)] = int(results[0][4])
            # Return artist_id
            # return results[0][4]

        else:
            print("DUPLICATION ERROR :: Multiple Artist entries for the same name, age and location")
            print("REMOVING DUPLICATE ENTRIES.")
            while len(results) > 1:
                result = results[-1]
                self.remove_duplicates(result[4])

    def read_artist_data(self):
        self.create_table_artist()
        self.my_cursor.execute("""SELECT * FROM artists""")
        artists = list(self.my_cursor.fetchall())
        ARTIST_INFO.clear()
        # We are not saving the artist_url in db so we can not initiate the KEY_INFO here.
        # KEY_INFO will get initiated when TheAuthor tries to write the data.
        # Purpose of KEY_INFO is to map the url for the artist to a key, that key in turn is stored with ARTIST_INFO
        # ARTIST_INFO stores the artist_id against the said 'key'. (key is generated by db->Artist->key_maker() )
        for artist in artists:
            key = Artist.key_maker(artist)
            artist_id = artist[4]
            ARTIST_INFO[key] = int(artist_id)


# _______________________________________________________________
# _______________________CLASS SELLER_____________________________
class Sellers:
    def __init__(self):
        mydb, my_cursor = connection("Sellers")
        self.mydb = mydb
        self.my_cursor = my_cursor

    def __del__(self):
        print("CLASS:: Sellers, disconnecting from database...")
        self.mydb.close()

    def create_table_sellers(self):

        self.my_cursor.execute("""CREATE TABLE IF NOT EXISTS sellers(
            URL VARCHAR(255) PRIMARY KEY,
            PLATFORM_ID VARCHAR(255),
            SELLER VARCHAR(255),
            LOCATION VARCHAR(255),
            WEBSITE VARCHAR(255),
            SELLER_ID INTEGER UNIQUE AUTO_INCREMENT
            )""")
        # Total 5 coloumns including the primary key, which will go to prices

    def insert_data_sellers(self, *args):
        # Return seller_id
        values = [*args]
        # args = url, platform_id, seller, location, website

        insert_query = """INSERT INTO sellers(
                                 URL, PLATFORM_ID, SELLER, LOCATION, WEBSITE
                                  )
                                 VALUES(%s, %s, %s, %s, %s)
                                 """

        self.my_cursor.execute("""SELECT * FROM sellers
                WHERE URL = %s""", [values[0]])
        results = list(self.my_cursor.fetchall())

        if len(results) == 0:
            try:
                self.my_cursor.execute(insert_query, values)
                self.mydb.commit()
                self.my_cursor.execute("""SELECT LAST_INSERT_ID()""")
                seller_id = self.my_cursor.fetchone()
                SELLER_INFO[values[0]] = int(seller_id[0])

            except pymysql.err.IntegrityError:
                print("SELLER ENTRY EXISTS")
                # We don't update SELLER_INFO here. Instead we slow this thread down so that the other thread has
                # time to write the entry.
                time.sleep(1)
                # Fetch the seller entry again.
                self.my_cursor.execute("""SELECT * FROM sellers WHERE URL = %s""", [values[0]])
                results = list(self.my_cursor.fetchall())
                print(values)
                print(results)
                if values[0] not in SELLER_INFO.keys():
                    print(values)
                    print(results)
                    SELLER_INFO[values[0]] = int(results[0][5])

        elif len(results) == 1:
            print("SELLER ENTRY EXISTS")
            if values[0] not in SELLER_INFO.keys():
                SELLER_INFO[values[0]] = int(results[0][5])
            # return results[0][4]
        else:
            print("SIR THE MATRIX HAS GLITCHED . MULTIPLE SELLER ENTRIES FOR A SINGLE URL ARE HERE.")
            # We don't update SELLER_INFO . The code shouldn't come here. If it does, it'll fail.

    def read_data_sellers(self):
        self.create_table_sellers()
        self.my_cursor.execute("""SELECT * FROM sellers""")
        sellers = self.my_cursor.fetchall()
        SELLER_INFO.clear()
        for seller in sellers:
            url = seller[0]
            seller_id = seller[5]
            SELLER_INFO[url] = int(seller_id)


# _______________________________________________________________
# _______________________CLASS IMAGE_____________________________
class Images:
    def __init__(self):
        mydb, my_cursor = connection("Images")
        self.mydb = mydb
        self.my_cursor = my_cursor

    def __del__(self):
        print("CLASS:: Images, disconnecting from database...")
        self.mydb.close()

    def create_table_images(self):

        self.my_cursor.execute("""CREATE TABLE IF NOT EXISTS images(
            IMAGE_URL VARCHAR(255),
            URL VARCHAR(255) PRIMARY KEY,
            PATH VARCHAR(255)
            )""")
        # Total 3 coloumns

    def insert_data_images(self, *args):
        values = [*args]
        # args = image_url, page_url, path

        insert_query = """INSERT INTO images(
                                 IMAGE_URL, URL, PATH
                                  )
                                 VALUES(%s, %s, %s)
                                 """

        self.my_cursor.execute("""SELECT * FROM images
                        WHERE URL = %s""", [str(values[1])])

        # If page_url already exists, we do not download a new image. Hence we don't make a new entry here.
        results = list(self.my_cursor.fetchall())

        if len(results) == 0:
            try:
                # print(values)
                self.my_cursor.execute(insert_query, values)
                self.mydb.commit()
            except pymysql.err.IntegrityError:
                print("IMAGE ENTRY EXISTS")
        elif len(results) == 1:
            print("IMAGE ENTRY EXISTS")
        else:
            print("SIR THE IMAGES TABLE IS BROKEN")
            # The code should never reach here

    def read_image_data(self):
        self.my_cursor.execute("""SELECT * FROM images""")
        results = list(self.my_cursor.fetchall())
        res = []
        for result in results:
            # Returning a list of tuple (page_url, url, path)
            res.append((str(result[1]), str(result[0]).strip(), str(result[2]).strip()))
        #
        return res

        # yielding a tuple of artwork_id and image_url.
        # This tuple will be used by TheMiner to 1. Generate file location, and 2. Download the images
        # TheMiner will return a bundle with artwork_id and file location( as image_loc)
        # The bundle will be passed to Artwork.update_image , which use it to update it in its dB
        # This entire work should be contained in a function somewhere, outside artsper.py

        # That function will, call this function, take this tuple, unpack it 100 at a time.
        # Then start a 100 threads
        # call TheMiner with these values and then gather file location ( as image_loc or path) from TheMiner
        # bundle artwork_id and image_loc together and call Artwork.update_image with these values.

        # This function is to be placed with TheMiner.
        # Who'll call it?.


def create_tables():
    agent = Sellers()
    agent.create_table_sellers()

    agent = Artist()
    agent.create_table_artist()

    agent = Artwork()
    agent.create_table_artwork()

    agent = Price()
    agent.create_table_prices()

    agent = Images()
    agent.create_table_images()


create_tables()


def main():
    pass
    # art = Artwork()
    #
    # data = ['Bad_dreams', 'Gopi', 2019, 'Painting', 'Unique Work', "20*20*20 cm", None, None, 'Signed by Artist',
    #         'Certificate from artsper', 'What a work', 'Somewhere']
    # artwork_id = art.insert_data_artwork(*data)
    #
    # data = ['Baddest_dreams', 'Gopi', 2021, 'Painting', 'Unique Work', "20*20*10 cm", None, None, 'Signed by Artist',
    #         'Certificate from artsper', 'What a work', 'Somewhere']
    # artwork_id = art.insert_data_artwork(*data)
    #
    # p_bundle = [artwork_id, 6477.76, None, None, None, None, None, None]
    #
    # price = Price()
    # price.create_table_prices()
    # price.insert_data_prices(*p_bundle)
    #
    # a_bundle = ['Ramesh', 1995, "India", "Awesome dude"]
    # artist = Artist()
    # artist.create_table_artist()
    # artist_id = artist.insert_data_artists(*a_bundle)

    # drop_tables()
    # close_connection()


if __name__ == "__main__":
    main()
