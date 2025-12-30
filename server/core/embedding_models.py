from fastembed import TextEmbedding,SparseTextEmbedding
from .config import settings

dense_embedding = TextEmbedding(settings.DENSE_EMBEDDING_MODEL)
sparse_embedding = SparseTextEmbedding(model_name=settings.SPARSE_EMBEDDING_MODEL)