import os
import pinecone
from pinecone.core.client.exceptions import ApiException

# ref:
# https://betterprogramming.pub/enhancing-chatgpt-with-infinite-external-memory-using-vector-database-and-chatgpt-retrieval-plugin-b6f4ea16ab8

# Quickstart
# https://docs.pinecone.io/docs/quickstart
# https://dev.classmethod.jp/articles/dive-deep-into-modern-data-saas-about-pinecone/
# https://docs.pinecone.io/docs/indexes

"""
Qdrant: https://github.com/qdrant/qdrant
Chroma: https://github.com/chroma-core/chroma
Typesense: https://github.com/typesense/typesense
pgvector
"""

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX")
"""
Init
"""
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

"""
Create Index
"""
# Define index configuration with user_id and room_id as attributes
index_config = pinecone.IndexConfig(index_name=PINECONE_INDEX , dimension=128, metric="euclidean", attributes=["user_id", "room_id"])
# Create or get the index
pinecone.create_index(config=index_config, if_exists=pinecone.IndexExistsAction.IGNORE)


"""
Store Vecs
"""
# Insert vectors with user_id and room_id attributes
index = pinecone.Index(PINECONE_INDEX)
vectors = [("vector1", [0.1, 0.2, 0.3], {"uid": "user1", "rid": "room1"}),
            ("vector2", [0.4, 0.5, 0.6], {"uid": "user1", "rid": "room2"}),]
#attributes = {"user_id": "user1", "room_id": "room1"}, {"user_id": "user2", "room_id": "room2"}]
try:
    index.upsert(vectors=vectors)#, set_metadata=attributes)
except ApiException as e:
    print(e)


"""
Query vec
"""
# Search vectors with user_id and room_id filters
query_vector = [0.7, 0.8, 0.9]
#results = pinecone.query(index_name="my_index", query=query_vector, filter={"user_id": "user1", "room_id": "room1"})
chat_id = "17844a60-efd7-456e-b1fc-59f7d8ffab59"
results = index.query(query_vector, filter={"user": 1, "chat_id":chat_id }, top_k=5)

# Get the results
for result in results:
    print(result.id, result.score)
