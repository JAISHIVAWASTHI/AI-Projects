import streamlit as st
import json
from io import BytesIO
import sys, os

sys.path.append(
    os.path.abspath(
        os.path.abspath(
            os.path.join(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
            )
        )
    )
)


from backend.src.agents.requirement_agent import (
    RequirementAgent,
)  # replace with your actual class file

# Initialize pipeline class
pipeline = RequirementAgent()

st.set_page_config(page_title="BRD & Story Generator", layout="wide")

st.title("BRD and User Story Generator")
st.markdown("Generate and validate BRD and User Stories from Meeting Minutes or PDF.")

# --- Input section ---
st.subheader("1️Upload MOM or PDF")
input_mode = st.radio("Select input mode:", ["Upload PDF", "Paste MOM text"])

pdf_bytes = None
mom_text = ""

if input_mode == "Upload PDF":
    uploaded_file = st.file_uploader("Upload a meeting minutes PDF", type=["pdf"])
    if uploaded_file:
        pdf_bytes = uploaded_file.read()
else:
    mom_text = st.text_area("Paste MOM text below:", height=250)

# --- Run button ---
if st.button("Run Pipeline"):
    with st.spinner("Running pipeline..."):
        try:
            # Save PDF temporarily if uploaded
            pdf_path = None
            if pdf_bytes:
                pdf_path = "temp_input.pdf"
                with open(pdf_path, "wb") as f:
                    f.write(pdf_bytes)

            # Identify mode in your runner (PDF or MOM text)
            result = pipeline.runner(pdf_path=pdf_path if pdf_bytes else None)

            # Display all returned state fields
            st.success("Pipeline completed successfully!")

            if "brd_text" in result:
                st.subheader("BRD Generated")
                st.text_area("BRD Document", result["brd_text"], height=300)

            if "brd_validation" in result:
                brd_val = result["brd_validation"]
                st.subheader("BRD Validation Results")
                # st.markdown(f"**BRD Validation:** {brd_val}%")
                st.json(brd_val)

            if "stories" in result:
                st.subheader("User Stories Generated")
                st.text_area("Generated Stories", result["stories"], height=300)

            if "story_validation" in result:
                story_val = result["story_validation"]
                st.subheader("User Story Validation Results")
                # st.markdown(
                #     f"**Story Validation:** `{story_val.get('alignment_confidence', 0)}"
                # )
                st.json(story_val)

        except Exception as e:
            st.error(f"Error running pipeline: {e}")
