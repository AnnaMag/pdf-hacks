from pymongo import MongoClient
from datetime import datetime

def set_collection(db_name, db_collection):

    try:

        client = MongoClient()#'mongodb://{0}:{1}/'.format(db_host, db_port))
        print('ok')

    except pymongo.errors.ConnectionFailure as e:

        print('error'% e)

    db = client.db_name

    return db.db_collection

def write_db(collection, doc):
    """
    write doc info to a MongoDB database.
    """

    #print('Inicio '.format(datetime.now()))

    collection.insert_one(doc)

    #print('Fin '.format(datetime.now()))
