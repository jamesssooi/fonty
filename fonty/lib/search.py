'''search.py: Library to handle the search of fonts.'''

import os.path
import click
from whoosh.query import Phrase, And, Term
from whoosh.qparser import QueryParser
from whoosh.index import create_in, open_dir, EmptyIndexError
from whoosh.fields import Schema, TEXT, KEYWORD, ID
from fonty.lib.constants import SEARCH_INDEX_PATH
from fonty.models.repository import Repository

SCHEMA = Schema(
    id=ID(stored=True),
    name=TEXT(stored=True),
    category=KEYWORD(stored=True),
    repository=ID(stored=True)
)

def search(name):
    '''Search the font index and return results.'''
    index = load_index()
    parser = QueryParser('name', SCHEMA)
    query = parser.parse(name)

    # Execute search query
    searcher = index.searcher()
    results = searcher.search(query)

    if not results:
        corrector = searcher.corrector('name')
        raise SearchNotFound(name, corrector.suggest(name))

    result = dict(**results[0]) # Convert search results object to Dictionary
    searcher.close()

    # Check if exact match
    if results and result['name'].lower() != name.lower():
        raise SearchNotFound(name, result['name'])

    repo = Repository.load_from_local(result['repository'])
    typeface = repo.get_typeface(result['name'])

    return repo, typeface

def create_index():
    '''Creates a font search schema.'''
    if not os.path.exists(SEARCH_INDEX_PATH):
        os.makedirs(SEARCH_INDEX_PATH, exist_ok=True)
    return create_in(SEARCH_INDEX_PATH, SCHEMA)

def index_fonts(repository):
    '''Indexes a repository's font data.

       A local index file will be automatically created in the user's
       application directory if an existing index does not exists.
    '''

    index = load_index()
    writer = index.writer()

    # Delete all existing index for this repository and start clean
    # TODO: Implement incremental indexing
    writer.delete_by_term('repository', repository.source)

    # Index all typefaces in this repository
    for typeface in repository.typefaces:
        writer.add_document(
            id=typeface.generate_id(repository.source),
            name=typeface.name,
            category=typeface.category,
            repository=repository.source
        )
    writer.commit()

def load_index(create=True):
    '''Loads a search index file. If one does not exist, create it.'''
    try:
        index = open_dir(SEARCH_INDEX_PATH)
    except EmptyIndexError:
        index = create_index() if create else False

    return index


class SearchNotFound(Exception):
    '''Exception: Raises when a search results fails to return any results.'''
    def __init__(self, keyword, suggestion):
        super(SearchNotFound, self).__init__()
        self.keyword = keyword

        if isinstance(suggestion, list):
            suggestion = ', '.join(suggestion)
        self.suggestion = suggestion
