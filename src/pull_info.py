import click
import requests
import tqdm
import csv
import enum

valid_output_columns = [

]

courtesy_wait = 100 #Time in ms to wait between requests, Scryfall requests between 50-100ms_

@click.command()
@click.option("-o", "--out", type=click.Path(dir_okay=False,writable=True),help="Filename to store output. Output will be in csv and file WILL BE OVERWRITTEN")
@click.option("-s", "--search", type=str,multiple=True,help="Parameters to search by, see full documentation for formatting. Can be provided multiple times.")
@click.option("-i", "--input",type=click.Path(exists=True,dir_okay=False),help="Input filename for a list of cards to return information for, each card should be on its own line")
@click.option("-c", "--columns",type=click.Choice(valid_output_columns),multiple=True,help="Output column information to include, can be specified multiple times. See https://scryfall.com/docs/api/cards Default is everything but images")
@click.option("--max",type=int,help="Max cards to pull",default=-1)
def pull():
    """
    Given a list of card names or other search parameters, pulls specified information from Scryfall.
    """
    print("Hello")