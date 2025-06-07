import streamlit as st
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_ollama.embeddings import OllamaEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

# loading gemini model
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# importing the database
embedding = OllamaEmbeddings(model="mistral")
vectorstore = FAISS.load_local(
    "krupal_faiss", embedding, allow_dangerous_deserialization=True
)

# image urls to display images
IMAGE_MAP = {
    "bedroom": "images/bedroom.jpeg",
    "house": "images/house.jpeg",
    "living room": "images/livingroom.jpeg",
    "dining room": "images/dining_room",
}


# guardrails
def violates_policy_llm(text: str):
    prompt = f"""
You are a content filter. Check if the following text contains any references to religion, sex, politics, terrorism, violence, or drugs.

Text: "{text}"

If it violates, reply only with "BLOCK". Otherwise, reply only with "ALLOW".
"""
    result = model.generate_content(prompt).text.strip().upper()
    return result == "BLOCK"


# for queries like hi or other vague queries
def is_greeting_or_vague_llm(text: str):
    prompt = f"""
Classify the user's message. If it's a greeting or vague unrelated message like "hi", "hello", "good morning", "how are you", or anything that doesn't ask about the project, respond with "GREETING". Otherwise respond with "QUERY".

Message: "{text}"
Category:"""
    result = model.generate_content(prompt).text.strip().upper()
    return result == "GREETING"


# greeting response
def vague_query_response():
    return "Hi! I’m your smart assistant. Ask me anything about Krupal Habitat."


# main response function for project queries
def fetch_response(query: str):
    # Step 1: Bypass filter for known image-related terms
    for keyword in IMAGE_MAP:
        if keyword in query.lower():
            break  # allow known keywords to proceed
    else:
        if violates_policy_llm(query):
            return {"text": "Query blocked due to policy.", "image_url": None}

    if is_greeting_or_vague_llm(query):
        return {"text": vague_query_response(), "image_url": None}

    docs = vectorstore.similarity_search(query, k=4)
    context = "\n".join([doc.page_content for doc in docs])

    # main prompt feeded to llm
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

    # for  detecting image query
    image_url = None
    for line in response_text.splitlines():
        if line.strip().startswith("IMAGE:"):
            room = line.split("IMAGE:")[1].strip().lower()
            image_url = IMAGE_MAP.get(room)
            response_text = response_text.replace(line, "").strip()
            break

    # classify guardrails
    if violates_policy_llm(response_text):
        return {"text": "Response blocked due to policy.", "image_url": None}

    return {"text": response_text, "image_url": image_url}


# streamlit to display image run on local host
st.set_page_config(page_title="Krupal Habitat Chatbot", layout="centered")
st.title("🏡 Krupal Habitat Chatbot")

query = st.text_input("Ask your question:")

if query:
    result = fetch_response(query)
    st.markdown(result["text"])
    if result["image_url"]:
        st.image(result["image_url"], use_container_width=True)
# to run cmd -- streamlit run chatbot.py
