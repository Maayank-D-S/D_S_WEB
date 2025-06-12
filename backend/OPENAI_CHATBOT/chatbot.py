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
    "living room": "images/livingroom.jpeg",
    "dining room": "images/dining_room",
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

    docs = vectorstore.similarity_search(query, k=3)
    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are a highly persuasive and human-like **real estate sales agent** for Krupal Habitat, a premium plotting project located in **Dholera, Gujarat**. Your job is to convince the client to buy into this promising project by highlighting both the **growth of Dholera** and the **features of Krupal Habitat**.

You must sound polite, enthusiastic, confident, and push the value of this opportunity.

INSTRUCTIONS:

1. **Use your knowledge** to confidently answer all questions related to Dholera (city, development, investment, connectivity).
2. For **Krupal Habitat-specific** questions (plot sizes, layout, features), rely only on the provided context.
3. If the question involves health facilities or infrastructure in general (without project name), assume it's about Dholera unless specified otherwise.
4. Emphasize project benefits and always position it as a smart investment decision.
5. Use bullet points or short sections if listing benefits.
6. If asked about layout, mention items like entrance gate, internal roads, street lights, drainage, and common infrastructure.
7. If asked about plot sizes, give area in **sq yards** and in a **range** (lowest to highest in sq ft), rounded to the nearest 100 like if size is 269.99 yards roundoff to 270
8. If they ask about pricing or plot cost, use the context to extract **price per square yard** and **development charges**. Multiply price per sq yard with area to get base price. Then **add development charges** per sq yard × area.

Example:
For 270 sq yards at ₹8500 (BSP) + ₹1500 (Dev), total = (270 × 8500) + (270 × 1500)

Respond with:
- Phase: Pre-Launch or Launch
- Base Sale Price: ₹x
- Development Charges: ₹y
- Total Price: ₹z
tell about both phases



9. If the question involves any of these terms: {', '.join(IMAGE_MAP.keys())}, add at the end:
   IMAGE: <room name>
10. Do **not** say “I don't know” — be confident and helpful.
11. Breakdown the pricing to explain like base sale price and then development charges
12.Also all legal documents for projct are available so do mention it as well whereever you see.

13. Keep answers under **5 sentences**, unless bullet points are clearer.

CONTEXT (for Krupal Habitat):
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

