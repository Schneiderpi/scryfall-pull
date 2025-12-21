import json

class Card():
    valid_output_columns = [
        "cmc",
        "color_identity",
        "color_indicator",
        "colors",
        "defense",
        "edhrec_rank",
        "game_changer",
        "hand_modifier",
        "keywords",
        "legalities",
        "life_modifier",
        "loyalty",
        "mana_cost",
        "name",
        "oracle_text",
        "penny_rank",
        "power",
        "produced_mana",
        "reserved",
        "toughness",
        "type_line",
        "artist",
        "attraction_lights",
        "booster",
        "border_color",
        "card_back_id",
        "collector_number",
        "content_warning",
        "digital",
        "finishes",
        "flavor_name",
        "flavor_text",
        "frame_effects",
        "frame",
        "full_art",
        "games",
        "oversized",
        "prices",
        "printed_name",
        "printed_text",
        "printed_type_line",
        "promo",
        "promo_types",
        "purchase_uris",
        "rarity",
        "related_uris",
        "released_at",
        "reprint",
        "scryfall_set_uri",
        "set_name",
        "set_type",
        "set",
        "story_spotlight",
        "textless",
        "variation",
        "security_stamp",
        "watermark",
        "preview.previewed_at",
        "preview.source"
    ]

    def __init__(self,scryfall_response,columns,image=False):
        self.columns = columns
        self.image = image

        self.from_json(scryfall_response)

        if image:
            self.get_image_info(scryfall_response)
        
    def from_json(self,scryfall_response):
        self.card = {}

        for column in self.valid_output_columns:
            if column in scryfall_response and (self.columns is None or column in self.columns):
                self.card[column] = scryfall_response[column]

        self.card["id"] = scryfall_response["id"]

    def get_card(self):
        return self.card

    def get_image_info(self,scryfall_response):
        pass