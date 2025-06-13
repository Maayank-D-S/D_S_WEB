from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os

# === Load environment variable ===
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === Path to DOCX file ===
doc_path = r"C:\Users\vaibh\Downloads\Ramvan_Villas_Final_Updated.docx"  # Ensure this is in the same directory

# === Step 1: Load the document ===
loader = UnstructuredWordDocumentLoader(doc_path)
documents = loader.load()

# === Step 2: Split into chunks ===
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documents)

# === Step 3: Generate embeddings ===
embedding = OpenAIEmbeddings(
    openai_api_key="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"
)
vectordb = FAISS.from_documents(chunks, embedding)

# === Step 4: Save FAISS vector store ===
vectordb.save_local("ramvan_villas_faiss")

print("✅ Vector database created and saved as 'ramvan_villas_faiss/'")
