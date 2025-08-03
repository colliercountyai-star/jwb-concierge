import streamlit as st
import json
import random
import re
from openai import OpenAI

# Load data
with open("jwb_grouped_menu_final_with_chicken.json") as f:
    grouped_menu = json.load(f)

with open("wine_list.json") as f:
    wine_list = json.load(f)

with open("beverage_menu.json") as f:
    beverage_menu = json.load(f)

with open("prompt_template.txt") as f:
    system_prompt = f.read()

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Prepare menu context
food_context = []
for category, items in grouped_menu.items():
    food_context.append(f"{category}:")
    food_context.extend([f"- {item['name']} (${item['price']})" for item in items])
context_string = "\n".join(food_context)

wine_context = "\n".join([f"{wine['name']} ({wine['type']} - {wine.get('region', 'N/A')})" for wine in wine_list])
bev_context = "\n".join([f"{bev['name']} ({bev['type']})" for bev in beverage_menu])

combined_context = f"{context_string}\n\nWines:\n{wine_context}\n\nBeverages:\n{bev_context}"

# Prompts
greeting_prompts = [
    "Let’s find you something worth writing home (or Instagramming) about.",
    "Hungry? Thirsty? Lost in a sea of steak and seafood? I’ve got you.",
    "I’m your island insider—think of me as the flip-flop version of a maître d'.",
    "You bring the appetite, I’ll bring the flavor map.",
    "Tell me what you're craving and I’ll make sure your tastebuds get a front-row seat to paradise."
]

follow_up_prompts = [
    "Gotcha—what else can I help with?",
    "Need dessert? A drink? Just say the word.",
    "I’ve got your back. Want to explore something new?",
    "Let’s keep going. What else sounds good?",
    "I’m here for you. More recs? Just ask."
]

# Utility
def extract_allergies(text):
    allergies = []
    known_allergens = ["gluten", "dairy", "peanut", "tree nut", "nuts"]
    for allergen in known_allergens:
        if re.search(rf"\bno\s+{allergen}\b|\b{allergen}-free\b", text, re.IGNORECASE):
            if allergen == "nuts":
                allergies.extend(["peanut", "tree nut"])
            else:
                allergies.append(allergen)
    return list(set(allergies))

def extract_protein(text):
    proteins = ["seafood", "steak", "chicken", "vegan", "vegetarian"]
    for protein in proteins:
        if re.search(rf"\b{protein}\b", text, re.IGNORECASE):
            return protein
    return "seafood"

def chat_with_ai(message, context):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{message}\nFood Context: {context}"}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=history
    )
    return response.choices[0].message.content

# Streamlit UI
st.set_page_config(page_title="JWB Grill Concierge", page_icon="🍤", layout="centered")

st.title("🍽️ JWB Grill Concierge")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.first_greeting = random.choice(greeting_prompts)

# Show chat history
for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Input from user
if prompt := st.chat_input(st.session_state.first_greeting if len(st.session_state.chat_history) == 0 else random.choice(follow_up_prompts)):
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    detected_allergies = extract_allergies(prompt)
    detected_protein = extract_protein(prompt)

    # Inject system prompt and context once
if len(st.session_state.chat_history) == 1:
    st.session_state.chat_history.insert(0, {"role": "system", "content": f"{system_prompt}\n\n{combined_context}"})
ai_reply = chat_with_ai(st.session_state.chat_history)
    st.chat_message("assistant").markdown(ai_reply)
    st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
