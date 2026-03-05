import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import time

# 1. Page Configuration
st.set_page_config(page_title="VizAI Math Engine", page_icon="📐", layout="wide")

# Custom CSS for Mobile Readability and Contrast
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .math-header { color: #1E3A8A; font-family: 'Helvetica', sans-serif; margin-bottom: 5px; text-align: left; }
    .attribution { color: #555; text-align: left; font-size: 0.95rem; margin: 0px; padding-bottom: 5px; }
    
    /* Button Styling */
    .stButton>button { 
        width: 100%; 
        border-radius: 10px; 
        height: 3.5em; 
        background-color: #1E3A8A; 
        color: white; 
        font-weight: bold; 
        font-size: 1.1rem; 
    }
    
    /* FIX: Result Box with High Contrast for Mobile */
    .result-box { 
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 10px; 
        border: 2px solid #ddd; /* Darker border */
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1); 
        color: #111111; /* Very dark charcoal for maximum readability */
        font-size: 1.05rem;
        line-height: 1.6;
        font-family: 'Helvetica', Arial, sans-serif;
    }
    
    /* Ensuring LaTeX and markdown headers inside the box are also dark */
    .result-box h2, .result-box h3 { color: #1E3A8A; }
    .result-box p, .result-box li { color: #111111; font-weight: 450; }
    </style>
    """, unsafe_allow_html=True)

# 2. Header & Attribution
st.markdown("<h1 class='math-header'>📐 VizAI Math Engine</h1>", unsafe_allow_html=True)
st.markdown("<p class='attribution'>💡 Your Homework Assistant, One Photo Away</p>", unsafe_allow_html=True)
st.markdown("<p class='attribution'>❤️ Developed by Vijay</p>", unsafe_allow_html=True)

# 3. Setup API Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- Model Selection Area ---
st.write("---")
col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    model_choice = st.selectbox(
        "🧠 Select Reasoning Engine", 
        ["gemma-3-27b-it", "gemini-2.0-flash-lite", "gemini-2.0-flash"]
    )
with col_opt2:
    complexity = st.select_slider("Explanation Detail", options=["Brief", "Standard", "Comprehensive"], value="Standard")

# 4. Input Section
st.subheader("1. Provide Problem Image")

if 'reset_key' not in st.session_state:
    st.session_state.reset_key = 0

tab1, tab2 = st.tabs(["📁 Upload File", "📸 Take Photo"])

with tab1:
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.reset_key}")

with tab2:
    camera_file = st.camera_input("Take a picture", key=f"camera_{st.session_state.reset_key}")

source_file = camera_file if camera_file is not None else uploaded_file

# 5. Solving Process
if source_file:
    img = Image.open(source_file)
    max_size = (1024, 1024)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    st.image(img, width=150) 
    st.caption("Target Problem Loaded")
    
    st.write("---") 
    
    btn_col1, btn_col2 = st.columns([4, 1])
    with btn_col1:
        solve_clicked = st.button("🚀 Solve")
    with btn_col2:
        if st.button("🔄 Reset"):
            st.session_state.reset_key += 1
            st.rerun()

    if solve_clicked:
        with st.spinner(f"Executing {model_choice} reasoning..."):
            try:
                instructions = (
    f"You are a mathematical reasoning engine. Provide a {complexity} solution. "
    "CORE OCR INSTRUCTION: If you see a complex definite integral (like ln(1+sin x)), "
    "apply King's Property: integral from 0 to a of f(x) = f(a-x). "
    "Use the identity sin x + cos x = sqrt(2)sin(x + pi/4) if necessary. "
    "Do NOT assume the result is zero without showing the full substitution steps. "
    "If the image is blurry, respond ONLY with: 'ERROR_NOT_READABLE'. "
    "Structure: ## PROBLEM IDENTIFICATION, ## THEOREMS, ## DERIVATION, ## FINAL RESULT (LaTeX)."
)

                if "gemini" in model_choice:
                    response = client.models.generate_content(
                        model=model_choice,
                        config=types.GenerateContentConfig(system_instruction=instructions),
                        contents=[img]
                    )
                else:
                    response = client.models.generate_content(
                        model=model_choice,
                        contents=[instructions, img]
                    )
                
                if "ERROR_NOT_READABLE" in response.text:
                    st.warning("⚠️ Image not readable. Please provide a clear mathematical image.")
                else:
                    st.subheader(f"2. Solution Report ({model_choice})")
                    # The container class 'result-box' now enforces dark font colors
                    st.markdown(f"<div class='result-box'>{response.text}</div>", unsafe_allow_html=True)
                
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    st.error("🚨 Rate Limit Reached. Please wait 60 seconds.")
                else:
                    st.error(f"Engine Error: {e}")
else:
    st.info("👋 Welcome! The engine is clear. Upload a file or take a photo to begin.")

st.markdown("---")
st.caption(f"Status: {model_choice} Active")
