__license__   = 'GPL v3'
__copyright__ = '2011, Jason Kulatunga <jason@quietthyme.com>'
__docformat__ = 'restructuredtext en'

from calibre.devices.interface import BookList as _BookList
class BookList(_BookList):

    def __init__(self, oncard, prefix, settings):
        _BookList.__init__(self, oncard, prefix, settings)
        self._bookmap = {}

    def supports_collections(self):
        return False

    def add_book(self, book, replace_metadata):
        return self.add_book_extended(book, replace_metadata, check_for_duplicates=True)

    def add_book_extended(self, book, replace_metadata, check_for_duplicates):
        '''
        Add the book to the booklist, if needed. Return None if the book is
        already there and not updated, otherwise return the book.
        '''
        try:
            b = self.index(book) if check_for_duplicates else None
        except (ValueError, IndexError):
            b = None
        if b is None:
            self.append(book)
            return book
        if replace_metadata:
            self[b].smart_update(book, replace_metadata=True)
            return self[b]
        return None

    def remove_book(self, book):
        self.remove(book)

    def get_collections(self):
        return {}