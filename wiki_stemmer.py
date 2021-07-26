"""
Wiki_Stemmer contains a set of functions producing stems
for morphological analysis based on the information from Wiktionary.
"""

import shelve
import stemmer

# The class contains three arguments:
# 'stems' is for database with stems,
# 'flexions' - the same for flexions,
#'file' is for file with flexions in case of fallback.   
class Wiki_Stemmer(object):
    def __init__(self, stems, flexions):

        self.stems = stems
        self.flexions = flexions

        # stems_db and flexions_db are
        # for stems-db and flexions-db openning respectively.
        self.stems_db = shelve.open(stems, 'r')
        self.flexions_db = shelve.open(flexions, 'r')

        # length stores the length of the longest flexion.
        # It sets the number of characters to cut from the end of the original string.
        self.length = max(len(flex) for flex in self.flexions_db)

    # Deconstructor that closes dbs.
    def __del__(self):

        self.stems_db.close()
        self.flexions_db.close()

    # Stemmer based on morphological information from Wiktionary.
    def stemming(self, string):

        # Check, if that the input is str-instance. 
        if not isinstance(string, str):
            raise TypeError('This is not a string.')

        # Check, if it's not empty.
        if string is '':
            raise TypeError('Empty string.')

        # Lower-case. 
        string = string.lower()

        # ... cut some symbols at the end of it...
        for i in range(self.length + 1):

            # In case of zero flexion. 
            if i == 0:
                stem = string
                flexion = ''

            # Otherwise cut a set number of characters from the end of the string in turns.    
            else:
                stem = string[:-i]
                flexion = string[-i:]

            # Until we get the correct decomposition into stem and flexion,
            # which are contained in the dbs. 
            if stem not in self.stems_db or flexion not in self.flexions_db:
                continue
            
            else:
        
                # Until obtained stem and flexion have the same template name,
                # which means that the decomposition was correct. 
                if set(self.stems_db[stem]).intersection(self.flexions_db[flexion]):

                    # The correct stem for a word from the db is yielded. 
                    yield stem
                                
    # Method used to check if the Stemmer was capable to analyze the word.                             
    def stemmer_manager(self, string):
        stems = self.stemming(string)

        # To check if stemming has yilded anything. 
        check = False

        # If it did, yield those stems. 
        for stem in stems:
            check = True
            yield stem

        # Otherwise do the fallback to the primitive stemmer, which cuts
        # a set number of characters from the end of the string and yields
        # all possible variants. 
        if check == False:

            stems = stemmer.Stemmer().pseudostem_generator(string)
            for stem in stems:
                yield stem

    # Method used for lemmatization. 
    def lemmatize(self, string):

        # Get stems. 
        stems = self.stemmer_manager(string)

        # If stems as in the stems_db, yield it's lemma. 
        try:
            for stem in stems:
                for key in self.stems_db[stem]:
                    yield self.stems_db[stem][key]

        # Otherwise yield the original string. 
        except KeyError:
            stems = stemmer.Stemmer().pseudostem_generator(string)
            for stem in stems:
                yield stem
