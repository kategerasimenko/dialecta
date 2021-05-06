from corpora.utils.db_utils import SENTENCE_COLLECTION
from .db_to_html import db_response_to_html


def compile_query(dialect, transcription, standartization, lemma, annotation):
    query_parts = {}

    if transcription:
        query_parts['transcription'] = transcription

    if standartization:
        query_parts['standartization'] = standartization

    if annotation:
        annotation = annotation.replace('-', ' ')
        ann_parts = annotation.split()
        query_parts['annotations'] = {'$elemMatch': {'tags': {'$all': ann_parts}}}

    if lemma:
        if 'annotations' not in query_parts:
            query_parts['annotations'] = {'$elemMatch': {}}
        query_parts['annotations']['$elemMatch']['lemma'] = lemma

    query = {'words': {'$elemMatch': query_parts}}

    if dialect:
        query['dialect'] = {'$in': [int(d) for d in dialect]}

    return query


def search(dialect, transcription, standartization, lemma, annotation):
    query = compile_query(dialect, transcription, standartization, lemma, annotation)
    results = SENTENCE_COLLECTION.find(query)
    result_html = db_response_to_html(results)
    return result_html
