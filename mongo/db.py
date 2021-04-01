import discord
from datetime import datetime
import time
import os

import pymongo
from pymongo.errors import OperationFailure, BulkWriteError, DuplicateKeyError
from dotenv import load_dotenv

load_dotenv()
client = pymongo.MongoClient(os.getenv('MONGODB'))
dev = os.getenv('DEV')
global db

if dev:
    db = client.test
else:
    db = client.main

### models ######
def guildModel(guild):
    return {
            "_id": guild.id,
            "name": guild.name,
            "owner": guild.owner_id,
            "joined_at": datetime.now().isoformat(),
            "created_at": guild.created_at.isoformat()
    }

def userModel(user):
    return {
        "_id": user.id,
        "name": user.name,
        "bal": 0
    }

######## CRUD ##########
def simpleInsert(obj, model, coll):
    try:
        if isinstance(obj, list):
            return coll.insert(model(map(lambda x: x.id, obj)))
        return coll.insert(model(obj))
    except OperationFailure as e:
        print(f"MongoDB update error in collection {coll}\nError:{e}")

def insert(obj, model, coll):
    unique = lambda d: coll.find({"_id": d.id}).count() == 0
    r=0
    try:
        if isinstance(obj, list):
                filtered = list(filter(unique, obj))
                if filtered:
                    if len(filtered) < 2:
                        r = coll.insert(model(filtered[0]))
                    else:
                        r = coll.insert(list(map(model, filtered)))
        else:
            if unique(obj):
                r = coll.insert(model(obj))
        return r
    except OperationFailure as e:
        print(f"MongoDB update error in collection {coll}\nError:{e}")

def update(query, update, coll, upsert=True):
    try:
        if isinstance(id, list):
            return coll.update_many(query, update)
        else:
            return coll.update_one(query, update)
    except OperationFailure as e:
        print(f"MongoDB update error in collection {coll}\nError:{e}")

def remove(query, coll):
    try:
        return coll.remove(query)
    except OperationFailure as e:
        return print(f"MongoDB remove error in collection {coll}\nError:{e}")

def find(doc, coll):
    try:
        if isinstance(doc, list):
            return coll.find_many(doc)
        else:
            return coll.find_one(doc)
    except OperationFailure as e:
        return print(f"MongoDB find error in collection {coll}\nError:{e}")
