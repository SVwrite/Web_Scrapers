import time

from packets import dbmanip as db
from packets.TheMiner import TheMiner
from packets.web.artsper import Artsper
from packets.websiteds import Website


def main():
    start = time.perf_counter()

    # Creating SELLER_INFO
    sellers = db.Sellers()
    sellers.read_data_sellers()

    # Creating ARTIST_INFO
    artists = db.Artist()
    artists.read_artist_data()


    artsperpainters = Website('https://www.artsper.com',
                              'https://www.artsper.com/us/contemporary-artists/youngtalents/painters?',
                              "ARTSPER")

    a_m = Artsper(artsperpainters)
    a_m.artsper_mine()

    finish = time.perf_counter()
    print(f"Lap Completed in {round(finish - start, 2)}, seconds.\n Starting sculptures")

    artspersculptors = Website('https://www.artsper.com',
                              'https://www.artsper.com/us/contemporary-artists/youngtalents/sculptors-artists',
                              "ARTSPER")

    a_m = Artsper(artspersculptors)
    a_m.artsper_mine()

    finish = time.perf_counter()


    print(f"Lap Completed in {round(finish - start, 2)}, seconds.\n Downloading and updating images")

    TheMiner.sir_image_manager()

    finish = time.perf_counter()
    print(f"Finished in {round(finish - start, 2)}, seconds")
    # close()


if __name__ == "__main__":
    main()
