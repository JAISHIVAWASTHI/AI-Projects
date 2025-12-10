import streamlit as st
import json
import sys, os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)

from backend.src.agents.requirement_agent import RequirementAgent

pipeline = RequirementAgent()

st.set_page_config(page_title="Project Generator", layout="wide")
st.markdown(
    "<h1 style='font-size:32px;'>📘 Project Generator</h1>",
    unsafe_allow_html=True,
)

# ---------------------- INPUT MODE ----------------------
st.subheader("1️ Upload or Paste Input", divider="blue")

input_mode = st.radio("Select input mode:", ["Upload PDF", "Paste MOM text"])
pdf_bytes = None
mom_text = ""

if input_mode == "Upload PDF":
    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded:
        pdf_bytes = uploaded.read()
else:
    mom_text = st.text_area("Paste MOM text:", height=250)

run_btn = st.button("Run Pipeline", type="primary")


# =============================================================
#                MAIN PIPELINE EXECUTION LOGIC
# =============================================================
if run_btn:

    # -------- Save temp PDF if uploaded --------
    pdf_path = None
    if pdf_bytes:
        pdf_path = "temp_input.pdf"
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

    st.write("---")
    st.markdown(
        "<h2 style='font-size:26px;'>STEP 1️⃣: BRD Generation & Validation</h2>",
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    #                STEP 1 — BRD GEN + VALIDATION
    # ---------------------------------------------------------

    with st.spinner("🔄 Generating and validating BRD..."):
        flag1, brd_out = pipeline.brd_generation_and_validation(
            input_text=mom_text if mom_text else pdf_path
        )

    st.subheader("Generated BRD", divider="gray")
    st.text_area("BRD Output", brd_out.get("brd_text", ""), height=300)

    st.subheader("BRD Validation Results", divider="gray")
    st.json(brd_out.get("brd_validation", {}))

    # ❗ If BRD incomplete — ask user to continue or stop
    if not flag1:
        st.error("⚠️ BRD is incomplete. Choose an option:")

        col1, col2 = st.columns(2)
        with col1:
            cont1 = st.button("Continue Anyway ➡️")
        with col2:
            stop1 = st.button("Stop Execution ❌")

        if stop1:
            st.stop()
        if not cont1:
            st.stop()

    # ---------------------------------------------------------
    #                STEP 2 — STORY GENERATION + VALIDATION
    # ---------------------------------------------------------
    st.write("---")
    st.markdown(
        "<h2 style='font-size:26px;'>STEP 2️⃣: Story Generation & Validation</h2>",
        unsafe_allow_html=True,
    )

    with st.spinner("🔄 Generating stories & validating..."):
        flag2, story_out = pipeline.story_generation_and_validation(
            brd_out.get("brd_text", "")
        )

    st.subheader("Generated Stories", divider="gray")
    st.text_area(
        "Stories", json.dumps(story_out.get("stories", {}), indent=2), height=350
    )

    st.subheader("Story Validation Results", divider="gray")
    st.json(story_out.get("story_validation", {}))

    # ❗ If STORY invalid — ask user to continue or stop
    if not flag2:
        st.error("⚠️ Story validation failed. Choose an option:")

        col1, col2 = st.columns(2)
        with col1:
            cont2 = st.button("Continue Anyway to JIRA ➡️")
        with col2:
            stop2 = st.button("Stop Execution ❌")

        if stop2:
            st.stop()
        if not cont2:
            st.stop()

    # ---------------------------------------------------------
    #                STEP 3 — JIRA TICKET CREATION
    # ---------------------------------------------------------
    st.write("---")
    st.markdown(
        "<h2 style='font-size:26px;'>STEP 3️⃣: Jira Ticket Creation</h2>",
        unsafe_allow_html=True,
    )

    with st.spinner("🔄 Creating JIRA tickets..."):
        flag3, msg = pipeline.create_jira_tickets(story_out.get("stories", {}))

    if flag3:
        st.success(f"✅ Jira Tickets Created Successfully!\n\n{msg}")
    else:
        st.error(f"❌ Failed to create Jira tickets.\n\n{msg}")
