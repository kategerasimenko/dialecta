import pymongo

from trimco.settings import MONGO_URL, MONGO_DB_NAME


MONGO_CLIENT = pymongo.MongoClient(MONGO_URL)
MONGO_DB = MONGO_CLIENT[MONGO_DB_NAME]

WORD_COLLECTION = MONGO_DB['words']
#WORD_COLLECTION.drop()
WORD_COLLECTION.create_index('word')

STANDARTIZATION_COLLECTION = MONGO_DB['standartizations']
#STANDARTIZATION_COLLECTION.drop()
STANDARTIZATION_COLLECTION.create_index('word')

SENTENCE_COLLECTION = MONGO_DB['sentences']
#SENTENCE_COLLECTION.drop()