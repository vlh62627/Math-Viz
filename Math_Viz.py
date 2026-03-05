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
        border: 2px solid #ddd; 
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1); 
        color: #111111; 
        font-size: 1.05rem;
        line-height: 1.6;
        font-family: 'Helvetica', Arial, sans-serif;
    }
    
    .result-box h2, .result-box h3 { color: #1E3A8A; }
    .result-box p, .result-box li { color: #111111; font-weight: 450; }
    </style>
    """, unsafe_allow_html=True)

# 2. Header & Attribution
st.markdown("<h1 class='math-header'>📐 VizAI Math Engine</h1>", unsafe_allow_html=True)
st.markdown("<p class='attribution'>💡 Your Homework Assistant, One Photo or Text Away</p>", unsafe_allow_html=True)
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
st.subheader("1. Provide Problem (Image or Text)")

if 'reset_key' not in st.session_state:
    st.session_state.reset_key = 0

# --- NEW: Added Text Input Area ---
typed_problem = st.text_area("Type your math problem here (LaTeX supported):", 
                             placeholder="e.g., Integrate ln(1+sin x)/(sin x + cos x) from 0 to pi/2",
                             key=f"text_{st.session_state.reset_key}")

st.markdown("<p style='text-align: center; font-weight: bold; color: #888;'>— OR —</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📁 Upload File", "📸 Take Photo"])

with tab1:
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.reset_key}")

with tab2:
    camera_file = st.camera_input("Take a picture", key=f"camera_{st.session_state.reset_key}")

source_file = camera_file if camera_file is not None else uploaded_file

# 5. Solving Process
# Check if either a file or text is provided
if source_file or typed_problem:
    content_to_send = []
    
    if source_file:
        img = Image.open(source_file)
        max_size = (1024, 1024)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        st.image(img, width=150) 
        st.caption("Target Problem Loaded from Image")
        content_to_send.append(img)
    
    if typed_problem:
        content_to_send.append(f"TEXT PROBLEM TO SOLVE: {typed_problem}")

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
                    f"You are an expert calculus reasoning engine. Provide a {complexity} solution. "
                    "For integrals involving ln(1+sin x) / (sin x + cos x): "
                    "1. Use the property integral(f(x)) = integral(f(pi/2 - x)). "
                    "2. Use the identity sin x + cos x = sqrt(2)sin(x + pi/4). "
                    "3. Do NOT simplify to zero unless strictly proven. "
                    "Structure: ## PROBLEM IDENTIFICATION, ## THEOREMS, ## DERIVATION, ## FINAL RESULT (LaTeX)."
                )

                if "gemini" in model_choice:
                    response = client.models.generate_content(
                        model=model_choice,
                        config=types.GenerateContentConfig(system_instruction=instructions),
                        contents=content_to_send
                    )
                else:
                    # For Gemma, we combine the instructions and content
                    response = client.models.generate_content(
                        model=model_choice,
                        contents=[instructions] + content_to_send
                    )
                
                if "ERROR_NOT_READABLE" in response.text:
                    st.warning("⚠️ Image not readable. Please provide a clear mathematical image or type the problem.")
                else:
                    st.subheader(f"2. Solution Report ({model_choice})")
                    st.markdown(f"<div class='result-box'>{response.text}</div>", unsafe_allow_html=True)
                
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    st.error("🚨 Rate Limit Reached. Please wait 60 seconds.")
                else:
                    st.error(f"Engine Error: {e}")
else:
    st.info("👋 Welcome! Type a problem above or upload an image to begin.")

st.markdown("---")
st.caption(f"Status: {model_choice} Active")
