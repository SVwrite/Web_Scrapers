import requests
from stem.control import Controller
from stem import Signal
import json


def ghost_sessions():

    def renew_conncetion():
        with Controller.from_port(port = 9051) as controller:
            controller.authenticate(password = "shreyansh")
            controller.signal(Signal.NEWNYM)

    def get_tor_session():
        renew_conncetion()

        session = requests.session()
        session.proxies = { 'http' : 'socks5://127.0.0.1:9050',
                            'https' : 'socks5://127.0.0.1:9050' }
        return session
        # Tor uses the 9050 port as the default socks port

    session = get_tor_session()
    r = session.get('http://httpbin.org/ip').json()
    lastip = r.get("origin")
    print(lastip)
    lastip = lastip.strip(".")

    while True:
        # renew_conncetion()

        session = get_tor_session()
        r = session.get('http://httpbin.org/ip').json()
        newip = r.get("origin")
        print(newip)
        newip = newip.strip(".")
        if newip[2] != lastip[2]:
            break
        lastip = newip
    return session

