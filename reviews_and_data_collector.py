import json
import os

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from places_id_collector import get_file_dir, connect_to_tor
from utils import execute_captcha


def collect_reviews_and_data(region_id, category):
    current_place_id = None

    def read_json_places_id():
        places_dir_path = os.path.join(get_file_dir(), "results/places_id")
        if not os.path.exists(places_dir_path):
            os.makedirs(places_dir_path)
        file_path = os.path.join(places_dir_path, region_id + ".json")

        file = open(file_path, "r")
        file_data = json.loads(file.read())
        file.close()

        return file_data.get(category)

    def save_json_place_data(item_data, item_id):
        places_dir_path = os.path.join(get_file_dir(), f"results/places_data/{region_id}")
        if not os.path.exists(places_dir_path):
            os.makedirs(places_dir_path)
        file_path = os.path.join(places_dir_path, item_id + ".json")

        file = open(file_path, "w+")
        file.write(json.dumps(item_data))
        file.close()

    def save_json_place_reviews(review_data, item_id):
        places_dir_path = os.path.join(get_file_dir(), f"results/reviews/{region_id}")
        if not os.path.exists(places_dir_path):
            os.makedirs(places_dir_path)
        file_path = os.path.join(places_dir_path, item_id + ".json")

        if not os.path.exists(file_path):
            open(file_path, "w").close()

        if os.path.getsize(file_path) > 0:
            file = open(file_path, "r")
            file_data = json.loads(file.read())
            file.close()
        else:
            file_data = dict()

        file_data_reviews = file_data.get("reviews")
        reviews = review_data["reviews"]

        if file_data_reviews is None:
            file_data.update({"reviews": reviews})
        else:
            file_data_reviews_id = list(map(lambda x: x["reviewId"], file_data_reviews))
            reviews_add = list()
            i = 0
            for review_id in list(map(lambda x: x["reviewId"], reviews)):
                if review_id not in file_data_reviews_id:
                    reviews_add.append(reviews[i])
                i += 1
            file_data_reviews = file_data_reviews + reviews_add
            file_data.update({"reviews": file_data_reviews})

        file_data.update({"aspects": review_data["aspects"]})
        file_data.update({"tags": review_data["tags"]})

        file = open(file_path, "w")
        file.write(json.dumps(file_data))
        file.close()

    with sync_playwright() as p:
        def handle_response(response):
            if "fetchReviews?" in response.url:
                try:
                    reviews_data = response.json()["data"]
                    save_json_place_reviews(reviews_data, current_place_id)
                except:
                    None

        print("Start collecting reviews and data - (region_id: " + region_id + ", category: " + category + ")")

        all_places_id = read_json_places_id()

        for place_id in all_places_id:
            url = f"https://yandex.ru/maps/org/-/{place_id}/reviews/"
            current_place_id = place_id

            # connect_to_tor()
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            page.on("response", handle_response)
            page.goto(url)

            execute_captcha(page)

            page.wait_for_load_state("load")

            place_data = json.loads(BeautifulSoup(page.content(), "html.parser").find("script", class_="state-view").text)["stack"][0]["results"]["items"][0]
            save_json_place_data(place_data, place_id)

            try:
                page.locator("div[class=business-reviews-card-view__reviews-container]").wait_for(timeout=2000)

                start_reviews = json.loads(BeautifulSoup(page.content(), "html.parser").find("script", class_="state-view").text)["stack"][0]["results"]["items"][0]["reviewResults"]
                save_json_place_reviews(start_reviews, place_id)

                while True:
                    review_cards = page.locator("div[class=business-reviews-card-view__review]")
                    items_on_page = len(review_cards.element_handles())
                    review_cards.element_handles()[-1].scroll_into_view_if_needed()
                    review_cards.element_handles()[-1].hover()
                    page.mouse.wheel(0, 1000)
                    page.wait_for_timeout(2000)
                    items_on_page_after_scroll = len(review_cards.element_handles())
                    if items_on_page_after_scroll > items_on_page:
                        continue
                    else:
                        break
            except:
                None

            page.context.close()
            browser.close()

        print("Finish collecting reviews and data - (region_id: " + region_id + ", category: " + category + ")")
        print("--------------------")
