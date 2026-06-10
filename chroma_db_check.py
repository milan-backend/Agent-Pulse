import chromadb
import os

client = chromadb.HttpClient(
host=os.getenv("CHROMA_HOST"),
port=443,
ssl=True,
headers={
"Authorization": f"Bearer {os.getenv('CHROMA_TOKEN')}"
}
)
