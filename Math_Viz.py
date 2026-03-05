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
    
    /* Result Box with High Contrast */
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
    .result-box h2, .result-box h3 { color: #1E3A8A; }
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

# 4. HARD RESET LOGIC
# This counter forces Streamlit to generate entirely new widgets when incremented
if "reset_id" not in st.session_state:
    st.session_state.reset_id = 0

def clear_and_reset():
    st.session_state.reset_id += 1
    # Clear all other session variables
    for key in list(st.session_state.keys()):
        if key != "reset_id":
            del st.session_state[key]
    st.rerun()

st.subheader("1. Provide Problem")

# Assigning unique keys based on the reset_id
text_key = f"text_v{st.session_state.reset_id}"
file_key = f"file_v{st.session_state.reset_id}"
cam_key = f"cam_v{st.session_state.reset_id}"

# Mutual Exclusion Check
has_image = (st.session_state.get(file_key) is not None) or (st.session_state.get(cam_key) is not None)
has_text = st.session_state.get(text_key, "").strip() != ""

# Text Input (Disabled if image provided)
typed_problem = st.text_area("Type your math problem here:", 
                             placeholder="e.g., 2+3 or Solve x^2 + 5x + 6 = 0",
                             key=text_key,
                             disabled=has_image)

st.markdown("<p style='text-align: center; font-weight: bold; color: #888;'>— OR —</p>", unsafe_allow_html=True)

# Image Tabs (Disabled if text provided)
tab1, tab2 = st.tabs(["📁 Upload File", "📸 Take Photo"])
with tab1:
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], key=file_key, disabled=has_text)
with tab2:
    camera_file = st.camera_input("Take a picture", key=cam_key, disabled=has_text)

source_file = camera_file if camera_file is not None else uploaded_file

# 5. Solving Process
active_content = []
if source_file and not has_text:
    img = Image.open(source_file)
    max_size = (1024, 1024)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    st.image(img, width=150) 
    active_content.append(img)
elif typed_problem and not has_image:
    active_content.append(f"TEXT PROBLEM: {typed_problem}")

if active_content:
    st.write("---") 
    if st.button("🚀 Solve"):
        with st.spinner(f"Executing {model_choice} reasoning..."):
            try:
                instructions = (
                    f"You are a math professor. Provide a {complexity} solution. "
                    "For simple arithmetic like '2+3', provide ONLY the answer. "
                    "For calculus/algebra, provide full steps: ## PROBLEM IDENTIFICATION, ## DERIVATION, ## FINAL RESULT."
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
                # Clicking this clears EVERYTHING
                if st.button("🔄 Solve another problem"):
                    clear_and_reset()

            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.info("👋 Provide a problem via text or image to begin.")

st.markdown("---")
st.caption(f"Status: {model_choice} Active")
