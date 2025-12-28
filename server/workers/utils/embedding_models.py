from fastembed import TextEmbedding,SparseTextEmbedding
from dotenv import load_dotenv
import os

load_dotenv()
dense_embedding = TextEmbedding(os.getenv('DENSE_EMBEDDING_MODEL'))
sparse_embedding = SparseTextEmbedding(model_name=os.getenv('SPARSE_EMBEDDING_MODEL'))