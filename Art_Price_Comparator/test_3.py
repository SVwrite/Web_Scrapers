from packets.TheMiner import TheMiner
import concurrent.futures
from packets.global_vars import visited

self_artist_listings = []
self_listy = []
self_website_domain = 'https://www.singulart.com'
self_artwork_listings = []


def self_link_maker(link):
    return self_website_domain+link

def get_artist_listings(url):

    def recurr(url):
        soup = TheMiner.fetch_page(url, ghost=True)
        if soup is not None:
            # Because singulart keeps blocking ips, we'll ship everything inside try-except statements.
            try:
                # artist_blocks = soup.find_all('div', class_='artist-container')
                artist_blocks = soup.find_all('figure', class_='pic-artist')
                print(len(artist_blocks))
                for artist in artist_blocks:
                    link = artist.figcaption.h2.a.get('href')
                    if "https://www.singulart.com" not in link:
                        link = 'https://www.singulart.com'+link
                    self_artist_listings.append(link)
                # print(self_artist_listings)


                # next pages
                next_pages = soup.find('div', class_='pagerfanta').find('nav')
                next_pages = next_pages.find_all('a')
                for next_ in next_pages:
                    link = next_.get('href')
                    if "https://www.singulart.com" not in link:
                        link = 'https://www.singulart.com' + link
                    if link not in listy:
                        listy.append(link)

                # print(listy)
                print(len(listy))

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    trig = executor.map(recurr, listy)
                for trigger in trig:
                    pass
            except AttributeError:
                visited.discard(url)
                pass

    while len(listy) == 0 and len(self_artist_listings) == 0:
        recurr(url)

    while len(listy) <= 50 and len(self_artist_listings) <= 1000:
        result = map(recurr, listy)
        for resul in result:
            pass


# get_artist_listings('https://www.singulart.com/en/painting?count=60')
# print(len(self_artist_listings))
# print(len(listy))

def get_artwork_listing_slave(url):
    soup = TheMiner.fetch_page(url, ghost=True)
    # Artist's info and artwork listings are available on the same page.
    if soup is not None:
        try:
            block = soup.find_all('div', class_='artist-container artist-container--details')
            if len(block) == 0:
                # Crash agent causes Attribute error.
                crash_agent = block.find_all('a')
            print(f"BLOCK : {len(block)}")
            try:
                for chunk in block:
                    items = chunk.find_all('figure', class_='artwork-item artwork-item--details')
                    print(f"ITEMS : {len(items)}")

                    for piece in items:
                        paise = piece.find('div', class_='meta').text.strip()
                        # print(paise)
                        if "Sold" not in str(paise):
                            # print("B")
                            a = piece.find('a')['href']
                            if self_website_domain not in a:
                                a = self_link_maker(a)
                            if a not in self_artwork_listings:
                                self_artwork_listings.append(a)

            except AttributeError:
                # print("A")
                pass

            # self_get_artist_data()

        except AttributeError:
            print("B")
            # Urls that get blocked are discarded from visited and added to listy for a recall. (linear if listy is
            # small and multithreaded if listy is large enough till, its brought of size.
            visited.discard(url)
            self_listy.append(url)


url = 'https://www.singulart.com/en/artist/alexandre-barbera-ivanoff-3209'
get_artwork_listing_slave(url)
print(len(self_artwork_listings))
print(len(self_listy))