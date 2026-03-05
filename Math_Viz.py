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

# 4. MUTUALLY EXCLUSIVE & HARD RESET LOGIC
# This counter forces Streamlit to regenerate entirely new widgets when incremented
if "version" not in st.session_state:
    st.session_state.version = 0

def hard_reset():
    # Completely wipe session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Reinitialize version counter
    st.session_state.version = st.session_state.get("version", 0) + 1

    # Force full rerun
    st.rerun()

st.subheader("1. Provide Problem")

# Assign unique keys based on the current version
current_text_key = f"text_v{st.session_state.version}"
current_uploader_key = f"uploader_v{st.session_state.version}"
current_camera_key = f"camera_v{st.session_state.version}"

# Disabling logic check
has_img = (st.session_state.get(current_uploader_key) is not None) or (st.session_state.get(current_camera_key) is not None)
has_text = st.session_state.get(current_text_key, "").strip() != ""

# Text Input
typed_problem = st.text_area("Type your math problem here:", 
                             placeholder="e.g., 2+3",
                             key=current_text_key,
                             disabled=has_img)

st.markdown("<p style='text-align: center; font-weight: bold; color: #888;'>— OR —</p>", unsafe_allow_html=True)

# Image Tabs
tab1, tab2 = st.tabs(["📁 Upload File", "📸 Take Photo"])
with tab1:
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], key=current_uploader_key, disabled=has_text)
with tab2:
    camera_file = st.camera_input("Take a picture", key=current_camera_key, disabled=has_text)

source_file = camera_file if camera_file is not None else uploaded_file

# 5. Solving Process
active_content = []
# Ensure logic only processes one input type
if source_file and not has_text:
    img = Image.open(source_file)
    max_size = (1024, 1024)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    st.image(img, width=150) 
    st.caption("Target Problem Loaded from Image")
    active_content.append(img)
elif typed_problem and not has_img:
    active_content.append(f"TEXT PROBLEM: {typed_problem}")

if active_content:
    st.write("---") 
    if st.button("🚀 Solve"):
        with st.spinner(f"Executing {model_choice} reasoning..."):
            try:

                instructions = (
                    "You are an elite mathematics reasoning engine and university-level math professor. "
                    "Your task is to analyze, validate, and solve the provided math problem with extreme accuracy.\n\n"

                    "PROCESS:\n"
                    "1. Validate the problem input (text or image) and interpret the mathematical intent.\n"
                    "2. Identify the mathematical domain (arithmetic, algebra, calculus, geometry, statistics, etc.).\n"
                    "3. Detect possible ambiguities or misread symbols and internally correct them if obvious.\n"
                    "4. Solve the problem step-by-step using mathematically rigorous logic.\n"
                    "5. Double-check the result for correctness.\n"
                    "6. Provide the final verified answer.\n\n"

                    "OUTPUT RULES:\n"
                    "- If the problem is SIMPLE arithmetic (e.g., 2+3, 5×7), output ONLY the final result.\n"
                    "- For medium or complex problems, use this structure:\n\n"

                    "## PROBLEM IDENTIFICATION\n"
                    "Explain what type of math problem it is.\n\n"

                    "## DERIVATION\n"
                    "Show clear step-by-step reasoning.\n\n"

                    "## FINAL RESULT\n"
                    "Provide the final answer using proper mathematical notation (LaTeX if needed).\n\n"

                    f"Explanation depth: {complexity}."
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
                st.markdown(
                    f"<div class='result-box'>{response.text}</div>",
                    unsafe_allow_html=True
                )

                st.write("---")

                if st.button("🔄 Solve another problem"):
                    hard_reset()

            except Exception as e:
                st.error(f"Engine Error: {e}")
else:
    st.info("👋 Welcome! Type a problem OR upload an image to begin.")

st.markdown("---")
st.caption(f"Status: {model_choice} Active")


