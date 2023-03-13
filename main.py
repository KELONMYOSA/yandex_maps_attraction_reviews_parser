from places_id_collector import collect_places_id
from reviews_and_data_collector import collect_reviews_and_data

region_ids = ["55"]
categories = ["museum", "landmark_attraction", "decorative_object_board_of_honor", "park", "zoo", "cafe", "restaurant",
              "fast_food", "coffee_shop"]

for region_id in region_ids:
    for category in categories:
        collect_places_id(region_id, category)

for region_id in region_ids:
    for category in categories:
        collect_reviews_and_data(region_id, category)
