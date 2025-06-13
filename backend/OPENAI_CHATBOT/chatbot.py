import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4.1-mini"

if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = ConversationBufferMemory(return_messages=True)

llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0, openai_api_key=OPENAI_API_KEY)
embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)


vectorstore = FAISS.load_local(
    "krupaldb_faiss", embedding, allow_dangerous_deserialization=True
)


IMAGE_MAP = {
    "bedroom": "images/bedroom.jpeg",
    "house": "images/house.jpeg",
    "clubhouse": "images/clubhouse.jpeg",
    "krupal habitat": "images/krupalhabitat",
}


def ask_llm(prompt: str) -> str:
    history = st.session_state.chat_memory.load_memory_variables({})["history"]
    response = llm.invoke(history + [HumanMessage(content=prompt)])
    st.session_state.chat_memory.chat_memory.add_user_message(prompt)
    st.session_state.chat_memory.chat_memory.add_ai_message(response.content)
    return response.content.strip()


def violates_policy_llm(text: str):
    prompt = f"""
You are a content filter. Check if the following text contains any references to religion, sex, politics, terrorism, violence, or drugs.

Text: "{text}"

If it violates, reply only with "BLOCK". Otherwise, reply only with "ALLOW".
"""
    return ask_llm(prompt).upper() == "BLOCK"


def is_greeting_or_vague_llm(text: str):
    prompt = f"""
Classify the user's message. If it's a greeting or vague unrelated message like "hi", "hello", "good morning", "how are you", or anything that doesn't ask about the project, respond with "GREETING". Otherwise respond with "QUERY".

Message: "{text}"
Category:"""
    return ask_llm(prompt).upper() == "GREETING"


def vague_query_response():
    return "Hi! I’m your smart assistant. Ask me anything about Krupal Habitat."


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
You are a confident, human-like, and persuasive **real estate sales agent** for *Krupal Habitat* — a premium plotting project located in **Dholera, Gujarat**. Your job is to help clients understand the opportunity and **convince them** why investing in Krupal Habitat is smart and future-focused.

Answer the user's question by following these rules:

🏙️ **Dholera-related Questions**
1. Use your general knowledge to answer any question about Dholera (e.g., development, investment potential, connectivity, infrastructure).
2. If the question involves health or civic facilities without naming Krupal Habitat, assume it refers to Dholera.

📐 **Krupal Habitat-specific Questions**
3. Use the provided CONTEXT below to answer anything about Krupal Habitat (e.g., plots, pricing, layout, amenities).
4. Always position the project as high-value and professionally developed.

💰 **Pricing & Plot Size**
5. Plot sizes must be given in **sq yards** and rounded to the nearest 10 (e.g., 269.99 → 270).
6. Pricing should always include both:
   - Base Sale Price (BSP) per sq yard
   - Development Charges (fixed ₹1500 per sq yard)
7. For cost queries, calculate **total cost** as:
   `Total = (area × BSP) + (area × development)`
8. Respond with **both Pre-Launch and Launch phase** pricing:
   - Pre-Launch: ₹6,500 + ₹1,500
   - Launch: ₹8,500 + ₹1,500
9. Show a clear price **breakdown**: BSP, Dev Charges, Total — for both phases.

🏠 **Layout & Amenities**
10. If asked about **layout**, mention structural elements: entrance gate, internal roads, street lights, drainage, and power supply.
11. If asked about **amenities**, highlight features like clubhouse, swimming pool, parks, and other community offerings.
12. Layout and amenities are different — explain both if asked.

📄 **Legal & Sales**
13. Always mention that **all legal documents are available** for review.
14. Never say "I don’t know" — instead, offer to connect them to the sales team (which is you).

🖼️ **Images**
15. If the query mentions one of these: {', '.join(IMAGE_MAP.keys())}, end your answer with:
   `IMAGE: <room name>`

🧠 **Tone & Limits**
16. Always be helpful, confident, and proactive — like a top-performing sales executive.
17. Keep answers under **5 sentences** unless bullet points make it clearer.

---

CONTEXT (from Krupal Habitat project):
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


st.set_page_config(page_title="Krupal Habitat Chatbot", layout="centered")
st.title("🏡 Krupal Habitat Chatbot")

query = st.text_input("Ask your question:")

if st.button("🔁 Reset Conversation"):
    st.session_state.chat_memory = ConversationBufferMemory(return_messages=True)
    st.rerun()


if query:
    result = fetch_response(query)
    st.markdown(result["text"])
    if result["image_url"]:
        st.image(result["image_url"], use_container_width=True)
