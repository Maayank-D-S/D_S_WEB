import streamlit as st
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_ollama.embeddings import OllamaEmbeddings
import os
from dotenv import load_dotenv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import asyncio

load_dotenv()

# Gemini model
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Load vector DB
embedding = OllamaEmbeddings(model="mistral")
index_dir = Path(__file__).resolve().parent / "krupal_faiss"
vectorstore = FAISS.load_local(
    str(index_dir),
    embedding,
    allow_dangerous_deserialization=True
)

IMAGE_MAP = {
    "bedroom": "images/bedroom.jpeg",
    "house": "images/house.jpeg",
    "living room": "images/livingroom.jpeg",
    "dining room": "images/dining_room",
}

executor = ThreadPoolExecutor()

# ----------------- Helper Functions ------------------

def violates_policy_llm(text: str):
    prompt = f"""
You are a content filter. Check if the following text contains any references to religion, sex, politics, terrorism, violence, or drugs.

Text: "{text}"

If it violates, reply only with "BLOCK". Otherwise, reply only with "ALLOW".
"""
    result = model.generate_content(prompt).text.strip().upper()
    return result == "BLOCK"

def is_greeting_or_vague_llm(text: str):
    prompt = f"""
Classify the user's message. If it's a greeting or vague unrelated message like "hi", "hello", "good morning", "how are you", or anything that doesn't ask about the project, respond with "GREETING". Otherwise respond with "QUERY".

Message: "{text}"
Category:"""
    result = model.generate_content(prompt).text.strip().upper()
    return result == "GREETING"

def vague_query_response():
    return "Hi! I’m your smart assistant. Ask me anything about Krupal Habitat."

def _fetch_response_sync(query: str):
    for keyword in IMAGE_MAP:
        if keyword in query.lower():
            break
    else:
        if violates_policy_llm(query):
            return {"text": "Query blocked due to policy.", "image_url": None}

    if is_greeting_or_vague_llm(query):
        return {"text": vague_query_response(), "image_url": None}

    docs = vectorstore.similarity_search(query, k=4)
    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are an expert assistant for the Krupal Habitat and Dholera. The context provided can be used to answer the question and also use your knowledge if context is not clear to you.
Be polite, helpful, and persuasive. Sound human-like. Do not sound dejected. Keep it under 5 sentences. Display in tabular form wherever necessary.

RULES:
1. If the question relates to a specific room or location that has an image available (e.g., bedroom, house, dining room, living room), always end your answer with:
IMAGE: <room name>
Use only one image tag. Do not say things like "I don't have access to photos."

2. The available image keys are:
{', '.join(IMAGE_MAP.keys())}

3. Keep your answers under 5 sentences.

Context:
{context}

User Question:
{query}

Answer:
"""

    response_text = model.generate_content(prompt).text.strip()

    image_url = None
    for line in response_text.splitlines():
        if line.strip().startswith("IMAGE:"):
            room = line.split("IMAGE:")[1].strip().lower()
            image_url = IMAGE_MAP.get(room)
            response_text = response_text.replace(line, "").strip()
            break

    if violates_policy_llm(response_text):
        return {"text": "Response blocked due to policy.", "image_url": None}

    # print(f"user: {query}", f"response: {response_text}", f"image_url: {image_url}")
    return {"text": response_text, "image_url": image_url}

# ----------------- Async wrapper ------------------

async def fetch_response(query: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _fetch_response_sync, query)

# ----------------- Streamlit App ------------------

st.set_page_config(page_title="Krupal Habitat Chatbot", layout="centered")
st.title("🏡 Krupal Habitat Chatbot")

query = st.text_input("Ask your question:")

if query:
    # Since Streamlit doesn't support async directly, use sync fetch
    result = asyncio.run(fetch_response(query))
    st.markdown(result["text"])
    if result["image_url"]:
        st.image(result["image_url"], use_container_width=True)
