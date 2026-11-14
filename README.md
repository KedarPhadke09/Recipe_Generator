# 🍳 AI Recipe Generator

An AI-powered multi-agent app that turns the ingredients you have into a complete recipe, with nutrition estimates, chef tips and an AI-generated photo of the dish.

Built with **Groq** (LLM), **Streamlit** (UI) and **Pollinations / Hugging Face FLUX** (image generation).

## ✨ Features

- Enter any ingredients, comma separated (e.g. `Tomato, Onion, Paneer, Capsicum`)
- Dietary preferences: Any, Vegetarian, Vegan, High-protein, Low-calorie, Jain
- Full output: recipe name, ingredients, cooking steps, estimated calories and macros, chef tips
- AI-generated image of the finished dish
- Live progress while the agents work

## 🧠 How it works

```
Available Ingredients
        ↓
 Ingredient Analyzer     → cleans input, finds cuisine, lists pantry basics
        ↓
 Recipe Generator        → name, ingredients, steps, cook time
        ↓
 Nutrition Advisor       → calories, protein, carbs, fat
        ↓
 Cooking Tips Generator  → practical chef tips
        ↓
 Image Prompt Agent      → food-photography prompt
        ↓
 Image Generator         → Pollinations (free), Hugging Face FLUX as fallback
```

Each agent is a separate function that calls the Groq API with its own role prompt. The output of one step feeds the next.

## 🚀 Run locally

**1. Clone the repo**
```bash
git clone https://github.com/<your-username>/ai-recipe-generator.git
cd ai-recipe-generator
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your API keys**

Get a free Groq key at https://console.groq.com/keys.

Create the file `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your_groq_key_here"
HF_TOKEN = "your_hugging_face_token_here"   # optional, only for image fallback
```

**4. Start the app**
```bash
streamlit run streamlit_app.py
```

## ☁️ Deploy on Streamlit Community Cloud

1. Push this repo to GitHub.
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **Create app**, select this repo, branch `main`, main file `streamlit_app.py`.
4. Open **Advanced settings → Secrets** and paste the same contents as `secrets.toml` above.
5. Click **Deploy**.

## ⚙️ Configuration

| Secret | Required | Purpose |
|---|---|---|
| `GROQ_API_KEY` | Yes | Powers all text agents |
| `HF_TOKEN` | No | Fallback image generation via Hugging Face FLUX |

The model is set in `streamlit_app.py` (`MODEL = "openai/gpt-oss-120b"`). Groq retires models from time to time, so if you see a model error, check the current list at https://console.groq.com/docs/models and update that line.

## ⚠️ Notes

- Calories and nutrition values are AI estimates, not exact figures.
- Free API tiers have rate limits, so heavy traffic may cause temporary errors.
- Never commit your API keys. Add `.streamlit/secrets.toml` to `.gitignore`.

## 📁 Project structure

```
ai-recipe-generator/
├── streamlit_app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 🛠️ Tech stack

Python · Streamlit · Groq API · Hugging Face Hub · Pillow · Requests

## 📄 License

MIT. Free to use and modify.
