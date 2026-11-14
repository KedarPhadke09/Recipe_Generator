import streamlit as st
st.set_page_config(page_title="AI Recipe Generator", page_icon="🍳", layout="wide")

import os

def get_secret(name):
    try:
        return st.secrets[name]
    except Exception:
        return os.environ.get(name)

import os, io, json, random, urllib.parse
import requests
from PIL import Image
from groq import Groq

client = Groq(api_key=get_secret("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-120b"   # llama-3.3-70b-versatile was retired by Groq

def ask_llm(system_prompt, user_prompt, json_mode=False, temperature=0.6):
    kwargs = dict(model=MODEL, temperature=temperature,
                  messages=[{"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}])
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    return client.chat.completions.create(**kwargs).choices[0].message.content

def ask_json(system_prompt, user_prompt, temperature=0.4, retries=2):
    # Retry if the model returns invalid JSON
    for attempt in range(retries + 1):
        try:
            return json.loads(ask_llm(system_prompt, user_prompt, json_mode=True, temperature=temperature))
        except json.JSONDecodeError:
            if attempt == retries:
                raise

def ingredient_analyzer(raw):
    system = ("You are an ingredient analysis expert. Respond ONLY with valid JSON with keys: "
              "'clean_ingredients' (list), 'categories' (dict ingredient -> vegetable/dairy/grain/protein/spice/other), "
              "'cuisine_suggestion' (string), 'missing_basics' (list of common pantry items like oil, salt).")
    return ask_json(system, f"Ingredients: {raw}", temperature=0.2)

def recipe_generator(analysis, diet="Any"):
    system = ("You are a creative professional chef. Create ONE recipe using the given ingredients, "
              f"following this dietary preference: {diet}. Respond ONLY with valid JSON with keys: "
              "'recipe_name' (string), 'ingredients' (list of strings with quantities, serves 2), "
              "'steps' (list of clear steps), 'cook_time_minutes' (number).")
    return ask_json(system, f"Analysis: {json.dumps(analysis)}")

def nutrition_advisor(recipe):
    system = ("You are a nutritionist. Estimate nutrition per serving (recipe serves 2). Respond ONLY with valid JSON: "
              "'calories_per_serving', 'protein_g', 'carbs_g', 'fat_g' (numbers), 'health_note' (one short sentence).")
    return ask_json(system, f"Recipe: {json.dumps(recipe)}", temperature=0.2)

def cooking_tips_generator(recipe):
    system = "You are a head chef. Give 3 to 4 short practical tips. Respond ONLY with JSON: {\"tips\": [strings]}."
    return ask_json(system, f"Recipe: {json.dumps(recipe)}")["tips"]

def image_prompt_agent(recipe):
    system = ("You write prompts for an AI image generator. Write ONE vivid prompt (max 60 words) for a professional "
              "food photograph of the finished dish: plated, natural light, shallow depth of field, appetizing, "
              "top-down or 45-degree angle. Output only the prompt text.")
    return ask_llm(system, f"Dish: {recipe['recipe_name']}. Ingredients: {', '.join(recipe['ingredients'])}", temperature=0.7).strip()

def generate_image(prompt):
    # 1) Pollinations: free, no API key
    try:
        url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
               + f"?width=768&height=768&nologo=true&seed={random.randint(1, 99999)}")
        r = requests.get(url, timeout=90)
        r.raise_for_status()
        return Image.open(io.BytesIO(r.content)), None
    except Exception as e:
        err = f"Pollinations failed ({e})"
    # 2) Fallback: Hugging Face FLUX (needs HF_TOKEN secret)
    try:
        from huggingface_hub import InferenceClient
        hf = InferenceClient(token=get_secret("HF_TOKEN"))
        return hf.text_to_image(prompt, model="black-forest-labs/FLUX.1-schnell"), None
    except Exception as e:
        return None, f"{err}; Hugging Face fallback failed ({e})"


# ---------------- UI ----------------
st.title("🍳 AI Recipe Generator")
st.caption("Tell me what's in your kitchen. Five AI agents will plan, check and photograph your dish.")

with st.sidebar:
    st.header("🥕 Your kitchen")
    ingredients = st.text_area("Available ingredients (comma separated)", placeholder="Tomato, Onion, Paneer, Capsicum", height=100)
    diet = st.selectbox("🥗 Dietary preference", ["Any", "Vegetarian", "Vegan", "High-protein", "Low-calorie", "Jain"])
    make_image = st.checkbox("🎨 Generate dish image", value=True)
    go = st.button("✨ Generate Recipe", type="primary", use_container_width=True)

if go:
    if not ingredients.strip():
        st.warning("Please enter at least one ingredient.")
    else:
        try:
            with st.status("Cooking up your recipe...", expanded=True) as status:
                st.write("🔎 Analyzing ingredients...")
                analysis = ingredient_analyzer(ingredients)
                st.write("👨‍🍳 Creating recipe...")
                recipe = recipe_generator(analysis, diet)
                st.write("🥗 Calculating nutrition...")
                nutrition = nutrition_advisor(recipe)
                st.write("💡 Gathering chef tips...")
                tips = cooking_tips_generator(recipe)
                image, img_err = None, None
                if make_image:
                    st.write("🎨 Painting your dish...")
                    image, img_err = generate_image(image_prompt_agent(recipe))
                status.update(label="Done!", state="complete", expanded=False)
            st.session_state["result"] = dict(analysis=analysis, recipe=recipe, nutrition=nutrition,
                                              tips=tips, image=image, img_err=img_err)
        except Exception as e:
            st.error(f"Something went wrong: {e}")

res = st.session_state.get("result")
if res:
    r, n, a = res["recipe"], res["nutrition"], res["analysis"]
    st.header(f"🍽️ {r['recipe_name']}")
    st.write(f"**⏱️ {r.get('cook_time_minutes', '?')} min** | **🌍 {a.get('cuisine_suggestion', '-')}** | "
             f"**🥄 Pantry basics:** {', '.join(a.get('missing_basics', [])) or 'none'}")
    col1, col2 = st.columns([1, 1])
    with col1:
        if res["image"] is not None:
            st.image(res["image"], use_container_width=True)
        elif res["img_err"]:
            st.info(f"Image unavailable: {res['img_err']}")
        st.subheader("⚡ Estimated nutrition (per serving)")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Calories", f"{n['calories_per_serving']} kcal")
        m2.metric("Protein", f"{n['protein_g']} g")
        m3.metric("Carbs", f"{n['carbs_g']} g")
        m4.metric("Fat", f"{n['fat_g']} g")
        st.caption(n["health_note"])
    with col2:
        st.subheader("📋 Ingredients")
        st.markdown("\n".join(f"- {i}" for i in r["ingredients"]))
        st.subheader("🔥 Cooking steps")
        st.markdown("\n".join(f"{k}. {s}" for k, s in enumerate(r["steps"], 1)))
        st.subheader("👨‍🍳 Chef tips")
        st.markdown("\n".join(f"- ⭐ {t}" for t in res["tips"]))
else:
    st.info("👈 Enter your ingredients in the sidebar and click **Generate Recipe**.")
