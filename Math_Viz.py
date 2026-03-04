import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import time

# 1. Page Configuration
st.set_page_config(page_title="VizAI Math Engine", page_icon="📐", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .math-header { color: #1E3A8A; font-family: 'Helvetica', sans-serif; margin-bottom: 5px; text-align: left; }
    .attribution { color: #555; text-align: left; font-size: 0.95rem; margin: 0px; padding-bottom: 5px; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1E3A8A; color: white; font-weight: bold; font-size: 1.1rem; }
    .result-box { background-color: #ffffff; padding: 25px; border-radius: 10px; border: 1px solid #ddd; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. Header & Attribution
st.markdown("<h1 class='math-header'>📐 VizAI Math Engine</h1>", unsafe_allow_html=True)
st.markdown("<p class='attribution'>💡 Your Homework Assistant, One Photo Away</p>", unsafe_allow_html=True)
st.markdown("<p class='attribution'>❤️ Developed by Vijay</p>", unsafe_allow_html=True)

# 3. Setup API Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- NEW: Model Switcher ---
st.write("---")
col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    model_choice = st.selectbox(
        "🧠 Select Reasoning Engine", 
        ["gemini-2.0-flash-lite", "gemini-2.0-flash", "gemma-3-27b-it"],
        help="Gemini is faster; Gemma offers a different reasoning perspective."
    )
with col_opt2:
    complexity = st.select_slider("Explanation Detail", options=["Brief", "Standard", "Comprehensive"], value="Standard")

# 4. Input Section
st.subheader("1. Provide Problem Image")
tab1, tab2 = st.tabs(["📁 Upload File", "📸 Take Photo"])

with tab1:
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], key="uploader")
with tab2:
    camera_file = st.camera_input("Take a picture")

source_file = camera_file if camera_file is not None else uploaded_file

# 5. Solving Process
if source_file:
    img = Image.open(source_file)
    
    # Image compression to save tokens/quota
    max_size = (1024, 1024)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    st.image(img, width=150) 
    st.caption("Target Problem Loaded")
    st.image(img, use_container_width=True)
    
    st.write("---") 
    
    if st.button("🚀 Solve"):
        with st.spinner(f"Executing {model_choice} reasoning..."):
            try:
                # Base Prompt
                instructions = (
                    f"You are a mathematical reasoning engine. Provide a {complexity} solution. "
                    "If the image is blurry or not math-related, respond ONLY with: 'ERROR_NOT_READABLE'. "
                    "Structure: ## PROBLEM IDENTIFICATION, ## THEOREMS, ## DERIVATION, ## FINAL RESULT (LaTeX)."
                )

                # --- NEW: Adaptive API Logic ---
                if "gemini" in model_choice:
                    # Gemini uses system_instruction
                    response = client.models.generate_content(
                        model=model_choice,
                        config=types.GenerateContentConfig(system_instruction=instructions),
                        contents=[img]
                    )
                else:
                    # Gemma uses combined prompt in contents
                    response = client.models.generate_content(
                        model=model_choice,
                        contents=[instructions, img]
                    )
                
                if "ERROR_NOT_READABLE" in response.text:
                    st.warning("⚠️ Image not readable. Please provide a clear mathematical image.")
                else:
                    st.subheader(f"2. Solution Report ({model_choice})")
                    st.markdown(f"<div class='result-box'>{response.text}</div>", unsafe_allow_html=True)
                
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    st.error("🚨 Rate Limit Reached. Please wait 60 seconds.")
                else:
                    st.error(f"Engine Error: {e}")
else:
    st.info("👋 Ready for a new problem! Upload a file or take a photo to begin.")

st.markdown("---")
st.caption(f"Status: {model_choice} Active | Multimodal Inference Enabled")
