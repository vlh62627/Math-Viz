import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="VizAI Math Engine", page_icon="📐", layout="wide")

# Custom CSS
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

# 4. HARD RESET LOGIC (Key Rotation)
if "reset_id" not in st.session_state:
    st.session_state.reset_id = 0

def perform_hard_reset():
    # Incrementing this ID forces Streamlit to recreate all widgets from scratch
    st.session_state.reset_id += 1
    # Clear all other session data
    for key in list(st.session_state.keys()):
        if key != "reset_id":
            del st.session_state[key]
    st.rerun()

st.subheader("1. Provide Problem")

# Generate unique keys for the current session iteration
current_text_key = f"text_input_v{st.session_state.reset_id}"
current_uploader_key = f"uploader_v{st.session_state.reset_id}"
current_camera_key = f"camera_v{st.session_state.reset_id}"

# Mutual Exclusion Disabling Logic
has_img = (st.session_state.get(current_uploader_key) is not None) or (st.session_state.get(current_camera_key) is not None)
has_txt = st.session_state.get(current_text_key, "").strip() != ""

# Text Input
typed_problem = st.text_area("Type your math problem here:", 
                             placeholder="e.g., 2+3",
                             key=current_text_key,
                             disabled=has_img)

st.markdown("<p style='text-align: center; font-weight: bold; color: #888;'>— OR —</p>", unsafe_allow_html=True)

# Image Tabs
tab1, tab2 = st.tabs(["📁 Upload File", "📸 Take Photo"])
with tab1:
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], key=current_uploader_key, disabled=has_txt)
with tab2:
    camera_file = st.camera_input("Take a picture", key=current_camera_key, disabled=has_txt)

source_file = camera_file if camera_file is not None else uploaded_file

# 5. Solving Process
active_content = []
# Ensure we only pick ONE source based on mutual exclusion
if source_file and not has_txt:
    img = Image.open(source_file)
    max_size = (1024, 1024)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    st.image(img, width=150) 
    st.caption("Target Problem Loaded from Image")
    active_content.append(img)
elif typed_problem and not has_img:
    active_content.append(f"TEXT PROBLEM TO SOLVE: {typed_problem}")

if active_content:
    st.write("---") 
    # Show the Solve button ONLY if data exists
    if st.button("🚀 Solve"):
        with st.spinner(f"Executing {model_choice} reasoning..."):
            try:
                instructions = (
                    f"You are an expert mathematics professor. Provide a {complexity} solution. "
                    "ADAPTIVE REASONING: If the problem is simple arithmetic (e.g., 2+3, 5*10), "
                    "output ONLY the answer with a one-sentence confirmation. "
                    "For complex calculus, show full steps: ## PROBLEM IDENTIFICATION, ## THEOREMS, ## DERIVATION, ## FINAL RESULT (LaTeX)."
                )

                if "gemini" in model_choice:
                    response = client.models.generate_content(
                        model=model_choice,
                        config=types.GenerateContentConfig(system_instruction=instructions),
                        contents=active_content
                    )
                else:
                    response = client.models.generate_content(
                        model=model_choice,
                        contents=[instructions] + active_content
                    )
                
                st.subheader("2. Solution Report")
                st.markdown(f"<div class='result-box'>{response.text}</div>", unsafe_allow_html=True)
                
                st.write("---")
                # Reset button appears after result
                if st.button("🔄 Solve another problem"):
                    perform_hard_reset()

            except Exception as e:
                st.error(f"Engine Error: {e}")
else:
    st.info("👋 Welcome! Provide a text problem OR an image to start.")

st.markdown("---")
st.caption(f"Status: {model_choice} Active")
