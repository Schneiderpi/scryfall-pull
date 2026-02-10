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

@click.command()
@click.option("-o", "--out", type=click.Path(dir_okay=False,writable=True),help="Filename to store output. Output will be in csv and file WILL BE OVERWRITTEN")
@click.option("-s", "--search", type=str,multiple=True,help="Parameters to search by, see full documentation for formatting. Can be provided multiple times.") #TODO
@click.option("-i", "--input",type=click.Path(exists=True,dir_okay=False),required=True,help="Input filename for a list of cards to return information for, each card should be on its own line")
@click.option("-c", "--columns",type=click.Choice(Card.valid_output_columns),multiple=True,help="Output column information to include, can be specified multiple times. See https://scryfall.com/docs/api/cards Default is everything but images, which is handled separately")
@click.option("-ci", "--column-file",type=click.Path(exists=True,dir_okay=False),help="Path to a file which contains output wanted output columns each contained on their own separate line, see -c command for valid column options")
@click.option("--image",is_flag=True,help="Whether to include image information in output. For now this is in the format =IMAGE(url) for use with Google Sheets. For multiple printings this grabs the oldest printing that matches the rarity flag (if used) and avoids secret lair and universes beyond if possible")
@click.option("--exclude-set",type=str,multiple=True,help="Set to exclude from printings, can be provided multiple times")
@click.option("--default",type=click.Choice(["newest","oldest"]),help="How to choose which printing to use as the final printing output. Current choices are 'oldest' or 'newest'")
def pull(out,search,input,columns,column_file,image,exclude_set,default):
    """
    Given a list of card names or other search parameters, pulls specified information from Scryfall.
    """
    card_names = []

    if column_file is not None:
        with open(column_file) as f:
            columns = [line.strip() for line in f]

    if len(columns) == 0:
        columns = Card.valid_output_columns

    cards = []
    with open(input) as f:
        lines = f.readlines()


    desired_rarity = None
    desired_set = None
    for line in tqdm(lines):
        l = line.strip()
        
        if l.startswith("##"):
            desired_set = l[2:].strip()
            continue
        elif l.startswith("#"):
            desired_rarity = l[1:].strip()
            continue
        elif not l == "":
            cards.append(Card(pull_card(l),columns,get_alternates=True,desired_rarity=desired_rarity,desired_set=desired_set))
            sleep(courtesy_wait/1000)

        if desired_set is not None:
            desired_set = None

    if out is None:
        for card in cards:
            out = card.get_card(exclude_sets=exclude_set,sort=default)
                
            if not image:
                out.pop("image")

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
        
        if image:
            columns.append("image")

        with open(out, 'w', encoding="utf8", newline="\n") as f:
            writer = csv.writer(f,quotechar='"',quoting=csv.QUOTE_MINIMAL)

            #Header
            header = deepcopy(columns)
            writer.writerow(header)

            for card in tqdm(cards):
                data = card.get_card(exclude_sets=exclude_set,sort=default)
                row = []
                
                for column in columns:
                    if column == "image":
                        row.extend(data["image"])
                    elif column in data:
                        row.append(data[column])
                    else:
                        row.append("")

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