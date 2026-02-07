import click
import requests
import tqdm
import csv

from requests.compat import urljoin
from time import sleep
from tqdm import tqdm
from copy import deepcopy

from card import Card



scryfall_url = "https://api.scryfall.com"
common_headers = {"User-Agent": "ScryfallPull/.1", "accept": "application/json"}

courtesy_wait = 100 #Time in ms to wait between requests, Scryfall requests between 50-100ms_

rarity_single = {
    "mythic": "M",
    "rare": "R",
    "uncommon": "U",
    "common": "C"
}

@click.command()
@click.option("-o", "--out", type=click.Path(dir_okay=False,writable=True),help="Filename to store output. Output will be in csv and file WILL BE OVERWRITTEN")
@click.option("-s", "--search", type=str,multiple=True,help="Parameters to search by, see full documentation for formatting. Can be provided multiple times.") #TODO
@click.option("-i", "--input",type=click.Path(exists=True,dir_okay=False),help="Input filename for a list of cards to return information for, each card should be on its own line")
@click.option("-c", "--columns",type=click.Choice(Card.valid_output_columns),multiple=True,help="Output column information to include, can be specified multiple times. See https://scryfall.com/docs/api/cards Default is everything but images, which is handled separately")
@click.option("-ci", "--column-file",type=click.Path(exists=True,dir_okay=False),help="Path to a file which contains output wanted output columns each contained on their own separate line, see -c command for valid column options")
@click.option("--image",is_flag=True,help="Whether to include image information in output. For now this is in the format =IMAGE(url) for use with Google Sheets. For multiple printings this grabs the oldest printing that matches the rarity flag (if used) and avoids secret lair and universes beyond if possible")
@click.option("--rarity",type=str,help="Rarity to use when determining between cards with multiple rarities. Note all input cards must have a valid printing of this rarity or an error will occur.")
def pull(out,search,input,columns,column_file,image,rarity):
    """
    Given a list of card names or other search parameters, pulls specified information from Scryfall.
    """
    card_names = []

    if column_file is not None:
        with open(column_file) as f:
            columns = [line.strip() for line in f]

    if len(columns) == 0:
        columns = Card.valid_output_columns

    if input is not None:
        with open(input) as f:
            card_names = [line.strip() for line in f]

    cards = []
    if len(card_names) > 0:
        for card in tqdm(card_names):
            cards.append(Card(pull_card(card),columns,image=image,rarity=rarity))
            sleep(courtesy_wait/1000)
    
    if out is None:
        for card in cards:
            out = card.get_card()

            if "rarity" in out:
                out["rarity"] = rarity_single[out["rarity"]]
                
            if image:
                out.update({"images": card.get_image()})

            print(out)
    else:
        if "power" in columns and "toughness" in columns:
            found = False
            for i in range(len(columns)):
                if columns[i] == "power" or columns[i] == "toughness":
                    if not found:
                        columns.pop(i)
                        columns.insert(i,"P/T")

                        found = True
                    else:
                        columns.pop(i)
                        break
    
        with open(out, 'w', encoding="utf8", newline="\n") as f:
            writer = csv.writer(f,quotechar='"',quoting=csv.QUOTE_MINIMAL)

            #Header
            header = deepcopy(columns)
            if image:
                header.append("Card Image")
                
            
            writer.writerow(header)

            for card in tqdm(cards):
                data = card.get_card()
                row = []

                for column in columns:
                    if column in data:
                        row.append(data[column])
                    else:
                        row.append("")

                if image:
                    row.extend(card.get_image())

                writer.writerow(row)

    
def pull_card(name):
    uri = "/cards/named"
    options = {"fuzzy": name}
    headers = common_headers

    url = urljoin(scryfall_url,uri)

    response = requests.get(url,params=options,headers=headers)

    response.raise_for_status()

    return response.json()

if __name__ == '__main__':
    pull()