import streamlit as st
from google import genai
from google.genai import types
from PIL import Image, ImageEnhance, ImageFilter
import io

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="VizAI Math Engine",
    page_icon="📐",
    layout="wide"
)

# -----------------------------------
# CUSTOM CSS
# -----------------------------------

st.markdown("""
<style>

.main {
background-color:#fcfcfc;
}

.math-header{
color:#1E3A8A;
font-family:Helvetica;
margin-bottom:5px;
}

.attribution{
color:#555;
font-size:0.95rem;
margin:0;
padding-bottom:5px;
}

.stButton>button{
width:100%;
border-radius:10px;
height:3.5em;
background-color:#1E3A8A;
color:white;
font-weight:bold;
font-size:1.1rem;
}

.result-box{
background-color:white;
padding:25px;
border-radius:10px;
border:2px solid #ddd;
box-shadow:2px 2px 10px rgba(0,0,0,0.1);
color:#111;
font-size:1.05rem;
line-height:1.6;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# HEADER
# -----------------------------------

st.markdown("<h1 class='math-header'>📐 VizAI Math Engine</h1>", unsafe_allow_html=True)
st.markdown("<p class='attribution'>💡 Your Homework Assistant, One Photo or Text Away</p>", unsafe_allow_html=True)
st.markdown("<p class='attribution'>❤️ Developed by Vijay</p>", unsafe_allow_html=True)

# -----------------------------------
# APP STATE
# -----------------------------------

if "app_mode" not in st.session_state:
    st.session_state.app_mode = "input"

if "version" not in st.session_state:
    st.session_state.version = 0

# -----------------------------------
# RESET FUNCTION
# -----------------------------------

def hard_reset():

    st.session_state.version += 1
    st.session_state.app_mode = "input"

    for key in list(st.session_state.keys()):
        if key.startswith("text_") or key.startswith("uploader_") or key.startswith("camera_"):
            del st.session_state[key]

    st.rerun()

# -----------------------------------
# API CLIENT
# -----------------------------------

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# -----------------------------------
# MODEL OPTIONS
# -----------------------------------

st.write("---")

col1,col2 = st.columns(2)

with col1:
    model_choice = st.selectbox(
        "🧠 Select Reasoning Engine",
        ["gemma-3-27b-it","gemini-2.0-flash-lite","gemini-2.0-flash"]
    )

with col2:
    complexity = st.select_slider(
        "Explanation Detail",
        ["Brief","Standard","Comprehensive"],
        value="Standard"
    )

# -----------------------------------
# INPUT SECTION
# -----------------------------------

st.subheader("1. Provide Problem")

text_key=f"text_v{st.session_state.version}"
upload_key=f"uploader_v{st.session_state.version}"
camera_key=f"camera_v{st.session_state.version}"

has_img=(st.session_state.get(upload_key) is not None) or (st.session_state.get(camera_key) is not None)
has_text=st.session_state.get(text_key,"").strip()!=""

typed_problem = st.text_area(
    "Type your math problem here:",
    placeholder="e.g., integrate x^2 dx",
    key=text_key,
    disabled=has_img
)

st.markdown("<p style='text-align:center;font-weight:bold;color:#888'>— OR —</p>",unsafe_allow_html=True)

tab1,tab2 = st.tabs(["📁 Upload File","📸 Take Photo"])

with tab1:
    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["png","jpg","jpeg"],
        key=upload_key,
        disabled=has_text
    )

with tab2:
    camera_file = st.camera_input(
        "Take a picture",
        key=camera_key,
        disabled=has_text
    )

source_file = camera_file if camera_file else uploaded_file

# -----------------------------------
# IMAGE PREPROCESSING (BETTER OCR)
# -----------------------------------

def preprocess_image(img):

    img = img.convert("L")

    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)

    img = img.filter(ImageFilter.SHARPEN)

    return img

# -----------------------------------
# PREPARE CONTENT
# -----------------------------------

active_content=[]

if source_file and not has_text:

    img = Image.open(source_file)

    img.thumbnail((1024,1024))

    img = preprocess_image(img)

    st.image(img,width=200)
    st.caption("Problem Loaded From Image")

    active_content.append(img)

elif typed_problem and not has_img:

    active_content.append(f"TEXT PROBLEM: {typed_problem}")

# -----------------------------------
# SOLVE
# -----------------------------------

if active_content:

    st.write("---")

    if st.button("🚀 Solve"):

        with st.spinner(f"Executing {model_choice} reasoning..."):

            try:

                instructions = f"""
You are a world-class mathematical reasoning engine trained for olympiad and university-level mathematics.

Your goal is to produce the MOST EXACT symbolic solution possible.

STRICT RULES:

1. ALWAYS attempt symbolic evaluation first.
2. NEVER stop at a decimal approximation if a closed-form expression exists.
3. Use symmetry, substitutions, identities, and known definite integrals when applicable.
4. If the integral can be expressed using constants (π, ln, √2, etc.), output the exact expression.
5. Only compute a decimal value AFTER the exact result.
6. Verify the solution by checking transformations or symmetry when possible.

REQUIRED OUTPUT FORMAT

## PROBLEM IDENTIFICATION
Identify the mathematical topic and any symmetry.

## STRATEGY
Explain the mathematical tricks used (symmetry, substitution, etc.).

## DERIVATION
Show the full symbolic derivation step-by-step.

## EXACT RESULT
Present the closed-form symbolic answer in LaTeX.

## NUMERICAL APPROXIMATION
Provide a decimal value for verification.

Explanation depth: {complexity}
"""

                if "gemini" in model_choice:

                    response = client.models.generate_content(
                        model=model_choice,
                        config=types.GenerateContentConfig(
                            system_instruction=instructions
                        ),
                        contents=active_content
                    )

                else:

                    response = client.models.generate_content(
                        model=model_choice,
                        contents=[instructions]+active_content
                    )

                st.session_state.app_mode="result"

                st.session_state.response_text=response.text

            except Exception as e:

                st.error(f"Engine Error: {e}")

# -----------------------------------
# RESULT VIEW
# -----------------------------------

if st.session_state.app_mode=="result":

    st.write("---")

    st.subheader("2. Solution Report")

    st.markdown(
        f"<div class='result-box'>{st.session_state.response_text}</div>",
        unsafe_allow_html=True
    )

    st.write("---")

    if st.button("🔄 Solve another problem"):
        hard_reset()

else:

    st.info("👋 Welcome! Type a problem OR upload an image to begin.")

# -----------------------------------
# FOOTER
# -----------------------------------

st.markdown("---")
st.caption(f"Status: {model_choice} Active")

