import os
from dotenv import load_dotenv
from collections import deque
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.vectorstores import FAISS

# ──────────────────────────────────────────────────────────────────────────────
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"

llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0, openai_api_key=OPENAI_API_KEY)
embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# ──────────────────────────────────────────────────────────────────────────────
# Prompt templates – note the placeholder *{image_keywords}*
# (Repeats trimmed for brevity; keep yours exactly as required.)

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
   Also mention preferable location charges and amount paid to be on time of booking and other things in context
   Preferential location charges = 10% of BSP(for corner and park facing plots)
    Payment Plan:
    On time of booking : 10% of BSP

    On executing BBA : 20% of BSP

    On land registry of unit : 70% BSP + Extra charges


8. Respond with 
    ₹8,000 + ₹1,500
9. Show a clear price **breakdown**: BSP, Dev Charges, Total — for both phases.

🏠 **Layout & Amenities**
10. If asked about **layout**, mention structural elements: entrance gate, internal roads, street lights, drainage, and power supply.
11. If asked about **amenities**, highlight features like clubhouse, swimming pool, parks, and other community offerings.
12. Layout and amenities are different — explain both if asked.

📄 **Legal & Sales**
13. Always mention that **all legal documents are available** for review.
14. Never say "I don’t know" — instead, offer to connect them to the sales team (which is you).



🧠 **Tone & Limits**
16. Always be helpful, confident, and proactive — like a top-performing sales executive.
17. Keep answers under **5 sentences** unless bullet points make it clearer.

---

If the query mentions one of these: {image_keywords}, end your answer with:
IMAGE: <room name>


CONTEXT:
{context}

USER:
{query}

ANSWER:
"""

RAMVAN_PROMPT = """
You are a sales executive for *Ramvan Villas* in Ramnagar.You are a persuasive, confident, and friendly **real estate sales executive** for **Ramvan Villas** — a premium gated residential project in **Ramnagar, Uttarakhand**, near Jim Corbett National Park.

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




If the query mentions one of these: {image_keywords}, end your answer with:
IMAGE: <room name>


CONTEXT:
{context}

USER:
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

If the query mentions one of these: {image_keywords}, end your answer with:
IMAGE: <room name>

CONTEXT:
{context}

USER:
{query}

ANSWER:
"""


# ──────────────────────────────────────────────────────────────────────────────
def _project_cfg(name: str):
    if name == "Krupal Habitat":
        return dict(
            vector=FAISS.load_local(
                "krupaldb_faiss", embedding, allow_dangerous_deserialization=True
            ),
            images={
                "bedroom": "images_krupal/bedroom.jpeg",
                "house": "images_krupal/house.jpeg",
                "clubhouse": "images_krupal/clubhouse.jpeg",
                "krupal habitat": "images_krupal/krupalhabitat",
            },
            tpl=KRUPAL_PROMPT,
        )
    if name == "Ramvan Villas":
        return dict(
            vector=FAISS.load_local(
                "ramvan_villas_faiss", embedding, allow_dangerous_deserialization=True
            ),
            images={
                "bedroom": "images_ramvan/bedroom.jpeg",
                "living room": "images_ramvan/livingroom.jpeg",
                "dining room": "images_ramvan/dining.jpeg",
                "villa": "images_ramvan/house.jpeg",
                "kitchen": "images_ramvan/kitchen.jpeg",
            },
            tpl=RAMVAN_PROMPT,
        )
    if name == "Firefly Homes":
        return dict(
            vector=FAISS.load_local(
                "firefly_faiss", embedding, allow_dangerous_deserialization=True
            ),
            images={
                "clubhouse": "https://res.cloudinary.com/dqlrfkgt0/image/upload/v1749902620/clubhouse_og4dc2.jpg"
            },
            tpl=FIREFLY_PROMPT,
        )
    raise ValueError("Unknown project")


# ──────────────────────────────────────────────────────────────────────────────
# tiny helper for LLM calls with explicit history
def _ask_llm(prompt: str, history: list[dict]):
    messages = []
    for h in history:
        if h["role"] == "user":
            messages.append(HumanMessage(content=h["content"]))
        else:
            messages.append(AIMessage(content=h["content"]))
    messages.append(HumanMessage(content=prompt))

    return llm.invoke(messages).content.strip()

    # wrapper filters -------------------------------------------------------------
    # def _violates_policy(text: str, history):
    pol_prompt = f"""You are a content-filter. Reply ONLY "BLOCK" or "ALLOW".
Text: "{text}" """
    return _ask_llm(pol_prompt, history).upper() == "BLOCK"


def _is_greeting(text: str, history):
    g_prompt = (
        f"""Reply "GREETING" if "{text}" is just a greeting/ vague, else "QUERY":"""
    )
    return _ask_llm(g_prompt, history).upper() == "GREETING"


# ──────────────────────────────────────────────────────────────────────────────
def generate_response(project: str, history: list[dict]):
    """
    history: full chat so far, *last item must be the latest USER msg*.
    Returns {text:str, image_url:str|None}
    """
    cfg = _project_cfg(project)
    user_input = history[-1]["content"]

    # 1 early exits -----------------------------------------------------------
    if _is_greeting(user_input, history):
        return dict(
            text=f"Hi! I'm your assistant for {project}. Ask me anything!",
            image_url=None,
        )
    # if _violates_policy(user_input, history):
    # return dict(text="Query blocked due to policy.", image_url=None)

    # 2 vector context --------------------------------------------------------
    docs = cfg["vector"].similarity_search(user_input, k=5)
    context = "\n".join(d.page_content for d in docs)

    # 3 main prompt -----------------------------------------------------------
    prompt = cfg["tpl"].format(
        context=context,
        query=user_input,
        image_keywords=", ".join(cfg["images"].keys()),
    )
    answer = _ask_llm(prompt, history)

    # 4 policy check on answer ------------------------------------------------
    # if _violates_policy(answer, history):
    # return dict(text="Response blocked due to policy.", image_url=None)

    # 5 optional image tag parsing -------------------------------------------
    img_url = None
    for line in answer.splitlines():
        if line.strip().lower().startswith("image:"):
            keyword = line.split("image:")[1].strip().lower()
            img_url = cfg["images"].get(keyword)
            answer = answer.replace(line, "").strip()
            break

    return dict(text=answer, image_url=img_url)
