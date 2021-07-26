"""
This module is used for compiling a database where keys are stems and values
are lemmas, tamplates and other stems of Russian nouns from Wiktionary. 
"""

import mwclient
from time import time
import shelve
import threading

start_time = time()

# Method to form sets of features (stem, template_name, val_name)
def get_features(line, template_name, features):
    
    # Check if the slot is not empty, and if not,
    # that a characher after '=' is aphabetical.
    try:
        alpha = line[line.index('=') + 1].isalpha()
    except (IndexError, ValueError):
        alpha = False
        
    # Get val_name and stem. 
    if alpha is True:
        after_split = line.split('=')
        val_name = after_split[0][1:]

        # Remove accent character. 
        stem = standardize_str(after_split[1])

        if stem != '':
            features.append([stem, template_name, val_name])

    # Return a list of features.     
    return features

# Method for the case when features are written in one line. 
def get_features_line(line, templates, features):

    # Get a template name. 
    template_name = line.split('|')[0][2:]

    # Add it to the set with all used template names. 
    templates.add(template_name)

    # Split the line by 'основа'. 
    after_split = line.split('|основа')
    stems = []

    # Try to get all stems and val_names in line.
    # Empirically the number of possible stems in this case was limited to 3.
    # As it's an exception, rude approximation was used. 
    try:
        stem = (standardize_str(after_split[1][1:].split('|')[0]), 'основа')
        stems.append(stem)
        stem1 = (standardize_str(after_split[2][2:].split('|')[0]), 'основа1')
        stems.append(stem1)
        stem2 = (standardize_str(after_split[3][2:].split('|')[0]), 'основа2')
        stems.append(stem2)

        # Add them to features. 
        for stem in stems:

            # Check if stem-val is not an empty string. 
            if stem[0] != '':
                features.append([stem[0], template_name, stem[1]])
                
    # If there are leaas than 3, get all present.              
    except IndexError:

        # Check if there is at least one stem. 
        if stems != []:
            for stem in stems:
                if stem[0] != '':
                    features.append([stem[0], template_name, stem[1]])

    return features

# Method used to get a standard string (lowercased and without accents).
def standardize_str(s):
    s = s.replace('\u0301', '').replace('\u0300', '').lower()
    return s

# Form a database, where keys are stems, values are a dict, where
# keys are lemmas, values are pairs template name-val_name. 
def dict_maker(lemmas, db, templates):

    for lemma in lemmas:
        if lemma != '':

            # Find a page of current lemma. 
            page = mwclient.page.Page(site, lemma)

            # Store wikitext of the page. 
            page_content = page.text()

            # Split the text.
            lines = page_content.split('\n')

            # A list of features. 
            features = []

            # To avoid 'reference before assignment' error. 
            template_name = ''
            another_stem = False
            
            for line in lines:

                # Get a teplate name, cut the brackets. 
                if '{{сущ ru ' in line:
                    template_name = line[2:]

                    # If there are too many characters in the line, it's more likely
                    # that all features are written in single line,
                    # so a separate method used for handling the case. 
                    if len(template_name) >= 25:
                        features = get_features_line(line, templates, features)

                    # Otherwise save the template name and add it to the set. 
                    else:
                        templates.add(template_name)

                # Get a template name for second names. 
                elif '{{Фам ' in line:
                    template_name = line[2:]

                    if len(template_name) >= 25:
                        features = get_features_line(line, templates, features)

                    else:
                        templates.add(template_name)

                # Get a stem.     
                elif '|основа=' in line:
                    features = get_features(line, template_name, features)
                        
                # Get the second stem if there is one.     
                elif '|основа' in line:

                    # Check that a stem has a number and the slot is not empty. 
                    try:
                        digit = line[line.index('а') + 1].isdigit()
                        if line[line.index('а') + 2] == '=':
                            another_stem = True
                    except IndexError:
                        brackets = False

                    if another_stem is True:
                        features = get_features(line, template_name, features)

            # Add obtained keys and values to the dict.
            if features != []:
                for feature in features:
                    value = (feature[1], feature[2])
                    draft_dict.setdefault(feature[0], {}).setdefault(value, lemma.lower()) 
    
# Сonnect to the site.
site = mwclient.Site('ru.wiktionary.org')

# Array of threads.
processes = []

# The file with nouns is opened.
with open('nouns.txt', 'r', encoding='utf8') as f:

    # Get a list of nouns. 
    words = f.read().split('\n')

# The number of words per single thread.
# A number of threads = ~175000/n.
n = 14000

# Split the words into separate arrays in terms of the number of threads. 
lists = [words[i:i+n] for i in range(0,len(words),n)]

# Temporate dict for stems. 
draft_dict = {}

# Set for templates. 
templates = set()
    
# Go through sub-arrays and create a thread for each one. 
for lemmas in lists:

    # Create a thread.
    process = threading.Thread(target=dict_maker, args=(lemmas, draft_dict, templates))
    process.start()
    processes.append(process)

# Join threads. 
for process in processes:
    process.join()  

# Create a file with templates names. 
with open('templates.txt', 'w', encoding='utf8') as f:
    for t in templates:
        f.write(t + '\n')
        
# The database file is created. 
with shelve.open('noun_stems_db', 'c', writeback=True) as db:
    db.update(draft_dict)

end_time = time()
time_taken = end_time - start_time
print("%s minutes" % (round((time_taken / 60), 2)))
#252.9 minutes
