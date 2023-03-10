from places_id_collector import collect_places_id

region_ids = ["11176"]
categories = ["museum", "landmark_attraction", "decorative_object_board_of_honor", "park", "zoo", "cafe", "restaurant", "fast_food"]

for region_id in region_ids:
    for category in categories:
        collect_places_id(region_id, category)
