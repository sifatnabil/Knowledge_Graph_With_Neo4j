import re
from definitions import *

def remove_special_characters(text):
    
    regex = re.compile(r'[\n\r\t]')
    clean_text = regex.sub(" ", text)
    
    return clean_text


def remove_stop_words_and_punct(text, non_nc, print_text=False):
    
    result_ls = []
    rsw_doc = non_nc(text)
    
    for token in rsw_doc:
        if print_text:
            print(token, token.is_stop)
            print('--------------')
        if not token.is_stop and not token.is_punct:
            result_ls.append(str(token))
    
    result_str = ' '.join(result_ls)

    return result_str


def create_svo_lists(doc, print_lists=False):
    
    subject_ls = []
    verb_ls = []
    object_ls = []

    for token in doc:
        if token.dep_ in SUBJECTS:
            subject_ls.append((token.lower_, token.idx))
        elif token.dep_ in VERBS:
            verb_ls.append((token.lemma_, token.idx))
        elif token.dep_ in OBJECTS:
            object_ls.append((token.lower_, token.idx))

    if print_lists:
        print('SUBJECTS: ', subject_ls)
        print('VERBS: ', verb_ls)
        print('OBJECTS: ', object_ls)
    
    return subject_ls, verb_ls, object_ls


def remove_duplicates(tup, tup_posn):
    
    check_val = set()
    result = []
    
    for i in tup:
        if i[tup_posn] not in check_val:
            result.append(i)
            check_val.add(i[tup_posn])
            
    return result


def remove_dates(tup_ls):
    
    clean_tup_ls = []
    for entry in tup_ls:
        if not entry[2].isdigit():
            clean_tup_ls.append(entry)
    return clean_tup_ls


def create_svo_triples(text, non_nc, nlp, print_lists=False):
    
    clean_text = remove_special_characters(text)
    doc = nlp(clean_text)
    subject_ls, verb_ls, object_ls = create_svo_lists(doc, print_lists=print_lists)
    
    graph_tup_ls = []
    dedup_tup_ls = []
    clean_tup_ls = []
    
    for subj in subject_ls: 
        for obj in object_ls:
            
            dist_ls = []
            
            for v in verb_ls:
                
                # Assemble a list of distances between each object and each verb
                dist_ls.append(abs(obj[1] - v[1]))
                
            # Get the index of the verb with the smallest distance to the object 
            # and return that verb
            index_min = min(range(len(dist_ls)), key=dist_ls.__getitem__)
            
            # Remove stop words from subjects and object.  Note that we do this a bit
            # later down in the process to allow for proper sentence recognition.
            no_sw_subj = remove_stop_words_and_punct(subj[0], non_nc)
            no_sw_obj = remove_stop_words_and_punct(obj[0], non_nc)
            
            # Add entries to the graph iff neither subject nor object is blank
            if no_sw_subj and no_sw_obj:
                tup = (no_sw_subj, verb_ls[index_min][0], no_sw_obj)
                graph_tup_ls.append(tup)
        
        clean_tup_ls = remove_dates(graph_tup_ls)
    
    dedup_tup_ls = remove_duplicates(graph_tup_ls, 2)
    clean_tup_ls = remove_dates(dedup_tup_ls)
    
    return clean_tup_ls