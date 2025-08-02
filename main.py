import json
import re
import random
from openai import OpenAI

# Load menu and beverage data
with open("jwb_grouped_menu_final_with_chicken.json") as f:
    grouped_menu = json.load(f)

with open("wine_list.json") as f:
    wine_list = json.load(f)

with open("beverage_menu.json") as f:
    beverage_menu = json.load(f)

with open("prompt_template.txt") as f:
    system_prompt = f.read()

client = OpenAI(api_key="sk-your-key-here")

# Witty first-time greetings
greeting_prompts = [
    "Let’s find you something worth writing home (or Instagramming) about.",
    "Hungry? Thirsty? Lost in a sea of steak and seafood? I’ve got you.",
    "I’m your island insider—think of me as the flip-flop version of a maître d'.",
    "You bring the appetite, I’ll bring the flavor map.",
    "Tell me what you're craving and I’ll make sure your tastebuds get a front-row seat to paradise."
]

# Supportive follow-ups that feel like a friend helping you out
follow_up_prompts = [
    "Gotcha—what else can I help with?",
    "Need dessert? A drink? Just say the word.",
    "I’ve got your back. Want to explore something new?",
    "Let’s keep going. What else sounds good?",
    "I’m here for you. More recs? Just ask."
]

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

def get_filtered_menu(grouped_menu, protein, allergies):
    all_items = []
    for category in grouped_menu:
        all_items.extend(grouped_menu[category])
    filtered = []
    for item in all_items:
        if all(allergen + "-free" in item.get("tags", []) or "customize-no-" + allergen in item.get("tags", []) for allergen in allergies):
            if protein.lower() in item["name"].lower() or protein in item.get("tags", []):
                filtered.append(item)
    return filtered

def chat_with_ai(message, context):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{message}\nFood Context: {context}"}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content

# Prepare context once at start
food_context = []
for category, items in grouped_menu.items():
    food_context.append(f"{category}:")
    food_context.extend([f"- {item['name']} (${item['price']})" for item in items])
context_string = "\n".join(food_context)

wine_context = "\n".join([f"{wine['name']} ({wine['type']} - {wine.get('region', 'N/A')})" for wine in wine_list])
bev_context = "\n".join([f"{bev['name']} ({bev['type']})" for bev in beverage_menu])

combined_context = f"{context_string}\n\nWines:\n{wine_context}\n\nBeverages:\n{bev_context}"

# Start interaction
print("Welcome to the JWB Grill dining concierge. Type 'exit' to end.\n")
first_time = True

while True:
    prompt = random.choice(greeting_prompts) if first_time else random.choice(follow_up_prompts)
    user_input = input(f"{prompt}\n> ")
    if user_input.strip().lower() == "exit":
        print("Thanks for visiting JWB Grill! Hope to see you soon 🌴")
        break

    detected_allergies = extract_allergies(user_input)
    detected_protein = extract_protein(user_input)

    print(f"Parsed allergies: {detected_allergies}")
    print(f"Parsed protein: {detected_protein}")

    ai_response = chat_with_ai(user_input, combined_context)
    print("\nAI Concierge Says:\n" + ai_response + "\n")

    first_time = False
