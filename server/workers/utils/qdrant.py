from qdrant_client import QdrantClient

from dotenv import load_dotenv
import os

load_dotenv()

def get_client():
    return QdrantClient(host=os.getenv('QDRANT_HOST'),port=os.getenv('QDRANT_PORT'))