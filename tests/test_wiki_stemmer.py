import unittest
import wiki_stemmer

class Tests(unittest.TestCase):

    def setUp(self):
        self.stmr = wiki_stemmer.Wiki_Stemmer('noun_stems_db', 'noun_flexions_db')
        self.s = 'друг'
        self.s2 = 'куздра'

    # Check stemming. 
    def test_stemmer_manager1(self):
        res = self.stmr.stemmer_manager(self.s)
        self.assertEqual(list(res), ['друг'])

    # Check the fallback.
    def test_stemmer_manager2(self):
        res2 = self.stmr.stemmer_manager(self.s2)
        self.assertEqual(list(res2), ['куздра', 'куздр', 'кузд', 'куз'])

    # Check lemmatization if the stem is the db. 
    def test_lemmatize(self):
        res3 = self.stmr.lemmatize(self.s)
        self.assertEqual(set(res3), {'друг', 'другое'})

    # Check if the original string is yielded if the stem is not in the db. 
    def test_lemmatize2(self):
        res4 = self.stmr.lemmatize(self.s2)
        self.assertEqual(set(res4), {'куздра', 'куздр', 'кузд', 'куз'})

if __name__ == '__main__':
    unittest.main()
