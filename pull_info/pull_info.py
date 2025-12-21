import click
import requests
import tqdm
import csv

from requests.compat import urljoin
from time import sleep

from card import Card


scryfall_url = "https://api.scryfall.com"
common_headers = {"User-Agent": "ScryfallPull/.1", "accept": "application/json"}

courtesy_wait = 100 #Time in ms to wait between requests, Scryfall requests between 50-100ms_

@click.command()
@click.option("-o", "--out", type=click.Path(dir_okay=False,writable=True),help="Filename to store output. Output will be in csv and file WILL BE OVERWRITTEN")
@click.option("-s", "--search", type=str,multiple=True,help="Parameters to search by, see full documentation for formatting. Can be provided multiple times.")
@click.option("-i", "--input",type=click.Path(exists=True,dir_okay=False),help="Input filename for a list of cards to return information for, each card should be on its own line")
@click.option("-c", "--columns",type=click.Choice(Card.valid_output_columns),multiple=True,help="Output column information to include, can be specified multiple times. See https://scryfall.com/docs/api/cards Default is everything but images, which is handled separately")
@click.option("--max",type=int,help="Max cards to pull",default=-1)
@click.option("--image",type=bool,help="Whether to include image information in output. For now this is in the format =IMAGE(url) for use with Google Sheets")
def pull(out,search,input,columns,max,image):
    """
    Given a list of card names or other search parameters, pulls specified information from Scryfall.
    """
    card_names = []

    if input is not None:
        with open(input) as f:
            card_names = [line.strip() for line in f]
    

    cards = []
    if len(card_names) > 0:
        for card in card_names:
            cards.append(Card(pull_card(card,columns,image=image)))
            sleep(courtesy_wait/1000)

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