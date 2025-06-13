import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage
import os
from dotenv import load_dotenv

load_dotenv()


# === Load API Key ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4.1-mini"

# === Initialize memory ===
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = ConversationBufferMemory(return_messages=True)

# === LLM and Embeddings ===
llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0, openai_api_key=OPENAI_API_KEY)
embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# === Load vector database ===
vectorstore = FAISS.load_local(
    "ramvan_villas_faiss", embedding, allow_dangerous_deserialization=True
)

# === Optional image mapping ===
IMAGE_MAP = {
    "bedroom": "images/bedroom.jpeg",
    "living room": "images/livingroom.jpeg",
    "dining room": "images/bedroom.jpeg",
    "villa": "images/house.jpeg",
    "kitchen": "images/kitchen.jpeg",
}


# === Chat with memory ===
def ask_llm(prompt: str) -> str:
    history = st.session_state.chat_memory.load_memory_variables({})["history"]
    response = llm.invoke(history + [HumanMessage(content=prompt)])
    st.session_state.chat_memory.chat_memory.add_user_message(prompt)
    st.session_state.chat_memory.chat_memory.add_ai_message(response.content)
    return response.content.strip()


# === Guardrails ===
def violates_policy_llm(text: str):
    prompt = f"""You are a content filter. Check if the following text contains any references to religion, sex, politics, terrorism, violence, or drugs.

Text: "{text}"

If it violates, reply only with "BLOCK". Otherwise, reply only with "ALLOW"."""
    return ask_llm(prompt).upper() == "BLOCK"


def is_greeting_or_vague_llm(text: str):
    prompt = f"""Classify the user's message. If it's a greeting or vague unrelated message like "hi", "hello", "good morning", "how are you", or anything that doesn't ask about the project, respond with "GREETING". Otherwise respond with "QUERY".

Message: "{text}"
Category:"""
    return ask_llm(prompt).upper() == "GREETING"


def vague_query_response():
    return "Hello! I'm your smart sales assistant. Ask me anything about Ramvan Villas in Ramnagar."


# === Main logic ===
def fetch_response(query: str):
    for keyword in IMAGE_MAP:
        if keyword in query.lower():
            break
    else:
        if violates_policy_llm(query):
            return {"text": "Query blocked due to policy.", "image_url": None}

    if is_greeting_or_vague_llm(query):
        return {"text": vague_query_response(), "image_url": None}

    docs = vectorstore.similarity_search(query, k=5)
    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are a persuasive, confident, and friendly **real estate sales executive** for **Ramvan Villas** — a premium gated residential project in **Ramnagar, Uttarakhand**, near Jim Corbett National Park.

Follow these rules when responding:

for any questions on ramnagar use your own knowledge

 **Location & Investment Highlights**
- Emphasize tourism growth, proximity to Jim Corbett, rising land value, and infrastructure.
- Mention circle rates doubled in 1.5 years and nearby attractions (Garjiya Temple, Kosi River, Pantnagar Airport, NH-309, etc.)

 **Plot & Construction Details**
- Plot: 250 sq yards (2250 sq ft), 75% built-up, up to 3 floors
- Possession by Dec 2025, gated community, 24x7 security, water, underground wiring

 **Pricing**
- ₹1800/sq ft → ₹40,50,000 (negotiable)
- 🎉 **Pre-launch offer**: ₹5,00,000 discount on registry (valid until August end)
- Charges:
  - Infra Dev: ₹50/sq ft
  - Clubhouse: ₹100/sq ft
  - Corner plot: +10%
- Payment Plan:
  - 10% on Booking = ₹4,05,000
  - 20% on BBA = ₹8,10,000
  - 70% on Registry = ₹28,35,000 + extras
- Construction: ₹1200–₹1500/sq ft
- Interiors: ₹1000/sq ft

 **Villa & Amenities**
- Features: 2BHK, smart TVs, fireplace, designer interiors
- Clubhouse: pool, indoor games, conference room, restaurant
- Layout = infrastructure (roads, drainage), Amenities = experience (clubhouse, parks)

 **Legal**
- NA land, Section 143 cleared, Title clear
- All legal documents available for review

**Developer Track Record**
- Harit Vatika (Jewar)
- Firefly Homes (Lansdowne)
- Krupal Habitat (Dholera)

**Tone**
- You're the sales agent: sound confident, helpful, and close the deal
- Never say “I don’t know” — always guide or offer assistance
- Use bullet points and stay under 5 sentences if possible

**Images**
If any of these are mentioned: {', '.join(IMAGE_MAP.keys())}, add:
IMAGE: <room name>

CONTEXT:
{context}

USER QUESTION:
{query}

ANSWER:
"""

    response_text = ask_llm(prompt)

    image_url = None
    for line in response_text.splitlines():
        if line.strip().startswith("IMAGE:"):
            room = line.split("IMAGE:")[1].strip().lower()
            image_url = IMAGE_MAP.get(room)
            response_text = response_text.replace(line, "").strip()
            break

    if violates_policy_llm(response_text):
        return {"text": "Response blocked due to policy.", "image_url": None}

    return {"text": response_text, "image_url": image_url}


# === Streamlit Interface ===
st.set_page_config(page_title="Ramvan Villas Chatbot", layout="centered")
st.title("🏡 Ramvan Villas Chatbot")

query = st.text_input("Ask your question:")

if st.button("🔁 Reset Conversation"):
    st.session_state.chat_memory = ConversationBufferMemory(return_messages=True)
    st.rerun()

if query:
    result = fetch_response(query)
    st.markdown(result["text"])
    if result["image_url"]:
        st.image(result["image_url"], use_container_width=True)
