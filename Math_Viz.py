import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="VizAI Math Engine", page_icon="📐", layout="wide")

# Custom CSS for Left Alignment and Spacing
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

model_choice = "gemini-2.0-flash-lite"
complexity = "Standard" 

st.write("---")

# 4. Input Section (Upload or Camera)
st.subheader("1. Provide Problem Image")
tab1, tab2 = st.tabs(["📁 Upload File", "📸 Take Photo"])

with tab1:
    uploaded_file = st.file_uploader("Upload an image (Handwritten or Printed)", type=["png", "jpg", "jpeg"], key="uploader")

with tab2:
    camera_file = st.camera_input("Take a picture of the problem")

# Combine inputs: prioritize camera if used, otherwise file upload
source_file = camera_file if camera_file is not None else uploaded_file

# 5. Solving Process
if source_file:
    # Logic to show a small preview above the text
    img = Image.open(source_file)
    
    # Display small thumbnail first
    st.image(img, width=150) 
    st.caption("Target Problem Loaded")
    
    # Display full preview below it
    st.image(img, use_container_width=True)
    
    st.write("---") 
    
    if st.button("🚀 Solve"):
        with st.spinner("Analyzing image..."):
            try:
                # System instructions with validation
                system_instructions = (
                    f"You are a mathematical reasoning engine. Provide a {complexity} solution. "
                    "VALIDATION RULE: If the image is blurry, unreadable, or does not contain a mathematical problem, "
                    "respond ONLY with: 'ERROR_NOT_READABLE'. "
                    "Otherwise, follow this structure:\n"
                    "## PROBLEM IDENTIFICATION\n"
                    "## THEOREMS & FORMULAS\n"
                    "## STEP-BY-STEP DERIVATION\n"
                    "## FINAL RESULT (in LaTeX)"
                )

                response = client.models.generate_content(
                    model=model_choice,
                    config=types.GenerateContentConfig(system_instruction=system_instructions),
                    contents=[img]
                )
                
                # Check for readability error
                if "ERROR_NOT_READABLE" in response.text:
                    st.warning("⚠️ Image not readable. Please provide another clear mathematical image.")
                else:
                    st.subheader("2. Solution Report")
                    st.markdown(f"<div class='result-box'>{response.text}</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Engine Error: {e}")
else:
    # Reset state on page refresh
    st.info("👋 Ready for a new problem! Upload a file or take a photo to begin.")

# 6. Technical Footer
st.markdown("---")
st.caption("Status: LLM Engine Ready | Multimodal Inference Active")
