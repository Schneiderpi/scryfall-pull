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

        if image:
            self._get_image_from_scryfall(scryfall_response)
        
    def from_json(self,scryfall_response):
        card = {}

        for column in self.valid_output_columns:
            if column in scryfall_response and (self.columns is None or column in self.columns):
                if type(scryfall_response[column]) is str and "//" not in scryfall_response[column]: #Ignore columns with multifaced output
                    card[column] = scryfall_response[column]

        card["id"] = scryfall_response["id"]

        return card
    
    def from_json_multiface(self,scryfall_response):
        card = []

        for _ in range(len(scryfall_response["card_faces"])):
            card.append(self.from_json(scryfall_response))
        
        for i in range(len(scryfall_response["card_faces"])):
            face = scryfall_response["card_faces"][i]

            for column in self.valid_output_columns:
                if column in face and (self.columns is None or column in self.columns):
                    card[i][column] = face[column]

        return card
    
    def get_card(self):
        self._merge_p_t()
        if not self.multifaced:
            return self.card
        else:
            unified = {}

            for i in range(len(self.card)):
                face = self.card[i]

                for column in face:
                    if column not in unified and i == 0:
                        unified[column] = face[column]
                    elif column not in unified and i > 0:
                        unified[column] = "\\ " + face[column]
                    elif not unified[column] == face[column] and not face[column] == '':
                        unified[column] = unified[column] + "\n\\\n" + face[column]

            return unified

    def get_image(self):
            return ['=IMAGE("{}",1)'.format(url) for url in self.image_url]
    
    def _get_image_from_scryfall(self,scryfall_response):
        if not self.multifaced:
            self.image_url = [scryfall_response["image_uris"]["normal"]]
        else:
            self.image_url = [face["image_uris"]["normal"] for face in scryfall_response["card_faces"]]

    def _merge_p_t(self):
        if not self.multifaced:
            if "power" in self.card and "toughness" in self.card:
                self.card["P/T"] = self.card["power"] + " / " + self.card["toughness"]

                self.card.pop("power")
                self.card.pop("toughness")
        else:
            for face in self.card:
                if "power" in face and "toughness" in face:
                    face["P/T"] = face["power"] + " / " + face["toughness"]

                    face.pop("power")
                    face.pop("toughness")

    def __str__(self):
        return self.get_card()