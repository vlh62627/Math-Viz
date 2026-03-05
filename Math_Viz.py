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

# 4. MUTUALLY EXCLUSIVE INPUT LOGIC
st.subheader("1. Provide Problem")

# Reset Function: Deletes all session data to clear text/images
def reset_all():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# Determine disabling logic based on existing content
has_image = st.session_state.get("uploader") is not None or st.session_state.get("camera") is not None
has_text = st.session_state.get("text_input", "") != ""

# Text Input (Disabled if image exists)
typed_problem = st.text_area("Type your math problem here:", 
                             placeholder="e.g., 2+3",
                             key="text_input",
                             disabled=has_image)

st.markdown("<p style='text-align: center; font-weight: bold; color: #888;'>— OR —</p>", unsafe_allow_html=True)

# Image Tabs (Disabled if text exists)
tab1, tab2 = st.tabs(["📁 Upload File", "📸 Take Photo"])
with tab1:
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], key="uploader", disabled=has_text)
with tab2:
    camera_file = st.camera_input("Take a picture", key="camera", disabled=has_text)

source_file = camera_file if camera_file is not None else uploaded_file

# 5. Solving Process
active_content = []
if source_file and not has_text:
    img = Image.open(source_file)
    max_size = (1024, 1024)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    st.image(img, width=150) 
    st.caption("Target Problem Loaded from Image")
    active_content.append(img)
elif typed_problem and not has_image:
    active_content.append(f"TEXT PROBLEM TO SOLVE: {typed_problem}")

if active_content:
    st.write("---") 
    if st.button("🚀 Solve"):
        with st.spinner(f"Executing {model_choice} reasoning..."):
            try:
                instructions = (
                    f"You are an expert mathematics professor. Provide a {complexity} solution. "
                    "ADAPTIVE REASONING: If the problem is a simple arithmetic calculation (e.g., 2+3), "
                    "provide ONLY the result or a very brief explanation. For complex calculus, "
                    "use the full structure: ## PROBLEM IDENTIFICATION, ## THEOREMS, ## DERIVATION, ## FINAL RESULT (LaTeX)."
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
                
                st.subheader(f"2. Solution Report ({model_choice})")
                st.markdown(f"<div class='result-box'>{response.text}</div>", unsafe_allow_html=True)
                
                st.write("---")
                # Clicking this will now trigger the full clear of the text box and images
                if st.button("🔄 Solve another problem"):
                    reset_all()

            except Exception as e:
                st.error(f"Engine Error: {e}")
else:
    st.info("👋 Welcome! Type a problem OR upload an image to begin.")

st.markdown("---")
st.caption(f"Status: {model_choice} Active")
