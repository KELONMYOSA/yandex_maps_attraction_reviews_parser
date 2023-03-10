import inspect
import json
import os

import requests
import socks
import socket
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def collect_places_id(region_id, category):
    url = "https://yandex.ru/maps/" + region_id + "/-/category/" + category

    with sync_playwright() as p:
        def connect_to_tor():
            print("Connecting to Tor")
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
            items_id = list()
            for item in items:
                items_id.append(item["id"])

            places_dir_path = os.path.join(get_file_dir(), "results/places_id")
            if not os.path.exists(places_dir_path):
                os.makedirs(places_dir_path)
            file_path = os.path.join(places_dir_path, region_id + ".json")

            if not os.path.exists(file_path):
                open(file_path, "w").close()

            if os.path.getsize(file_path) > 0:
                file = open(file_path, "r")
                file_data = json.loads(file.read())
                file.close()
            else:
                file_data = dict()

            file_category_data = file_data.get(category)

            if file_category_data is None:
                file_data.update({category: items_id})
            else:
                file_category_data = list(set(file_category_data + items_id))
                file_data.update({category: file_category_data})

            file = open(file_path, "w")
            file.write(json.dumps(file_data))
            file.close()

        def handle_response(response):
            if "search?" in response.url:
                items = response.json()["data"]["items"]
                save_json_place(items)

        print("Start - (region_id: " + region_id + ", category: " + category + ")")

        connect_to_tor()
        browser = p.chromium.launch()
        page = browser.new_page()

        page.on("response", handle_response)
        page.goto(url)
        page.wait_for_selector("li[class=search-snippet-view]")

        start_items = \
        json.loads(BeautifulSoup(page.content(), "html.parser").find("script", class_="state-view").text)["stack"][0][
            "results"]["items"]
        save_json_place(start_items)

        while True:
            attraction_cards = page.locator("li[class=search-snippet-view]")
            attraction_cards.element_handles()[-1].scroll_into_view_if_needed()
            items_on_page = len(attraction_cards.element_handles())
            attraction_cards.element_handles()[-1].hover()
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(2000)
            items_on_page_after_scroll = len(attraction_cards.element_handles())
            if items_on_page_after_scroll > items_on_page:
                continue
            else:
                break

        page.context.close()
        browser.close()

        print("Finish - (region_id: " + region_id + ", category: " + category + ")")
        print("--------------------")
