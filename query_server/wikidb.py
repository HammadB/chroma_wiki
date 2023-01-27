import pandas as pd
import wikipedia
import csv
import bz2
import wikitextparser as wtp
import bs4 as bs
import tiktoken
from typing import Optional, Union
from index import Index
from nltk.tokenize import sent_tokenize
from os import path
from config import settings
from token_consts import MAX_SECTION_TOKENS
import pickle

WIKI_INDEX_FILE = 'wiki_index.pckl'
DISCARD_CATEGORIES = set(['See also', 'References', 'External links', 'Further reading', "Footnotes",
    "Bibliography", "Sources", "Citations", "Literature", "Footnotes", "Notes and references",
    "Photo gallery", "Works cited", "Photos", "Gallery", "Notes", "References and sources",
    "References and notes", "General and cited references"])

# TODO: encoder should be parameterized
ENCODING = "cl100k_base"
tokenizer = tiktoken.get_encoding(ENCODING)

path_to_wikipedia_index = settings.wikipedia_local_index_path
path_to_wikipedia_data = settings.wikipedia_local_dump_path

class WikipediaDatabase():
    """ A wikipedia database allows for:

            1. querying for document sections by ID or page title.
            2. querying for full pages by page id or title
            3. searching for relevant articles against a query

        For now it is just a simple wrapper over a local pandas df of wikipedia sections as well as a local copy of wikipedia and the NN index.
        Ideally we should split this class to seperate the datastore from the local wikipedia copy.
    """
    index: Index

    def __init__(self, dataframe_path: Optional[str] = None, index_path: Optional[str] = None):
        # Vector datastore
        if dataframe_path:
            self.df: pd.DataFrame = pd.read_pickle(dataframe_path)
            # self.df.drop("embeddings", axis=1, inplace=True)
        else:
            self.df = pd.DataFrame([], columns=["title", "section", "section_index", "permalink", "content", "tokens"])
        
        self.index = Index(index_path)

        # Wikipedia documentstore
        self.index_filename = path_to_wikipedia_index
        self.wiki_filename = path_to_wikipedia_data
        # HACK: this is just a quick hack to read the index and store. We should do this better
        if not path.exists(WIKI_INDEX_FILE):
            self.wiki_index = {}
            self._build_wiki_index()
            with open(WIKI_INDEX_FILE, 'wb') as handle:
                pickle.dump(self.wiki_index, handle, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            print("Loading wiki index from file")
            with open(WIKI_INDEX_FILE, 'rb') as handle:
                self.wiki_index = pickle.load(handle)

    # TODO __gettiem__
    def get_section_by_ids(self, ids: list[int]):
        """ Get a section by ids """
        return self.df.iloc[ids]
    
    def get_section_by_id(self, id: int):
        """Get a section by id """
        return self.get_section_by_ids([id]).iloc[0]

    def search(self, query: str) -> list[str]:
        """ Search wikipedia api for articles relevant to a task """
        return wikipedia.search(query)

    def get_page(self, page_title: str) -> Union[wtp.WikiText, None]:
        """ Get the wikitext for a page given its title """
        try:
            start_byte, data_length = self._search_index(page_title)
        except KeyError:
            return None
        chunk_xml = self._decompress_chunk(start_byte, data_length)
        parsed_page = self._extract_page_from_chunk(page_title, chunk_xml)
        return parsed_page

    def add_page(self, page_title: str, page_content: wtp.WikiText):
        """Add a page to the vector datastore """
        # Don't add existing pages
        if page_title in self.df['title'].values:
            return
        print(f"Adding page: {page_title}")
        entries = self._format_document_for_indexing(page_title, page_content)        
        did_add = self.index.add_to_index([entry[4] for entry in entries])
        if did_add:
            self.df = pd.concat([self.df, pd.DataFrame(entries, columns=["title", "section", "section_index", "permalink", "content", "tokens"])])

    def save(self, dataframe_path: str, index_path: str):
        self.index.save_to_path(index_path)
        self.df.to_pickle(dataframe_path)

    # TODO refactor this for treating index vs local wiki appropriately
    def _encode_with_split(self, section: str, max_tokens: int = MAX_SECTION_TOKENS):
        """ Encodes and potentially splits a section into seperate sections on sentence boundries by max_tokens """
        encoded_section = tokenizer.encode(section)
        if len(encoded_section) >= max_tokens:
            sentences = sent_tokenize(section.replace("\n", " "))
            n_tokens = 0
            prev_boundary = 0
            result = []
            for i, sentence in enumerate(sentences):
                # Space is one token
                n_tokens += 1 + len(tokenizer.encode(sentence))
                if n_tokens >= max_tokens:
                    max_length_sentence = " ".join(sentences[prev_boundary:i])
                    encoded_max_length_sentence = tokenizer.encode(max_length_sentence)
                    # Edge case where the entire sentence is unbrekable and too long
                    if len(encoded_max_length_sentence) <= MAX_SECTION_TOKENS:
                        result.append((max_length_sentence, encoded_max_length_sentence))
                    n_tokens = 0
                    prev_boundary = i
                    
            # Handle remaining
            max_length_sentence = " ".join(sentences[prev_boundary:])
            encoded_max_length_sentence = tokenizer.encode(max_length_sentence)
            if len(encoded_max_length_sentence) <= MAX_SECTION_TOKENS:
                result.append((max_length_sentence, encoded_max_length_sentence))
            
            return result
        return [(section, encoded_section)]


    # TODO refactor this for treating documents as a class
    def _format_document_for_indexing(self, page_title: str, page_content: wtp.WikiText):
        res = []
        for section in page_content.sections:
            if section.title == None or (section.title and section.title.strip() not in DISCARD_CATEGORIES):
                # TODO: parse plain text, remove headings, format tables for ingestion, remove media references
                encoded_sections = self._encode_with_split(section.plain_text())
                section_index = 0
                for split_section, encoded_section in encoded_sections:
                    # TODO: The empty entry is the permalink, leave alone for now. artifact from port, remove later
                    res.append((page_title, section.title, section_index, '', split_section, len(encoded_section)))
                    section_index += 1
        return res 

    def _search_index(self, page_title: str) -> tuple[int, int]:
        """ Search downloaded index for the btye range of the chunk containing the page """
        return self.wiki_index[page_title]

    def _build_wiki_index(self):
        """ Load the wikipedia index which tells you which bz2 byte range to read into memory """
        index_file = open(self.index_filename, 'r')
        csv_reader = csv.reader(index_file, delimiter=':')
        # A line is start_byte:id:name
        prev_start_byte = None
        curr_chunk_titles = []
        for line in csv_reader:
            curr_page_title = line[2]
            start_byte = int(line[0])
            # First chunk is offset by non-zero value
            if prev_start_byte == None:
                prev_start_byte = start_byte
            # end of chunk
            if start_byte != prev_start_byte:
                for title in curr_chunk_titles:
                    self.wiki_index[title] = (prev_start_byte, start_byte - prev_start_byte)
                prev_start_byte = start_byte
                curr_chunk_titles = []
                curr_chunk_titles.append(curr_page_title)
            else: 
                curr_chunk_titles.append(curr_page_title)
        index_file.close()

    def _decompress_chunk(self, start_byte: int, data_length: int) -> str:
        """ Read a chunk of the wikpedia dump """
        with open(self.wiki_filename, 'rb') as wiki_file:
            wiki_file.seek(start_byte)
            data = wiki_file.read(data_length)
        return bz2.decompress(data).decode("utf-8") 

    def _extract_page_from_chunk(self, page_title: str, chunk_xml: str) -> wtp.WikiText:
        """ Parse a chunk and return the page contents as WikiText for a given page title"""
        soup = bs.BeautifulSoup(chunk_xml, "lxml")
        pages = soup.find_all('page')
        for page in pages:
            if page.title.text == page_title:
                text = page.find('text').text
                return wtp.parse(text)
        # TODO: handle this better
        print(f'didnt find {page_title}')

