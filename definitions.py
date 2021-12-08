# Define the subject and its types
SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
# Define the verb and its types
VERBS = ['ROOT', 'advcl']
# Define the object and its types
OBJECTS = ["dobj", "dative", "attr", "oprd", 'pobj']
# Define the types of entities
ENTITY_LABELS = ['PERSON', 'NORP', 'GPE', 'ORG', 'FAC', 'LOC', 'PRODUCT', 'EVENT', 'WORK_OF_ART']

# Google Knowledge Search API Key 
api_key = open('api_key').read()