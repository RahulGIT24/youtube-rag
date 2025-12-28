from fastembed import TextEmbedding
from dotenv import load_dotenv
import os

load_dotenv()
dense_embedding = TextEmbedding(os.getenv('DENSE_EMBEDDING_MODEL'))