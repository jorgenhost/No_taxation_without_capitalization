import requests
from bs4 import BeautifulSoup
import time
import os
import pandas as pd

def log(response: requests.Response):
    """
    Creates or appends a log-file with information from a `requests.get()`-call.
    
    The information gathered is:
    - - - - - - - -
        timestamp   :   Current local time.
        status_code :   Status code from requests call.
        length      :   Length of the HTML-string.
        output_path :   Current working directory.
        url         :   The URL of the response.
    """

    # Open or create the csv file
    if os.path.isfile('log'):
        log = open('log','a')
    else: 
        log = open('log','w')
        header = ['timestamp', 'status_code', 'length', 'output_file', 'url'] # Header names
        log.write(';'.join(header) + "\n")
        
    # Gather log information
    status_code = response.status_code # Status code from the request result
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) # Local time
    length = len(response.text) # Length of the HTML-string
    output_path = os.getcwd() # Output path
    url = response.url # URL-string
    
    # Open the log file and append the gathered log information
    with open('log2','a') as log:
        log.write(f'{timestamp};{status_code};{length};{output_path};{url}' + "\n") 

def get_soup(url: str, header: dict) -> BeautifulSoup:
    """
    Constructs a HTML-string from a request of the given URL. 
    Requests are logged, see `log()`. 

    Input:
    - - - - - - - - 
    url (str)     :    URL of the website to receive the HTML-string from. \n
    header (dict) :    Dictionary to send in the query string for the request.

    Returns:
    - - - - - - - - 
    soup (BeautifulSoup) :  HTML-string in the class of BeutifulSoup with 'lxml' parser.
    """

    response = requests.get(url, headers=header) # Request
    log(response) # Log 
    soup = BeautifulSoup(response.content, 'lxml') # Convert to response to HTML

    return soup

def get_json(url: str, header: dict):
    """
    Fetches the JSON-file from api.boliga.dk.  

    Input:
    - - - - - - - - 
    url (str)     :    URL of the website to receive the HTML-string from. \n
    header (dict) :    Dictionary to send in the query string for the request.

    Returns:
    - - - - - - - - 
    json :  json-file from Boliga's API.
    """

    response = requests.get(url, headers=header) # Request
    json_ = response.json()
    log(response) # Log 

    return json_

def get_evals_bbr(bbr_df: pd.DataFrame, year: int):
    """
    Fetches evaluation by each individual house (called 'guid' in the data) in a given year. 

    Input:
    - - - - - - - - 
    year (int)    :    Year of property valuation. \n
    header (dict) :    Dictionary to send in the query string for the request.

    Returns:
    - - - - - - - - 
    df (DataFrame) :  Returns DataFrame of property valuations by year.
    """

    property_vals=[{'guid': bbr_df['guid'][i], f'eval_prop_{year}': e['propertyValue'], f'eval_land_{year}': e['landValue'], f'eval{year}_last_changed':e['lastChange'], 'eval_year': e['evaluationYear']} 
                for i, evaluationInfos in enumerate(bbr_df['evaluationInfos'])
                for e in evaluationInfos if e['evaluationYear'] == year]
    
    df=pd.DataFrame(property_vals)
    # Tweak data types to conserve memory
    df['eval_year']=df['eval_year'].astype('int16')
    eval_prop = f'eval_prop_{year}'
    eval_land= f'eval_land_{year}'
    df[eval_prop]=df[eval_prop].astype('int32')
    df[eval_land]=df[eval_land].astype('int32')
    df[f'eval{year}_last_changed']=pd.to_datetime(df[f'eval{year}_last_changed'])
    df = df.sort_values(by=f'eval{year}_last_changed', ascending=False).drop_duplicates(subset='guid', keep='first')
    df = df.reset_index(drop=True)
    return df