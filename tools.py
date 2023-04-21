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

# From advanced microeconometrics

def outreg(
    results: dict,
    var_labels: list,
    name: str,
    se_type='normal',
) -> pd.Series:
    
    '''
    Args:
        Results (dict)      : pass the results (dict) output from the estimate()-function
        var_labels (list)   : List of variable names used previously in our regression
        name (str)          : the name given to the pd.Series as output
        se_type (str)       : If robust std. errors have been used, write in brackets []
    
    Returns:
        A pd.Series with variable names as index. NB! Add number of obs (N), time periods (T), regressors (K) and degrees of freedoms manually if appropriate.
        Ideally, pass one result at a time, and then merge with pandas later on.
        When merging, use 'outer' as method. In this case, it picks up all labels defined from different estimations
    
    '''
    sig_levels = {0.05: '*', 0.01: '**', 0.001: '***'} #Set significance level for p-value
    
    deg_of_frees = results['deg_of_frees'] #Extract degrees of freedom from results dict

    beta = pd.Series(results['b_hat'].reshape(-1), index=var_labels).round(2) #Make series of our coeff
    se = pd.Series(results['se'].reshape(-1), index=var_labels).round(3) #Make series of standard errors
    t_stat = pd.Series(results['t_values'].reshape(-1), index=var_labels).round(4) #Make series of t-values
    p_val = pd.Series(
                t.cdf(-np.abs(t_stat),df=deg_of_frees)*2, index=var_labels).round(4) #Make series of p-values, using the deg of freedoms
    
    temp_df = pd.concat((beta, se, p_val), axis=1) #concatenate above into dataframe, index is the varlabels
    temp_df.columns=['beta', 'se', 'pt'] #set column names to beta, se, pt (p-values)
    temp_df=temp_df.stack() #Stack it so we make a multiindex
    temp_df.name=name #Have to name the series

    #Defining i, j, k
    # i: index position of our coeffs/var_labels
    # j: index position of our standard errors
    # k: index position of our p-values
    # -> loop through these in increments of 3 and add stars for significance levels

    for i,j,k in zip(range(0,len(temp_df-2),3), range(1, len(temp_df-1),3), range(2,len(temp_df),3)):
        var_index=temp_df.index[i]
        se_index=temp_df.index[j]
        p_val_index=temp_df.index[k]
        if temp_df.at[p_val_index]<0.001:
            temp_df.at[var_index]=f'{temp_df.at[var_index]}'+sig_levels[0.001]
        elif temp_df.at[p_val_index]<0.01:
            temp_df.at[var_index]=f'{temp_df.at[var_index]}'+sig_levels[0.01]
        elif temp_df.at[p_val_index]<=0.05:
            temp_df.at[var_index]=f'{temp_df.at[var_index]}'+sig_levels[0.05]
        elif temp_df.at[p_val_index]>0.05:
            temp_df.at[var_index]=temp_df.at[var_index]
        
        #Write standard errors 
        if se_type != 'normal':
            temp_df.at[se_index]=f'[{temp_df.at[se_index]}]' #In brackes for robust std errors
        else:
            temp_df.at[se_index]=f'({temp_df.at[se_index]})' #In parentheses for 'normal' std errors