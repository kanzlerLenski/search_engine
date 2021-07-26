"""
This module is used for compiling a database where keys are flexions and values
are templates and val_name of stems of Russian nouns from Wiktionary. 
"""

import mwclient
from time import time
import shelve
import re 

start_time = time()

# Сonnect to the site.
site = mwclient.Site('ru.wiktionary.org')

# A list of templates from stems-db. 
templates = []

# Get the templates from the stems-db. 
with open('templates.txt', 'r', encoding='utf8') as f:
    templates = f.read().split('\n')

# The database file is created. 
with shelve.open('noun_flexions_db', 'c', writeback=True) as db:

    for template in templates:
        if template != '':

            try:
                page = mwclient.page.Page(site, 'Шаблон:' + template)

            except mwclient.errors.InvalidPageTitle:
                continue

            # Store wikitext of the page.  
            page_content = page.text()

            # Split the text. 
            lines = page_content.split('\n')
            for line in lines:

                # Default value for flexion-val.
                flexion = '?'

                # Variable for template-val_name pair. 
                pair = set()

                # Get a val_name (stem).
                if '={{{основа' in line:
                    after_split = line.split('={{{')
                    after_after_split = after_split[1].split('}}}')

                    val_name = after_after_split[0]

                    # Form a pair of template and val_name. 
                    pair = (template, val_name)

                    # Cut off extra brackets if there is any. 
                    flexion = re.sub('[^а-я]', '', (after_after_split[1]))

                # In case there is variation of a flexion, store all of them. 
                if 'основа' in flexion:
                    flexions = []
                    flexions.append(flexion.split('основа')[0])
                    try:
                        flexions.append(after_after_split[2])
                    except IndexError:
                        pass
                    
                    for f in flexions:

                        f = f.replace('\u0301', '').replace('\u0300', '')

                        # Check if default value has changed. 
                        if f != '?':
                            db.setdefault(f, set()).add(pair)
                    
                # If there is only one flexion.
                else:
                    if flexion != '?':
                        db.setdefault(flexion, set()).add(pair)

end_time = time()
time_taken = end_time - start_time
print("%s minutes" % (round((time_taken / 60), 2)))
#2.98 minutes
