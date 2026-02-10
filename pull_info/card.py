import json
import requests
from time import sleep
from tqdm import tqdm
from datetime import datetime
from copy import deepcopy

scryfall_url = "https://api.scryfall.com"
common_headers = {"User-Agent": "ScryfallPull/.1", "accept": "application/json"}

courtesy_wait = 100 #Time in ms to wait between requests, Scryfall requests between 50-100ms_

class Card():
    rarity_single = {
        "mythic": "M",
        "rare": "R",
        "uncommon": "U",
        "common": "C"
    }

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

    def __init__(self,scryfall_response,columns,get_alternates=True,desired_rarity=None,desired_set=None):
        self.columns = deepcopy(columns)
        self.multifaced = False
        self.desired_rarity = desired_rarity.lower() if desired_rarity is not None else desired_rarity
        self.desired_set = desired_set.lower() if desired_set is not None else desired_set

        if "card_faces" in scryfall_response:
            self.multifaced = True
        
        self.cards = [scryfall_response]

        if get_alternates:
            printings = self._get_alternate_printings(scryfall_response["prints_search_uri"])

            for card in printings:
                if self.multifaced:
                    self.cards.append(card)
                else:
                    self.cards.append(card)

    def trim_to_columns(self,card_object):
        card = {}

        for column in self.valid_output_columns:
            if column in card_object and (self.columns is None or column in self.columns):
                if type(card_object[column]) is not str or (type(card_object[column]) is str and "//" not in card_object[column]): #Ignore columns with multifaced output
                    if type(card_object[column]) is list:
                        card[column] = ", ".join(card_object[column])
                    else:
                        card[column] = card_object[column]

        card["id"] = card_object["id"]

        return card
    
    def trim_to_columns_multiface(self,card_object):
        card = []

        for _ in range(len(card_object["card_faces"])):
            card.append(self.trim_to_columns(card_object))
        
        for i in range(len(card_object["card_faces"])):
            face = card_object["card_faces"][i]

            for column in self.valid_output_columns:
                if column in face and (self.columns is None or column in self.columns):
                    card[i][column] = face[column]

        return card
    
    def get_card(self,**kwargs):
        printings = self.cards

        if self.desired_set is not None:
            _printings = [card for card in printings if card["set"] == self.desired_set]
            printings = _printings
        else:
            if "rarity" in kwargs or self.desired_rarity is not None:
                desired_rarity = kwargs["rarity"] if "rarity" in kwargs else self.desired_rarity

                _printings = [card for card in printings if card["rarity"] == desired_rarity]
                printings = _printings

            if "exclude_sets" in kwargs:
                _printings = [card for card in printings if card["set"] not in kwargs["exclude_sets"]]
                printings = _printings

            if "sort" in kwargs:
                if kwargs["sort"] == "oldest":
                    printings = sorted(printings,key=lambda d: datetime.strptime(d["released_at"],"%Y-%M-%d"))
                elif kwargs["sort"] == "newest":
                    printings = sorted(printings,key=lambda d: datetime.strptime(d["released_at"],"%Y-%M-%d"),reverse=True)

            if len(printings) > 1:
                _printings = [card for card in printings if card["lang"] == "en"]

                if len(_printings) > 0:
                    printings = _printings

            if len(printings) > 1:
                _printings = []

                for card in printings:
                    if "promo_types" in card and "universesbeyond" not in card["promo_types"]:
                        _printings.append(card)

                if len(_printings) > 0:
                    printings = _printings


        if len(printings) == 0:
            msg = "No valid printings for {} with restrictions.".format(self.cards[0]["name"])
            raise ValueError(msg)
    
        card = printings[0]
        self._get_image_from_scryfall(card)
        image = self.get_image()

        if self.multifaced:
            card = self.trim_to_columns_multiface(card)
        else:
            card = self.trim_to_columns(card)
        
        card = self._merge_p_t(card)
        
        if "rarity" in card:
            card["rarity"] = self.rarity_single[card["rarity"]]
        
        if not self.multifaced:
            card["image"] = image
            card.pop("id")
            return card
        else:
            unified = {}

            for i in range(len(card)):
                face = card[i]

                if "rarity" in face:
                    face["rarity"] = self.rarity_single[face["rarity"]]

                for column in face:
                    if column not in unified and i == 0:
                        unified[column] = face[column]
                    elif column not in unified and i > 0:
                        unified[column] = "\\ " + face[column]
                    elif not unified[column] == face[column] and not face[column] == '':
                        unified[column] = unified[column] + "\n\\\\\n" + face[column]

            unified["image"] = image
            unified.pop("id")
            return unified

    def get_image(self):
            return ['=IMAGE("{}",1)'.format(url) for url in self.image_url]
    
    def _get_image_from_scryfall(self,card_object):
        if not self.multifaced or card_object["layout"] in ["split","adventure"]:
            self.image_url = [card_object["image_uris"]["normal"]]
        else:
            self.image_url = [face["image_uris"]["normal"] for face in card_object["card_faces"]]

    def _merge_p_t(self,card):
        if not self.multifaced:
            if "power" in card and "toughness" in card:
                card["P/T"] = card["power"] + " / " + card["toughness"]

                card.pop("power")
                card.pop("toughness")
        else:
            for face in card:
                if "power" in face and "toughness" in face:
                    face["P/T"] = face["power"] + " / " + face["toughness"]

                    face.pop("power")
                    face.pop("toughness")
        
        return card

    def _get_alternate_printings(self,alternate_printings_url):
        headers = common_headers

        response = requests.get(alternate_printings_url,headers=headers)
        sleep(courtesy_wait/1000)

        response.raise_for_status()

        prints_search = response.json()

        return prints_search["data"]

    def __str__(self):
        return self.get_card()
    