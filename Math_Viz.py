import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="VizAI Math Engine", page_icon="📐", layout="wide")

# Custom CSS for Mobile Readability & High Contrast
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .math-header { color: #002D62; font-family: 'Arial', sans-serif; text-align: left; }
    
    /* FIX: High-Contrast Result Box for Mobile */
    .result-box { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 8px; 
        border: 3px solid #000000; /* Thick black border */
        color: #000000; /* Pure black text */
        font-size: 1.1rem;
        font-weight: 500; /* Thicker font weight */
        line-height: 1.6;
    }
    .result-box h2, .result-box h3 { color: #002D62; font-weight: 700; }
    
    .stButton>button { 
        background-color: #002D62; 
        color: white; 
        font-weight: bold; 
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='math-header'>📐 VizAI Math Engine</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #333;'>❤️ Developed by Vijay</p>", unsafe_allow_html=True)

# 3. Setup API Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- Model Selection Area ---
st.write("---")
model_choice = st.selectbox("🧠 Select Reasoning Engine", ["gemini-2.0-flash", "gemma-3-27b-it"])

# 4. Input Section
if 'reset_key' not in st.session_state:
    st.session_state.reset_key = 0

tab1, tab2 = st.tabs(["📁 Upload File", "📸 Take Photo"])
with tab1:
    uploaded_file = st.file_uploader("Upload", type=["png", "jpg", "jpeg"], key=f"u_{st.session_state.reset_key}")
with tab2:
    camera_file = st.camera_input("Photo", key=f"c_{st.session_state.reset_key}")

source_file = camera_file if camera_file else uploaded_file

if source_file:
    img = Image.open(source_file)
    st.image(img, width=200)
    
    if st.button("🚀 Solve"):
        with st.spinner("Analyzing complex integral..."):
            try:
                # --- FIX: REFINED CALCULUS PROMPT ---
                instructions = (
                    "You are an expert calculus reasoning engine. "
                    "For integrals involving ln(1+sin x) / (sin x + cos x): "
                    "1. Use the property integral(f(x)) = integral(f(pi/2 - x)). "
                    "2. Use the identity sin x + cos x = sqrt(2)sin(x + pi/4). "
                    "3. Do NOT simplify to zero unless strictly proven. "
                    "Structure: ## PROBLEM IDENTIFICATION, ## MATHEMATICAL IDENTITIES, ## STEP-BY-STEP INTEGRATION, ## FINAL RESULT (LaTeX)."
                )

                response = client.models.generate_content(
                    model=model_choice,
                    config=types.GenerateContentConfig(system_instruction=instructions),
                    contents=[img]
                )
                
                st.subheader("2. Solution Report")
                st.markdown(f"<div class='result-box'>{response.text}</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error: {e}")

if st.button("🔄 Reset Page"):
    st.session_state.reset_key += 1
    st.rerun()
