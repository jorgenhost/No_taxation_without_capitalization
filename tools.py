import requests
from bs4 import BeautifulSoup
import time
import os
import pandas as pd
import numpy as np

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

    response = requests.get(url, headers=header) # Request
    json_ = response.json()
    log(response) # Log 

    return json_

def get_evals_bbr(bbr_df: pd.DataFrame, year):
    property_vals=[{'unitId': bbr_df['unitId'][i], f'eval_prop_{year}': e['propertyValue'], f'eval_land_{year}': e['landValue'], 'last_changed':e['lastChange'], 'eval_year': e['evaluationYear']} 
                for i, evaluationInfos in enumerate(bbr_df['evaluationInfos'])
                for e in evaluationInfos if e['evaluationYear'] == year]
    
    df=pd.DataFrame(property_vals)
    df['eval_year']=df['eval_year'].astype('int16')
    eval_prop = f'eval_prop_{year}'
    eval_land= f'eval_land_{year}'
    df[eval_prop]=df[eval_prop].astype('int32')
    df[eval_land]=df[eval_land].astype('int32')
    df['last_changed']=pd.to_datetime(df['last_changed'])
    df = df.sort_values(by='last_changed', ascending=False).drop_duplicates(subset='unitId', keep='first')
    df=df.rename(columns={'unitId': 'guid', 'last_changed': 'eval_last_changed'})
    df = df.reset_index(drop=True)
    return df

def convert_latex_table(latex_str):
    # Find the beginning and end of the tabular environment
    begin = latex_str.find("\\begin{tabular}")
    end = latex_str.find("\\end{tabular}")

    # Extract the contents of the tabular environment
    tabular_str = latex_str[begin:end]

    # Split the tabular environment into rows
    rows = tabular_str.split("\\\\")
    rows = [row.strip() for row in rows]

    # Split the first row into columns
    cols = rows[1].split("&")
    cols = [col.strip() for col in cols]

    # Get the length of the longest column name
    max_len = max([len(col) for col in cols])

    # Reformat the table rows
    new_rows = []
    for row in rows[2:]:
        # Split the row into cells
        cells = row.split("&")
        cells = [cell.strip() for cell in cells]

        # Pad the column names with spaces
        cells[0] = cells[0].ljust(max_len)

        # Add the row to the new table
        new_row = " & ".join(cells)
        new_rows.append(new_row)

    # Reformat the table columns
    new_cols = " & ".join([col.ljust(max_len) for col in cols])

    # Reformat the table header
    header = "\\begin{table}[H]\n\\centering\n\\begin{tabular}{@{}lcccc@{}}\n\\toprule\n"
    header += " " * max_len + " & \\multicolumn{3}{c}{Quantile regressions} & \\\\\\cmidrule(lr){2-4}\n"
    header += new_cols + " & OLS-FE \\\\\n\\midrule\n"

    # Reformat the table footer
    footer = "\\bottomrule\n\\end{tabular}\n\\end{table}\n"

    # Combine the header, new rows, and footer
    new_tabular_str = header + "\n".join(new_rows) + "\n" + footer

    return new_tabular_str