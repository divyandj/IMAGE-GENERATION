from pymongo import MongoClient
from config import Config
from datetime import datetime  # Import datetime here too

class Image:
    collection = MongoClient(Config.MONGO_URI).imagetales.images

    @classmethod
    def create(cls, user_id, title, category, url, prompt):  # Added prompt parameter
        from bson.objectid import ObjectId
        result = cls.collection.insert_one({
            'user_id': ObjectId(user_id),
            'title': title,
            'category': category,
            'url': url,
            'prompt': prompt,  # Add prompt to the document
            'likes': 0,
            'created_at': datetime.now()
        })
        return result.inserted_id
    

    @classmethod
    def get_all(cls):
        return list(cls.collection.find())

    @classmethod
    def find_by_user(cls, user_id):
        from bson.objectid import ObjectId
        return list(cls.collection.find({'user_id': ObjectId(user_id)}))

    @classmethod
    def find_by_id(cls, image_id):
        from bson.objectid import ObjectId
        return cls.collection.find_one({'_id': ObjectId(image_id)})
    
    @classmethod
    def find_by_url(cls, url):
        return cls.collection.find_one({'url': url})