import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage
from langchain.schema import AIMessage
from langchain.memory import ConversationBufferMemory
from collections import deque

# Load env vars
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4.1-mini"

# Shared LLM and Embeddings
llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0, openai_api_key=OPENAI_API_KEY)
embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# In-memory store for session memory (per-user)
MEMORY_STORE = {}


def get_user_memory(user_id):
    if user_id not in MEMORY_STORE:
        MEMORY_STORE[user_id] = deque(maxlen=20)
    return MEMORY_STORE[user_id]


# Prompt templates
KRUPAL_PROMPT = """
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
RAMVAN_PROMPT = """
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
FIREFLY_PROMPT = """
You are a helpful and friendly real estate sales agent for **Firefly Homes**, a premium residential project in Lansdowne, Uttarakhand.

Always answer based on the provided context. If users ask general questions about Lansdowne or Uttarakhand, use your knowledge.

🏡 **Project Details**
- Scenic location in Lansdowne
- AQI 25–30, clean air, lush greenery
- Modern infrastructure: internet, mobile, roads
- Nearby: Sona River, Corbett Safari, War Memorial, Bulla Lake, Tarkeshwar Dham

 **Project Amenities**
- Gated community, 24x7 security, CCTV
- Café & restaurant, clubhouse, kids' area
- Well-furnished rooms: living room, bedroom, modular kitchen, en-suites

🧠 **Tone**
- Confident, clear, and persuasive — like a top real estate sales rep
- Never say "I don’t know", always offer help
- Use bullet points where needed and keep it short (max 5 sentences)

🖼️ **Images**
If any of these are mentioned: {keywords}, add:
IMAGE: <room name>

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:

"""


# Project configuration loader
def get_project_config(project_name):
    if project_name == "Krupal Habitat":
        return {
            "vectorstore": FAISS.load_local(
                "krupaldb_faiss", embedding, allow_dangerous_deserialization=True
            ),
            "image_map": {
                "bedroom": "images_krupal/bedroom.jpeg",
                "house": "images_krupal/house.jpeg",
                "clubhouse": "images_krupal/clubhouse.jpeg",
                "krupal habitat": "images_krupal/krupalhabitat",
            },
            "prompt_template": KRUPAL_PROMPT,
        }
    elif project_name == "Ramvan Villas":
        return {
            "vectorstore": FAISS.load_local(
                "ramvan_villas_faiss", embedding, allow_dangerous_deserialization=True
            ),
            "image_map": {
                "bedroom": "images_ramvan/bedroom.jpeg",
                "living room": "images_ramvan/livingroom.jpeg",
                "dining room": "images_ramvan/bedroom.jpeg",
                "villa": "images_ramvan/house.jpeg",
                "kitchen": "images_ramvan/kitchen.jpeg",
            },
            "prompt_template": RAMVAN_PROMPT,
        }
    elif project_name == "Firefly Homes":
        return {
            "vectorstore": FAISS.load_local(
                "firefly_faiss", embedding, allow_dangerous_deserialization=True
            ),
            "image_map": {"clunhouse": "firefly_images/clunhouse.jpg"},
            "prompt_template": FIREFLY_PROMPT,
        }
    else:
        raise ValueError("Unknown project selected")


# LLM invocation
def ask_llm(prompt, memory_deque):
    messages = list(memory_deque) + [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    memory_deque.append(HumanMessage(content=prompt))
    memory_deque.append(AIMessage(content=response.content))
    return response.content.strip()


# Policy filter
def violates_policy_llm(text, memory):
    prompt = f"""
You are a content filter. Check if the following text contains any references to religion, sex, politics, terrorism, violence, or drugs.

Text: "{text}"

If it violates, reply only with "BLOCK". Otherwise, reply only with "ALLOW".
"""
    return ask_llm(prompt, memory).upper() == "BLOCK"


# Greeting/vague detection
def is_greeting_or_vague_llm(text, memory):
    prompt = f"""
Classify the user's message. If it's a greeting or vague unrelated message like "hi", "hello", "good morning", or anything not about the project, respond with "GREETING". Otherwise respond with "QUERY".

Message: "{text}"
Category:"""
    return ask_llm(prompt, memory).upper() == "GREETING"


# Main function to respond to message
def get_chat_response(user_id, project_name, user_input):
    config = get_project_config(project_name)
    memory = get_user_memory(user_id)
    vectorstore = config["vectorstore"]
    image_map = config["image_map"]
    base_prompt = config["prompt_template"]

    if is_greeting_or_vague_llm(user_input, memory):
        return {
            "text": f"Hi! I'm your assistant for {project_name}. Ask me anything.",
            "image_url": None,
        }

    if violates_policy_llm(user_input, memory):
        return {"text": "Query blocked due to policy.", "image_url": None}

    docs = vectorstore.similarity_search(user_input, k=5)
    context = "\n".join([doc.page_content for doc in docs])

    prompt = base_prompt.format(
        context=context, query=user_input, image_keywords=", ".join(image_map.keys())
    )
    response_text = ask_llm(prompt, memory)

    image_url = None
    for line in response_text.splitlines():
        if line.strip().startswith("IMAGE:"):
            keyword = line.split("IMAGE:")[1].strip().lower()
            image_url = image_map.get(keyword)
            response_text = response_text.replace(line, "").strip()
            break

    if violates_policy_llm(response_text, memory):
        return {"text": "Response blocked due to policy.", "image_url": None}

    return {"text": response_text, "image_url": image_url}
