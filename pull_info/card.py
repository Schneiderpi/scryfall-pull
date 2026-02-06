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

        if "card_faces" in scryfall_response:
            self.multifaced = True
            self.card = self.from_json_multiface(scryfall_response)
        else:
            self.multifaced = False
            self.card = self.from_json(scryfall_response)

        print(self.card)

        if image:
            self._get_image_from_scryfall(scryfall_response)
        
    def from_json(self,scryfall_response):
        card = {}

        for column in self.valid_output_columns:
            if column in scryfall_response and (self.columns is None or column in self.columns):
                card[column] = scryfall_response[column]

        card["id"] = scryfall_response["id"]

        return card
    
    def from_json_multiface(self,scryfall_response):
        card = []

        for _ in range(len(scryfall_response["card_faces"])):
            card.append(self.from_json(scryfall_response))
        
        for face in scryfall_response["card_faces"]:
            for column in self.valid_output_columns:
                if column in scryfall_response["card_faces"] and (self.columns is None or column in self.columns):
                    face[column] = scryfall_response[column]

        return card
    
    def get_card(self):
        return self.card

    def get_image(self):
        return '=IMAGE("{}",1)'.format(self.image_url)
    
    def _get_image_from_scryfall(self,scryfall_response):
        uris = scryfall_response["image_uris"] if "image_uris" in scryfall_response else None
        
        self.image_url = uris["normal"]

    def __str__(self):
        return self.get_card()