import streamlit as st
import json
import sys, os

# --- Setup for Path (Keep this as is) ---
# Ensure the backend module is discoverable
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)

# NOTE: Assuming RequirementAgent is properly defined and accessible
try:
    from backend.src.agents.requirement_agent import RequirementAgent

    pipeline = RequirementAgent()
except ImportError:
    st.error(
        "Could not import RequirementAgent. Please ensure your project structure and paths are correct."
    )

    # Create a mock pipeline for demonstration if the real one isn't available
    class MockPipeline:
        def brd_generation_and_validation(self, input_text):
            st.session_state.brd_input_source = "PDF" if "pdf" in input_text else "MOM"
            mock_brd = f"**Business Requirement Document (BRD) Draft**\n\nGenerated from: {st.session_state.brd_input_source}\n\n1. **Objective:** To automate project generation from Minutes of Meeting (MOM) or a PDF document.\n2. **Scope:** The system will generate BRD, user stories, and create Jira tickets automatically.\n3. **Key Requirements:** Must handle both text and PDF inputs. BRD must be editable. Stories must be editable. Final output must integrate with Jira.\n\n*Validation:* **PASS** (100% complete)"
            mock_validation = {
                "validation_status": "complete",
                "completeness_score": 1.0,
            }
            return True, {"brd_text": mock_brd, "brd_validation": mock_validation}

        def story_generation_and_validation(self, brd_text):
            mock_stories = {
                "STORY-101": {
                    "summary": "As a user, I want to upload a PDF file.",
                    "description": "The system should allow uploading and parsing content from a PDF file as input.",
                },
                "STORY-102": {
                    "summary": "As a user, I want to paste text input.",
                    "description": "The system should provide a text area to paste MOM text as input.",
                },
                "STORY-103": {
                    "summary": "As a Product Manager, I want to edit the generated BRD.",
                    "description": "After BRD generation, the PM should be able to review and modify the content before proceeding.",
                },
                "STORY-104": {
                    "summary": "As a user, I want to create Jira tickets from the final stories.",
                    "description": "The system must connect to Jira and automatically create tickets for each validated user story.",
                },
            }
            mock_validation = {
                "validation_status": "complete",
                "story_count": len(mock_stories),
            }
            return True, {"stories": mock_stories, "story_validation": mock_validation}

        def create_jira_tickets(self, stories_json):
            num_tickets = len(stories_json)
            return (
                True,
                f"Successfully created {num_tickets} Jira tickets based on the final stories.",
            )

    if "pipeline" not in locals():
        pipeline = MockPipeline()
# --- End Setup ---


# --- CHATBOT SESSION STATE INITIALIZATION ---

# Initialize state variables if they don't exist
if "step" not in st.session_state:
    st.session_state.step = (
        "input_mode"  # "input_mode", "brd_review", "stories_review", "final_result"
    )
if "mom_text" not in st.session_state:
    st.session_state.mom_text = ""
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None
if "brd_text" not in st.session_state:
    st.session_state.brd_text = ""
if "brd_validation" not in st.session_state:
    st.session_state.brd_validation = {}
if "stories_json" not in st.session_state:
    st.session_state.stories_json = ""
if "story_validation" not in st.session_state:
    st.session_state.story_validation = {}
if "jira_message" not in st.session_state:
    st.session_state.jira_message = ""
if "input_mode" not in st.session_state:
    st.session_state.input_mode = "Paste MOM text"

# --- HELPER FUNCTIONS FOR NAVIGATION ---


def set_step(new_step):
    """Updates the current step in the session state."""
    st.session_state.step = new_step
    st.rerun()


def generate_brd():
    """Logic for Step 1: BRD Generation."""
    st.session_state.step = "processing"  # A temporary state to show spinner

    # 1. Handle PDF saving (if any)
    pdf_path = None
    if st.session_state.pdf_bytes:
        pdf_path = "temp_input.pdf"
        try:
            with open(pdf_path, "wb") as f:
                f.write(st.session_state.pdf_bytes)
        except Exception as e:
            st.error(f"Error saving PDF: {e}")
            set_step("input_mode")
            return

    input_data = st.session_state.mom_text if st.session_state.mom_text else pdf_path

    # 2. Call pipeline
    with st.spinner("🔄 STEP 1: Generating and validating BRD..."):
        try:
            flag, brd_out = pipeline.brd_generation_and_validation(
                input_text=input_data
            )
        except Exception as e:
            st.error(f"Error during BRD generation: {e}")
            set_step("input_mode")
            return

    # 3. Store results and move to review step
    st.session_state.brd_text = brd_out.get("brd_text", "")
    st.session_state.brd_validation = brd_out.get("brd_validation", {})

    # NOTE: Original code had logic to stop if BRD was incomplete.
    # We will let the user review/edit it regardless, but display a warning.
    st.session_state.brd_incomplete = not flag
    set_step("brd_review")


def generate_stories():
    """Logic for Step 2: Story Generation."""
    st.session_state.step = "processing"  # A temporary state to show spinner

    # Use the potentially edited BRD text
    brd_to_use = st.session_state.brd_text

    # 1. Call pipeline
    with st.spinner("🔄 STEP 2: Generating and validating Stories..."):
        try:
            flag, story_out = pipeline.story_generation_and_validation(brd_to_use)
        except Exception as e:
            st.error(f"Error during Story generation: {e}")
            set_step("brd_review")
            return

    # 2. Store results and move to review step
    stories = story_out.get("stories", {})
    try:
        # Store as a formatted JSON string for easy editing
        st.session_state.stories_json = json.dumps(stories, indent=2)
    except TypeError:
        st.session_state.stories_json = str(stories)  # Fallback to string
        st.warning("Stories output was not a valid JSON structure.")

    st.session_state.story_validation = story_out.get("story_validation", {})

    # NOTE: Original code had logic to stop if stories were invalid.
    # We will let the user review/edit them regardless, but display a warning.
    st.session_state.stories_invalid = not flag
    set_step("stories_review")


def create_tickets():
    """Logic for Step 3: Jira Ticket Creation."""
    st.session_state.step = "processing"  # A temporary state to show spinner

    # 1. Parse the potentially edited stories JSON
    try:
        final_stories = json.loads(st.session_state.stories_json)
    except json.JSONDecodeError:
        st.error(
            "The edited Stories text is not valid JSON. Please fix it before creating tickets."
        )
        set_step("stories_review")
        return

    # 2. Call pipeline
    with st.spinner("🔄 STEP 3: Creating JIRA tickets..."):
        try:
            flag, msg = pipeline.create_jira_tickets(final_stories)
        except Exception as e:
            st.error(f"Error during Jira ticket creation: {e}")
            st.session_state.jira_message = (
                f"❌ Failed to create Jira tickets due to a technical error: {e}"
            )
            set_step("final_result")
            return

    # 3. Store result and move to final step
    if flag:
        st.session_state.jira_message = (
            f"✅ Jira Tickets Created Successfully!\n\n{msg}"
        )
    else:
        st.session_state.jira_message = f"❌ Failed to create Jira tickets.\n\n{msg}"

    set_step("final_result")


def reset_all():
    """Clears all session state variables."""
    for key in list(st.session_state.keys()):
        if key not in ["input_mode"]:  # Keep input_mode
            del st.session_state[key]
    st.session_state.step = "input_mode"
    st.rerun()


# --- STREAMLIT APP LAYOUT ---

st.set_page_config(page_title="Project Generator Chatbot", layout="wide")
st.markdown(
    "<h1 style='font-size:32px;'>🤖 Project Generator Chatbot</h1>",
    unsafe_allow_html=True,
)

st.sidebar.button("Start Over / Reset", on_click=reset_all)

# --- CHATBOT INTERFACE (Multi-Step Logic) ---

# =============================================================
#                    STEP 0: INPUT MODE
# =============================================================
if st.session_state.step == "input_mode":

    st.subheader("1️⃣ Upload or Paste Input", divider="blue")

    # Use a key to link the radio button to the session state
    st.session_state.input_mode = st.radio(
        "Select input mode:", ["Upload PDF", "Paste MOM text"], key="radio_input_mode"
    )

    # Reset input data when switching modes
    if st.session_state.input_mode == "Upload PDF":
        uploaded = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            on_change=lambda: st.session_state.update(mom_text="", pdf_bytes=None),
        )
        if uploaded:
            st.session_state.pdf_bytes = uploaded.read()
            st.success("PDF uploaded.")
    else:  # Paste MOM text
        mom_text_input = st.text_area(
            "Paste MOM text:", height=250, key="mom_text_input"
        )
        st.session_state.mom_text = mom_text_input
        if mom_text_input:
            st.info("MOM text captured.")

    # Check if we have valid input to run
    has_input = (
        st.session_state.input_mode == "Upload PDF"
        and st.session_state.pdf_bytes is not None
    ) or (st.session_state.input_mode == "Paste MOM text" and st.session_state.mom_text)

    st.write("---")
    if has_input:
        st.button("Start BRD Generation 🚀", type="primary", on_click=generate_brd)
    else:
        st.warning("Please upload a PDF or paste MOM text to proceed.")


# =============================================================
#                   STEP 1: BRD REVIEW & EDIT
# =============================================================
elif st.session_state.step == "brd_review":

    st.markdown(
        "<h2 style='font-size:26px;'>2️⃣ BRD Generation & Validation (Review)</h2>",
        unsafe_allow_html=True,
    )

    if st.session_state.brd_incomplete:
        st.error(
            "⚠️ The initial BRD draft was marked as **incomplete** by the validation step. Please review and edit it carefully."
        )

    st.subheader("Generated BRD (Edit Below)", divider="gray")

    # 🌟 KEY FEATURE: Editable BRD text area
    st.session_state.brd_text = st.text_area(
        "Edit the BRD content here:", st.session_state.brd_text, height=400
    )

    st.subheader("BRD Validation Results", divider="gray")
    st.json(st.session_state.brd_validation)

    st.write("---")
    st.button(
        "Confirm BRD & Generate Stories ➡️", type="primary", on_click=generate_stories
    )
    st.button("⬅️ Back to Input", on_click=lambda: set_step("input_mode"))


# =============================================================
#                   STEP 2: STORIES REVIEW & EDIT
# =============================================================
elif st.session_state.step == "stories_review":

    st.markdown(
        "<h2 style='font-size:26px;'>3️⃣ Story Generation & Validation (Review)</h2>",
        unsafe_allow_html=True,
    )

    if st.session_state.stories_invalid:
        st.error(
            "⚠️ Story validation failed. Please ensure the stories are well-formed and meet requirements."
        )

    st.subheader("Generated Stories (Edit JSON Below)", divider="gray")
    st.info("Stories must be in a valid JSON format for the next step.")

    # 🌟 KEY FEATURE: Editable Stories JSON text area
    # Note: We must ensure the user enters valid JSON here.
    st.session_state.stories_json = st.text_area(
        "Edit the Stories JSON here:", st.session_state.stories_json, height=400
    )

    st.subheader("Story Validation Results", divider="gray")
    st.json(st.session_state.story_validation)

    st.write("---")
    st.button(
        "Confirm Stories & Create JIRA Tickets 🚀",
        type="primary",
        on_click=create_tickets,
    )
    st.button("⬅️ Back to BRD Edit", on_click=lambda: set_step("brd_review"))


# =============================================================
#                   STEP 3: FINAL RESULT
# =============================================================
elif st.session_state.step == "final_result":
    st.markdown(
        "<h2 style='font-size:26px;'>4️⃣ JIRA Ticket Creation Result</h2>",
        unsafe_allow_html=True,
    )

    if "✅" in st.session_state.jira_message:
        st.success(st.session_state.jira_message)
    else:
        st.error(st.session_state.jira_message)

    st.write("---")
    st.button("Start New Project", type="primary", on_click=reset_all)

# =============================================================
#                   PROCESSING/WAITING STEP
# =============================================================
elif st.session_state.step == "processing":
    # This state is brief and immediately calls the next function via on_click
    # We keep it here just in case a manual rerun is needed or to show a placeholder
    st.info("Processing... please wait.")
    st.stop()
