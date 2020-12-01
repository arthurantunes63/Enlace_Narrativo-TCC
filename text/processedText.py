import time
import re
import string

import pandas as pd
from text.utils.emotion import adverbs as advList
from text.utils.emotion import pairs

class BookDoc:
    '''
     A class that represents the book processed.

     Attributes:
        _book(Book): The Book object.
        _nlp(): The spacy object to process the book.
        _doc(Doc): The book processed.
        _cleanDoc(Doc): The book without noise. 

     Methods:
        clearDoc(): Removes noise from the processed book text.
        extractCharacters(): Extracts validated characters names from the book.
        _extractPersonGroup(): Returns a list with the groups of persons.
        _extractAmbiguousEnts(): Extracts ambiguous entities based on the total of occurrences of the given entity type.
        _countEntsLabel(): Returns the total of occurrences of the entities from the processed book.
        _extractInitials(): Extracts initials from a name list based on a regex.
        _extractPseudoProperNoun(): Extracts "pseudo proper nouns" based on the total of occurrences of proper nouns and another classes for the same word.
        buildNetwork(): Make connections between characters based in a range, and calculates the relation weight through the total occurrences of this relationship.
        _sentenceHasModifiers(): Verify if a word has adverbial modifiers or negation based on its sentence.
        analysisEmotion(lexicon, emotionPerChapter, locEmotion): Analysis the emotions of the book based on a emotion lexicon.
    '''
    def __init__(self, book, nlp, doc = None, cleanDoc = None):
        self._book = book
        self._nlp = nlp
        self._doc = []
        for chapter in book._chapters:
        	self._doc.append(nlp(chapter))
        	# Time delay
        	if len(self._doc) % 2 == 0:
        		time.sleep(1.5)
        self._cleanDoc = cleanDoc

    def clearDoc(self, num = False, punct = False, stop = False, space = False):
        '''
        Removes noise from the processed book text.

        Parameters:
            num (bool): Filter or not words like numbers.
            puct (bool): Filter or not punctuation. 
            stop (bool): Filter or not stop words.
            space (bool): Filter or not spaces.
        '''
        cleanDoc = []
        for chapter in self._doc:
            cleanChapter = []
            for word in chapter:
                if word.is_stop == stop and word.is_punct == punct\
                   and word.like_num == num and word.is_space == space:
                    cleanChapter.append(word)
            cleanDoc.append(cleanChapter)
        self._cleanDoc = cleanDoc

    def extractCharacters(self):
        '''
        Extracts validated characters names from the book.
        
        Returns:
            clearNames(list): The list with the characters names.
        '''
        names = []
        surnames = []

        for chapter in self._doc:
            i = 0
            while i < len(chapter):
                if chapter[i].tag_ == 'NNP' and chapter[i].ent_type_ == 'PERSON'\
                   and chapter[i].ent_iob_ == 'B' and chapter[i].text == chapter[i].lemma_\
                   and not chapter[i].is_stop and not chapter[i].like_num and chapter[i-1].tag_ != 'PRP$'\
                   and not self._filterSpecialCharac(chapter[i].lower_):
                    if chapter[i+1].ent_type_ != 'PERSON' and chapter[i-1].ent_type_ != 'PERSON'\
                        and chapter[i].lower_ not in names:
                        names.append(chapter[i].lower_)
                    if chapter[i+1].tag_ == 'NNP' and chapter[i+1].ent_type_ == 'PERSON'\
                        and chapter[i+1].ent_iob_ == 'I' and chapter[i+1].text == chapter[i+1].lemma_\
                        and not chapter[i+1].is_stop and not chapter[i+1].like_num\
                        and chapter[i+1].lower_ not in names and not self._filterSpecialCharac(chapter[i+1].lower_):
                            surnames.append(f'{chapter[i].lower_} {chapter[i+1].lower_}')
                            i += 1

                i += 1

        # Validation
        charactersOut = []
        for surname in surnames:
            parts = surname.split(' ')
            if parts[0] in names:
                for name in names:
                    if name.find(parts[1]) != -1:
                        charactersOut.append(name)

        for word in names:
            if word[-1:] == 's' and word[-2:] != 'es'\
               and word[:len(word)-1] in names:
                    charactersOut.append(word[:len(word)-1])
                    charactersOut.append(word)
            elif word[:len(word)-2]  and word[-2:] == 'es'\
                 and word[:len(word)-2] in names:
                charactersOut.append(word[:len(word)-2])
                charactersOut.append(word)

        extracts = [self._extractAmbiguousEnts(label = 'PERSON'), self._extractPersonGroup(), self._extractPseudoProperNoun(), self._extractInitials(names)]

        for extract in extracts:
            for info in extract:
                if info in names:
                    charactersOut.append(info)
    
        clearNames = [name for name in names if name not in charactersOut]

        return clearNames

    def _extractPersonGroup(self):
        '''Returns a list with the groups of persons.'''
        group = []
        for chapter in self._doc:
            for word in chapter:
                if word.i < len(chapter)-3: 
                    if word.lower_ == 'the' and chapter[word.i+1].tag_ == 'NNP'\
                    and chapter[word.i+2].tag_ == 'NNP' and chapter[word.i+1].ent_type_ == 'PERSON'\
                    and chapter[word.i+2].ent_type_ == 'PERSON':
                        group.append(chapter[word.i+1].lower_)
                    if word.tag_ == 'NNP' and chapter[word.i+1].lower_ == 'the':
                        group.append(chapter[word.i+2].lower_)
                    if word.tag_ == 'NNP' and chapter[word.i+1].text == ','\
                        and chapter[word.i+2].lower_ == 'the':
                        group.append(chapter[word.i+3].lower_)
        return list(set(group))

    def _extractAmbiguousEnts(self, label):
        '''
        Extracts ambiguous entities based on the total of occurrences\
        of the given entity type.

        Parameters:
            label (str): Ent label for validation.

        Returns:
            ents (list): The list of ambiguous entities.
        '''
        ents = []
        entLabels = self._countEntsLabel()
        for i in entLabels:
            for j in entLabels:
                if i[0] == j[0] and i[1] == label.upper() and i != j:
                    if entLabels[i] < entLabels[j]:
                        ents.append(i[0].lower())
        return list(set(ents))

    def _countEntsLabel(self):
        '''Returns the total of occurrences of the entities from the processed book.'''
        labelCount = {}
        for chapter in self._doc:
            for ent in chapter.ents:
                label = (ent.text, ent.label_)
                if label in labelCount:
                    labelCount[label] += 1
                else:
                    labelCount[label] = 1
        return labelCount

    def _extractInitials(self, names):
        '''Extracts initials from a name list based on a regex.'''
        pattern = "^[a-z]$|^[a-z]\.$|^([a-z]\s[a-z])$|^([a-z]\.[a-z]\.)$"
        initialPattern = re.compile(pattern, flags = re.MULTILINE)
        initials = list(filter(initialPattern.search, names))
        return initials

    def _extractPseudoProperNoun(self):
        '''
        Extracts "pseudo proper nouns" based on the total of occurrences
        of proper nouns and another classes for the same word.
        '''
        words = {}
        for chapter in self._doc:
            for word in chapter:
                key = (word.lower_, word.tag_)
                if key in words:
                    words[key] += 1
                else:
                    words[key] = 1
        wordsProperNoun = []
        for word in words:
            if word[1] == 'NNP':
                wordsProperNoun.append(word[0])
        wordsCountProper = {}
        for word in words:
            if word[0] in wordsProperNoun:
                wordsCountProper[word] = words[word]
        pseudoProperNoun = []
        for i in wordsCountProper:
            for j in wordsCountProper:
                if i[0] == j[0] and i[1] == 'NNP' and i != j:
                    if wordsCountProper[i] < wordsCountProper[j]:
                        pseudoProperNoun.append(i[0].lower())

        return list(set(pseudoProperNoun))

    def buildNetwork(self, dist = 15, idxCharacters = True):
        '''
        Make connections between characters based in a range, and calculates the
        relation weight through the total occurrences of this relationship.

        Parameters:
            dist (int): Range pattern to set relationships.
            idxCharacters (bool): Sets if the connections will be between indexes.

        Returns:
            links (list): The connections between the characters.
            strength (list): The intensity of the connections.
        '''
        connections = {}
        for chapter in self._doc:
            for i in range(len(chapter) - dist):
                if chapter[i].lower_ in self._book._characters:
                    for j in range(i + 1, i + dist + 1):
                        if chapter[j].lower_ in self._book._characters:
                            if chapter[i].lower_ != chapter[j].lower_:
                                if idxCharacters:
                                    par = tuple(sorted(((self._book._characters\
                                                         .index(chapter[i].lower_),
                                                         self._book._characters\
                                                         .index(chapter[j].lower_)))))
                                else:
                                    par = tuple(sorted(((chapter[i].lower_, chapter[j].lower_))))   
                                if par in connections:
                                    connections[par] += 1
                                else:
                                    connections[par] = 1
        links = list(connections.keys())
        intensity = list(connections.values())
        return links, intensity 

    def _sentenceHasModifiers(self, word, advList):
        '''
        Verify if a word has adverbial modifiers or negation based on its
        sentence.

        Parameters:
            word (token): The word for the analysis of its sentence.

        Returns:
            neg (bool): The word have or not negation.
            advStrength (int/float): The strength of the adverb.
        '''
        neg = False
        advStrength = 1
        for wordSentence in word.sent:
            # negação com dependência indireta
            if wordSentence.dep_ == 'neg' and wordSentence.head == word.head:
                neg = True
            # negação com dependência direta
            elif wordSentence.dep_ == 'neg' and wordSentence.head == word:
                neg = True
            if wordSentence.dep_ == 'advmod' and wordSentence.head == word:
                if wordSentence.lower_ in advList['Increase']:
                    advStrength = 2
                elif wordSentence.lower_ in advList['Decrease']:
                    advStrength = 0.5
                else:
                    advStrength = 1
        return neg, advStrength

    def filterDataFrame(self, dataframe, array, column):
        return dataframe.loc[dataframe[column].isin(array)]

    def analysisEmotion(self, lexicon, locEmotion = ['joy', 'trust', 'disgust', 'fear', 'anger',
                                                     'surprise', 'anticipation', 'sadness'],
                        emotionPerChapter = True):
        '''
        Analysis the emotions of the book based on a emotion lexicon.

        Parameters:
            lexicon (DataFrame): A lexicon of emotion words - columns pattern: Word, Emotion, Value
            emotionPerChapter (bool): Sets if the analysis will be separated into chapters.
            locEmotion (list): The set of emotions that will be considered in the analysis.
        '''
        lexiconWords = self.filterDataFrame(lexicon, locEmotion, 'Emotion')['Word'].unique()

        if emotionPerChapter:
            emotions = []
        else:
            wordc = 0
            avgEmotion = {}    
        for count, chapter in enumerate(self._doc):
            if emotionPerChapter:
                wordc = 0
                avgEmotion = {}
            for word in chapter:
                if word.text in lexiconWords:
                    neg, advStrength = self._sentenceHasModifiers(word, advList)
                    wordc += 1
                    affect = (lexicon['Word'] == word.text)\
                                & (lexicon['Value'] > 0)
                    hasEmotion = lexicon.loc[affect]
                    options = {"compact": True, "bg": "#09a3d5",
                               "color": "white", "font": "Source Sans Pro"}
                    for idx, row in hasEmotion.iterrows():
                        if row['Emotion'] in locEmotion:
                            if row['Emotion'] in avgEmotion:
                                if neg:
                                    if pairs[row['Emotion']] in avgEmotion:
                                        avgEmotion[pairs[row['Emotion']]] += 1 * advStrength
                                else:
                                    avgEmotion[row['Emotion']] += 1 * advStrength
                            elif neg:
                                avgEmotion[pairs[row['Emotion']]] = 1 * advStrength
                            else:
                                avgEmotion[row['Emotion']] = 1 * advStrength
            if emotionPerChapter:
                for key in avgEmotion:
                    avgEmotion[key] = (avgEmotion[key]*100)/wordc
                emotions.append(avgEmotion)
        if emotionPerChapter:
            chapterEmotion = {}
            for emotion in locEmotion:
                chapterEmotion[emotion] = []
            for dicionario in emotions:
                for key in dicionario:
                    for emotion in chapterEmotion:
                        if key == emotion:
                            chapterEmotion[emotion].append(dicionario[key])
            return chapterEmotion
        else:
            for key in avgEmotion:
                avgEmotion[key] = (avgEmotion[key]*100)/wordc
            emotions = avgEmotion

            return emotions

    def _filterSpecialCharac(self, word):
        for letter in word:
            if letter in string.punctuation:
                return True
        return False