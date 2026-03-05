import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="VizAI Math Engine", page_icon="📐", layout="wide")

# Custom CSS for Mobile Readability and Contrast
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .math-header { color: #1E3A8A; font-family: 'Helvetica', sans-serif; margin-bottom: 5px; text-align: left; }
    .attribution { color: #555; text-align: left; font-size: 0.95rem; margin: 0px; padding-bottom: 5px; }
    .stButton>button { 
        width: 100%; 
        border-radius: 10px; 
        height: 3.5em; 
        background-color: #1E3A8A; 
        color: white; 
        font-weight: bold; 
        font-size: 1.1rem; 
    }
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

# Use query params to facilitate a "Fresh Start" refresh
if 'refresh' in st.query_params:
    st.query_params.clear()
    st.rerun()

typed_problem = st.text_area("Type your math problem here:", 
                             placeholder="e.g., 2+3 or Integrate ln(1+sin x)/(sin x + cos x) from 0 to pi/2",
                             key="text_input")

st.markdown("<p style='text-align: center; font-weight: bold; color: #888;'>— OR —</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📁 Upload File", "📸 Take Photo"])
with tab1:
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], key="uploader")
with tab2:
    camera_file = st.camera_input("Take a picture", key="camera")

source_file = camera_file if camera_file is not None else uploaded_file

# 5. Solving Process logic
if source_file or typed_problem:
    content_to_send = []
    
    if source_file:
        img = Image.open(source_file)
        max_size = (1024, 1024)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        st.image(img, width=50) 
        st.caption("Target Problem Loaded from Image")
        content_to_send.append(img)
    
    if typed_problem:
        content_to_send.append(f"TEXT PROBLEM TO SOLVE: {typed_problem}")

    st.write("---") 
    
    # Solve button appears only when data is present
    if st.button("🚀 Solve"):
        with st.spinner(f"Executing {model_choice} reasoning..."):
            try:
                # Instructions updated to handle simplicity vs complexity
                instructions = (
                    f"You are an expert mathematics professor. Provide a {complexity} solution. "
                    "ADAPTIVE REASONING: If the problem is a simple arithmetic calculation (e.g., 2+3), "
                    "provide ONLY the result or a very brief explanation. For complex calculus or "
                    "theorems, follow the full structure. "
                    "For integrals involving ln(1+sin x) / (sin x + cos x): "
                    "1. Use the property integral(f(x)) = integral(f(pi/2 - x)). "
                    "2. Use the identity sin x + cos x = sqrt(2)sin(x + pi/4). "
                    "3. Do NOT simplify to zero unless strictly proven. "
                    "Structure (for complex only): ## PROBLEM IDENTIFICATION, ## THEOREMS, ## DERIVATION, ## FINAL RESULT (LaTeX)."
                )

                if "gemini" in model_choice:
                    response = client.models.generate_content(
                        model=model_choice,
                        config=types.GenerateContentConfig(system_instruction=instructions),
                        contents=content_to_send
                    )
                else:
                    response = client.models.generate_content(
                        model=model_choice,
                        contents=[instructions] + content_to_send
                    )
                
                if "ERROR_NOT_READABLE" in response.text:
                    st.warning("⚠️ Image not readable. Please provide a clear mathematical image.")
                else:
                    st.subheader(f"2. Solution Report ({model_choice})")
                    st.markdown(f"<div class='result-box'>{response.text}</div>", unsafe_allow_html=True)
                
                st.write("---")
                # Reset button moved to the end and renamed
                if st.button("🔄 Solve another problem"):
                    st.query_params["refresh"] = "true"
                    st.rerun()

            except Exception as e:
                st.error(f"Engine Error: {e}")
else:
    st.info("👋 Welcome! Type a problem above or upload an image to begin.")

st.markdown("---")
st.caption(f"Status: {model_choice} Active")
