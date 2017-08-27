__license__ = 'GPL 3'
__copyright__ = '2015, Jason Kulatunga <jason@quietthyme.com>'
__docformat__ = 'restructuredtext en'


import os, re, time, sys, logging
from calibre.ebooks.metadata.book.base import Metadata
from calibre.ebooks.metadata import title_sort

logger = logging.getLogger(__name__)

class Book(Metadata):

    def __init__(self):
        Metadata.__init__(self, '')
        self._new_book = False

        self.size = 0
        self.datetime = time.gmtime()
        self.path = '' #the quitthyme book storage_id
        self.thumbnail = None

        self.quietthyme_id = -1

    def __eq__(self, other):
        # use lpath because the prefix can change, changing path
        return (self.quietthyme_id == other.quietthyme_id) and (self.quietthyme_id != -1) and (other.quietthyme_id != -1)

    @classmethod
    def from_quietthyme_metadata(cls, qt_metadata):
        book = cls()
        book.title = qt_metadata['title']
        book.authors = []
        #authors
        for author in qt_metadata['authors']:
            book.authors.append(author)
        book.size = qt_metadata['storage_size']
        #book.datetime = qt_metadata[]
        book.quietthyme_id = qt_metadata['id']
        book.path = qt_metadata['storage_type'] + '://' + \
                    str(qt_metadata['id']) + '/' + \
                    qt_metadata['storage_filename'] + qt_metadata['storage_format']
        book.thumbnail = None
        book.tags = qt_metadata['tags']

        #additional properties

        #populate identifiers
        book.identifiers['isbn'] = qt_metadata.get('isbn', qt_metadata.get('isbn',None))
        if 'amazon_id' in qt_metadata:
            book.identifiers['amazon'] = qt_metadata['amazon_id']
        if 'google_id' in qt_metadata:
            book.identifiers['google'] = qt_metadata['google_id']
        if 'goodreads_id' in qt_metadata:
            book.identifiers['goodreads'] = qt_metadata['goodreads_id']

        book.rating = qt_metadata.get('average_rating', None)

        book.series = qt_metadata.get('series_name',None)
        book.series_index = qt_metadata.get('series_number', None)

        book.comments = qt_metadata.get('short_summary', None)

        book.publisher = qt_metadata.get('publisher',None)

        # class Thumbnail():
        #     def __init__(self, path):
        #         self.image_path = path

        #book.thumbnail = Thumbnail("/home/jason/cover.jpg")
        #book.thumbnail = Thumbnail('http://ak-hdl.buzzfed.com/static/enhanced/webdr06/2013/7/30/18/grid-cell-14969-1375222023-8.jpg')
        cover_path = qt_metadata.get('cover', '')
        if cover_path:
            import urllib2
            try:
                book.thumbnail = urllib2.urlopen("https://s3.amazonaws.com/" + cover_path).read()
            except:
                book.thumbnail = None

        return book
        #raise NotImplementedError()

    @classmethod
    def from_calibre_metadata(cls, calibre_metadata):
        "Initialize MyData from a dict's items"
        book = cls()
        book.smart_update(calibre_metadata)
        return book
