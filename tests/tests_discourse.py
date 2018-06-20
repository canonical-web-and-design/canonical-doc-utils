import unittest
from CanonicalDocUtils.cli.md2yaml import get_link
from CanonicalDocUtils.cli.md2yaml import strip_comments
from CanonicalDocUtils.cli.md2yaml import get_items

class TestGetLink(unittest.TestCase):
# get_link should return { title: , source:, location:} or nothing
    def test_dict_or_nothing(self):
        t = '* Just some random text'
        self.assertIsNone(get_link(t))
        t = '*  Some text [a link](/t/topic-text/104)'
        self.assertIsInstance(get_link(t),dict)
    def test_proper_dict(self):
        t = '*  Some text [a link](/t/topic-text/104)'
        r = get_link(t)
        self.assertEqual(r['title'], 'a link')
        self.assertEqual(r['source'], '/t/topic-text/104')
        self.assertEqual(r['location'], 'topic-text.md')

class TestStripComments(unittest.TestCase):
# strip_comments(text): should remove HTML comment blocks
    def test_all_comments(self):
        t = 'Some text\n<!-- A comment block to take out -->\nSome text'
        r = 'Some text\n\nSome text'
        self.assertEqual(strip_comments(t),r)
        t = 'Some text\n  <!-- A different comment \n  -->\nSome text'
        self.assertEqual(strip_comments(t),r)
        t = 'Some text\n<!--\n A comment block to take out \n-->\nSome <-- silly --> text'
        r = 'Some text\n\nSome <-- silly --> text'
        self.assertEqual(strip_comments(t),r)     
        
class TestGetItems(unittest.TestCase):
# get_link should return { title: , source:, location:} or nothing
    def test_list_or_nothing(self):    
        t = 'Just some random text'
        self.assertIsNone(get_items(t))
        t = '*  Some text [a link](/t/topic-text/104)'
        self.assertIsInstance(get_items(t),list)
        self.assertEqual(get_items(t)[0]['location'],'topic-text.md' )
        self.assertEqual(get_items(t)[0]['title'],'a link' )
        self.assertEqual(get_items(t)[0]['source'],'/t/topic-text/104' )
# get_header_groups should return list of headers and blocks of text between