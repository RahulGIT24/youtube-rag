from qdrant_client import QdrantClient,models
from .config import settings

def create_collection():
    client = QdrantClient(host=settings.QDRANT_HOST,port=settings.QDRANT_PORT)
    name=settings.QDRANT_COLLECTION
    is_exist = client.collection_exists(name)

    if is_exist == False:
        client.create_collection(collection_name=name,
            vectors_config={
                "dense-text":models.VectorParams(
                    size=client.get_embedding_size(settings.DENSE_EMBEDDING_MODEL),
                    distance=models.Distance.COSINE
                )
            },
            sparse_vectors_config={
                "sparse-text":models.SparseVectorParams()
            }
        )

    client.close()

def get_client():
    return QdrantClient(host=settings.QDRANT_HOST,port=settings.QDRANT_PORT)