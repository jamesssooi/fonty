'''search.py: Library to handle the search of fonts.'''

import os.path
import click
from whoosh.query import Phrase, And, Term
from whoosh.qparser import QueryParser
from whoosh.index import create_in, open_dir, EmptyIndexError, Index
from whoosh.fields import Schema, TEXT, KEYWORD, ID
from fonty.lib.constants import SEARCH_INDEX_PATH
from fonty.models.repository import Repository

SCHEMA = Schema(
    id=ID(stored=True),
    name=TEXT(stored=True),
    category=KEYWORD(stored=True),
    repository_path=ID(stored=True)
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

    try:
        repo = Repository.load_from_path(result['repository_path'])
        remote_family = repo.get_family(result['name'])
    except FileNotFoundError:
        raise

    return repo, remote_family

def create_index() -> Index:
    '''Creates a font search schema.'''
    if not os.path.exists(SEARCH_INDEX_PATH):
        os.makedirs(SEARCH_INDEX_PATH, exist_ok=True)
    return create_in(SEARCH_INDEX_PATH, SCHEMA)

def index_fonts(repository: Repository, path_to_repository: str) -> None:
    '''Indexes a repository's font data.

       A local index file will be automatically created in the user's
       application directory if an existing index does not exists.
    '''

    index = load_index()
    writer = index.writer()

    # Delete all existing index for this repository and start clean
    # TODO: Implement incremental indexing
    writer.delete_by_term('repository_path', path_to_repository)

    # Index all font families in this repository
    for family in repository.families:
        writer.add_document(
            id=family.generate_id(path_to_repository),
            name=family.name,
            repository_path=path_to_repository
        )
    writer.commit()

def unindex_fonts(path_to_repository: str) -> int:
    '''Unindex a entire repository. Returns the number of documents deleted.'''
    index = load_index(create=False)
    writer = index.writer()

    # Delete all existing index for this repository
    count = writer.delete_by_term('repository_path', path_to_repository)
    writer.commit()

    return count

def load_index(create: bool = True) -> Index:
    '''Loads a search index file. If one does not exist, create it.'''
    try:
        index = open_dir(SEARCH_INDEX_PATH)
    except EmptyIndexError:
        if create:
            index = create_index()
        else:
            raise

    return index


class SearchNotFound(Exception):
    '''Exception: Raises when a search results fails to return any results.'''
    def __init__(self, keyword, suggestion):
        super(SearchNotFound, self).__init__()
        self.keyword = keyword

        if isinstance(suggestion, list):
            suggestion = ', '.join(suggestion)
        self.suggestion = suggestion
