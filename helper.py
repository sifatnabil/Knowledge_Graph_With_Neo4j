import urllib
import json
import time
import numpy as np

from data_cleaning import create_svo_triples

def query_google(query, api_key, limit=10, indent=True, return_lists=True):
    """
    This functions takes a query, searches google knowledge graph using the 
    knoweldge graph API and return a list containing description, entity type
    and URLs.

    Args: 
        query (str): The query to be searched.
        api_key (str): The API key to be used.

    Returns: 
        list: A list containing the description, entity type and URLs.
    """
    
    text_ls = []
    node_label_ls = []
    url_ls = []
    
    params = {
        'query': query,
        'limit': limit,
        'indent': indent,
        'key': api_key,
    }   
    
    service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
    url = service_url + '?' + urllib.parse.urlencode(params)
    response = json.loads(urllib.request.urlopen(url).read())
    
    if return_lists:
        for element in response['itemListElement']:

            try:
                node_label_ls.append(element['result']['@type'])
            except:
                node_label_ls.append('')

            try:
                text_ls.append(element['result']['detailedDescription']['articleBody'])
            except:
                text_ls.append('')
                
            try:
                url_ls.append(element['result']['detailedDescription']['url'])
            except:
                url_ls.append('')
                
        return text_ls, node_label_ls, url_ls
    
    else:
        return response


def get_obj_properties(api_key, tup_ls):
    
    init_obj_tup_ls = []
    
    for tup in tup_ls:

        try:
            text, node_label_ls, url = query_google(tup[2], api_key, limit=1)
            new_tup = (tup[0], tup[1], tup[2], text[0], node_label_ls[0], url[0])
        except:
            new_tup = (tup[0], tup[1], tup[2], [], [], [])
        
        init_obj_tup_ls.append(new_tup)
        
    return init_obj_tup_ls


def add_layer(tup_ls, api_key, non_nc, nlp):

    svo_tup_ls = []
    
    for tup in tup_ls:
        
        if tup[3]:
            svo_tup = create_svo_triples(tup[3], non_nc, nlp)
            svo_tup_ls.extend(svo_tup)
        else:
            continue
    
    return get_obj_properties(api_key, svo_tup_ls)
        

def subj_equals_obj(tup_ls):
    
    new_tup_ls = []
    
    for tup in tup_ls:
        if tup[0] != tup[2]:
            new_tup_ls.append((tup[0], tup[1], tup[2], tup[3], tup[4], tup[5]))
            
    return new_tup_ls


def check_for_string_labels(tup_ls):
    # This is for an edge case where the object does not get fully populated
    # resulting in the node labels being assigned to string instead of list.
    # This may not be strictly necessary and the lines using it are commnted out
    # below.  Run this function if you come across this case.
    
    clean_tup_ls = []
    
    for el in tup_ls:
        if isinstance(el[2], list):
            clean_tup_ls.append(el)
            
    return clean_tup_ls


def create_word_vectors(nlp, tup_ls):

    new_tup_ls = []
    
    for tup in tup_ls:
        if tup[3]:
            doc = nlp(tup[3])
            new_tup = (tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], doc.vector)
        else:
            new_tup = (tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], np.random.uniform(low=-1.0, high=1.0, size=(300,)))
        new_tup_ls.append(new_tup)
        
    return new_tup_ls


def calculate_time(start_time):
    end_time = time.time()
    time_taken = end_time - start_time
    return time_taken