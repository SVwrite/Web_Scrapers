class Website:
    def __init__(self, domain, start, platform):
        self.domain = domain
        self.start_url = start
        self.platform = platform
        self.platform_id = self.platform_id_maker(platform)

    def platform_id_maker(self, platform):
        platform = str(platform).strip().upper()
        col_names = ['Null', 'ARTSPER', 'KAZOART', 'ARTSY', 'SINGULART', 'ARTMAJEUR', 'SAATCHIART',
                     'EMERGINGARTISTPLATFOM']
        return col_names.index(platform)

    def url_maker(self, url):
        return self.domain + url

    def print_website(self):
        print(self.domain)