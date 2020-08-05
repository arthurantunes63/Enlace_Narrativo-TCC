import unicodedata

class Book:
    '''
    A class that represents a Book.

    Attributes:
        title (str): The book title.
        _content (str): The book content.
        _chapters (str): The book content split into chapters.
        chapterNumber (int): The number of chapters of the book.
        _characters (list): The characters extracted from the book.

    Methods:
        openBook(): Sets the book content string from a file.
        lowercaseBook(): Sets the book content string to a lowercase string.
        removeAccents(): Removes accents from the book content string.
        sliceBook(): Splits the book content into chapters.
    '''
    def __init__(self, title, content = None, chapters = None, chapterTotal = None,\
                 characters = None):
        '''
        Constructs all the necessary attributes for the book object.

        Parameters:
            title (str): The book title.
            _content (str): The book content.
            _chapters (str): The book content broken in chapters.
            chapterTotal (int): The total number of chapters of the book.
            _characters (list): The characters extracted from the book.
        '''
        self.title = title
        self._content = content
        self._chapters = chapters
        self.chapterTotal = chapterTotal
        self._characters = characters

    @property
    def characters(self):
        '''Returns character list with their strings capitalized.'''
        return sorted(set(list(map(lambda character: character\
                                   .capitalize(), self._characters))))

    @characters.setter
    def characters(self, characters):
        '''
        Sets the character list with theirs strings lowercased. 
            
        Parameters:
            characters (list): The character list.
        '''
        self._characters = sorted(set(list(map(lambda character: character\
                                               .lower(), characters))))

    def openBook(self, path, encoding = 'utf8'):
        '''
        Sets the book content string from a file.

        Parameters:
            path (str): The path of the file.
            encoding (str): The encoding of the file.
        '''
        with open(path, 'r', encoding = encoding) as book:
            strBook = [line.strip() for line in book.readlines()]
        strBook = ' '.join(strBook)       
        self._content = strBook
        return self

    def lowercaseBook(self):
        '''Sets the book content string in a lowercase string.''' 
        self._content = self._content.lower()
        return self
            
    def removeAccents(self):
        '''Removes accents from the book content string.'''
        noAccent = unicodedata.normalize('NFKD',self._content)\
                   .encode('utf8', 'ignore').decode('utf8')
        self._content = noAccent
        return self

    def sliceBook(self, breaker):
        '''
        Splits the book content into chapters.
        
        Parameters:
            breaker (str): The delimiter for the chapters.
        '''
        chapters = self._content.split(breaker)
        self.chapterTotal = len(chapters)
        self._chapters = chapters
        return self