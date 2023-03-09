import inspect
import json
import os

import requests
import socks
import socket
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

URL_ATTRACTIONS = "https://yandex.ru/maps/2/-/category/landmark_attraction"

with sync_playwright() as p:
    def connect_to_tor():
        print("Before:")
        check_ip()

        socks.set_default_proxy(socks.SOCKS5, "localhost", 9150)
        socket.socket = socks.socksocket

        print("After:")
        check_ip()


    def check_ip():
        ip = requests.get('http://checkip.dyndns.org').content
        soup = BeautifulSoup(ip, 'html.parser')
        print(soup.find('body').text)


    def get_file_dir():
        filename = inspect.getframeinfo(inspect.currentframe()).filename
        path = os.path.dirname(os.path.abspath(filename))
        return path


    def save_json_place(items):
        places_dir_path = os.path.join(get_file_dir(), "results/places")
        if not os.path.exists(places_dir_path):
            os.makedirs(places_dir_path)
        for item in items:
            file_path = os.path.join(places_dir_path, item["id"] + ".json")
            new_file = open(file_path, "w+")
            new_file.write(json.dumps(item))
            new_file.close()


    def handle_response(response):
        if "search?" in response.url:
            items = response.json()["data"]["items"]
            save_json_place(items)


    connect_to_tor()
    browser = p.chromium.launch()
    page = browser.new_page()

    page.on("response", handle_response)
    page.goto(URL_ATTRACTIONS)
    page.wait_for_selector("li[class=search-snippet-view]")

    start_items = json.loads(BeautifulSoup(page.content(), "html.parser").find("script", class_="state-view").text)["stack"][0]["results"]["items"]
    save_json_place(start_items)

    attraction_cards = None
    while True:
        attraction_cards = page.locator("li[class=search-snippet-view]")
        attraction_cards.element_handles()[-1].scroll_into_view_if_needed()
        items_on_page = len(attraction_cards.element_handles())
        attraction_cards.element_handles()[-1].hover()
        page.mouse.wheel(0, 1000)
        page.wait_for_timeout(1000)
        items_on_page_after_scroll = len(attraction_cards.element_handles())
        if items_on_page_after_scroll > items_on_page:
            continue
        else:
            break

    page.context.close()
    browser.close()
