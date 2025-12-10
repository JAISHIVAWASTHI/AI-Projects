import streamlit as st
import json
import sys, os

# --- Path Setup ---
# Ensure the backend module is discoverable
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)
from backend.src.agents.requirement_agent import RequirementAgent

# --- Initialize Agent ---
if "pipeline" not in st.session_state:
    try:
        # st.session_state.pipeline = RequirementAgent()
        raise ImportError
    except ImportError:
        # Placeholder for demonstration if RequirementAgent is not available
        class MockPipeline:
            def process_user_message(self, user_input, current_context=None):
                if "brd" in user_input.lower():
                    return {
                        "type": "action_brd",
                        "message": "Starting BRD generation...",
                        "input_data": "Mock MOM Text",
                    }
                if "stories" in user_input.lower():
                    return {
                        "type": "action_stories",
                        "message": "Starting Story generation...",
                        "input_data": current_context,
                    }
                if "jira" in user_input.lower():
                    return {
                        "type": "action_jira",
                        "message": "Starting Jira ticket creation...",
                    }
                return {
                    "type": "chat",
                    "message": "I'm a mock AI. Try asking me to 'Generate BRD' or 'Generate Stories' after providing input.",
                }

            def brd_generation_and_validation(self, input_text):
                # Simulate a failure for demonstration (e.g., incompleteness)
                is_valid = False
                validation = {
                    "completeness": "80%",
                    "missing_sections": ["Scope", "Success Criteria"],
                }
                brd_text = "DRAFT BRD:\n1. Objective: Project automation.\n2. Needs: Convert input to BRD, stories, and Jira tickets."
                return is_valid, {"brd_validation": validation, "brd_text": brd_text}

            def story_generation_and_validation(self, brd_text):
                # Simulate a success for demonstration
                is_valid = True
                validation = {"format_check": "Pass", "story_count": 3}
                stories = {
                    "STORY-1": {
                        "summary": "As a user, I can upload a PDF.",
                        "description": "System parses PDF content.",
                    },
                    "STORY-2": {
                        "summary": "As a PM, I can edit the BRD.",
                        "description": "Editable text area for BRD content.",
                    },
                    "STORY-3": {
                        "summary": "As a dev, I get a Jira ticket.",
                        "description": "Automated ticket creation.",
                    },
                }
                return is_valid, {"story_validation": validation, "stories": stories}

            def create_jira_tickets(self, stories_json):
                num_tickets = len(stories_json)
                return True, f"Successfully created {num_tickets} Mock Jira tickets."

        st.session_state.pipeline = MockPipeline()


st.set_page_config(page_title="Project AI Assistant", layout="wide")

# --- Session State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! Upload a MOM PDF in the sidebar or paste text here. I can help you generate BRDs and User Stories.",
        }
    ]
if "context_brd" not in st.session_state:
    st.session_state.context_brd = ""
if "context_stories" not in st.session_state:
    st.session_state.context_stories = {}
if "temp_pdf_path" not in st.session_state:
    st.session_state.temp_pdf_path = None
if "is_processing" not in st.session_state:
    st.session_state.is_processing = (
        False  # New state variable for sequential guardrail
    )

# =========================================================
# 📂 SIDEBAR: FILE UPLOADER
# =========================================================
with st.sidebar:
    st.header("📂 Input Source")
    st.write("Upload your Minutes of Meeting (MOM) here:")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:
        temp_path = "temp_uploaded_mom.pdf"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.session_state.temp_pdf_path = temp_path
        st.success(f"✅ Loaded: {uploaded_file.name}")
    else:
        st.session_state.temp_pdf_path = None

# =========================================================
# 💬 CHAT INTERFACE
# =========================================================
st.title("🤖 Quantnik AI")

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        content = msg["content"]
        # Threshold: if content is longer than 500 chars, use a scroll box
        if len(content) > 500:
            with st.container(height=300, border=True):
                st.markdown(content)
        else:
            st.markdown(content)

if st.session_state.is_processing:
    st.chat_input("Processing in progress... please wait.", disabled=True)
elif user_input := st.chat_input(
    "Type here... (e.g., 'Generate BRD from the uploaded file')"
):

    # Set processing flag
    st.session_state.is_processing = True

    # 1. Append User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Process Intent via Agent
    with st.spinner("Thinking..."):
        response_payload = st.session_state.pipeline.process_user_message(
            user_input, current_context=st.session_state.context_brd
        )
        print("Response Payload:", response_payload)
    if not response_payload.get("data") and response_payload.get("error"):
        st.error(f"⚠️ An error occurred: {response_payload['error']}")
    intent_type = response_payload.get("type")
    bot_reply = response_payload.get("message")
    extracted_data = response_payload.get("input_data")

    # 3. Handle Actions based on Intent

    # --- CASE A: Normal Chat ---
    if intent_type == "chat":
        print("Normal Chat...")
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # --- CASE B: Generate BRD (Handles PDF vs Text) ---
    elif intent_type == "action_brd":
        print("Generating BRD...")
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

            # --- Input Source Logic (PDF vs Text) ---
            final_input = None
            source_label = ""

            if extracted_data and len(extracted_data) > 100:
                final_input = extracted_data
                source_label = "chat text"
            elif st.session_state.temp_pdf_path:
                final_input = st.session_state.temp_pdf_path
                source_label = "uploaded PDF"
            else:
                st.error(
                    "⚠️ I need input data! Please paste the MOM text in the chat OR upload a PDF in the sidebar."
                )
                st.stop()

            with st.spinner(f"🔄 Reading from {source_label} and generating BRD..."):
                # Call Pipeline
                flag, brd_out = st.session_state.pipeline.brd_generation_and_validation(
                    input_text=final_input
                )

            # ❗ CHANGE 1: DO NOT STOP, SHOW RESULTS REGARDLESS OF FLAG
            st.success("✅ BRD Generation Attempt Complete!")
            st.session_state.context_brd = brd_out.get("brd_text", "")

            # Show Warning if Validation Failed
            if not flag:
                st.warning(
                    "⚠️ **BRD Validation Failed!** Please review the validation data and edit the BRD to ensure completeness before continuing."
                )

            # Show Validation Data
            with st.expander("🔬 AI Validation Data (BRD)", expanded=True):
                # ❗ CHANGE 2: Show validation data explicitly
                st.json(brd_out.get("brd_validation", {}))

            # Editable BRD Container (Always shown)
            with st.expander("📄 Review & Edit Generated BRD", expanded=True):
                edited_brd = st.text_area(
                    "Edit BRD:", st.session_state.context_brd, height=300
                )
                if st.button("Save & Confirm BRD"):
                    st.session_state.context_brd = edited_brd
                    st.info("BRD Saved. You can now ask: 'Generate user stories'.")

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "I have generated the BRD. Please review the validation and edit if necessary.",
                }
            )
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"{st.session_state.context_brd}",
                }
            )

    # --- CASE C: Generate Stories ---
    elif intent_type == "action_stories":
        print("Generating user stories...")
        if not st.session_state.context_brd:
            st.error(
                "⚠️ I don't have a BRD yet. Please upload a PDF or paste text and ask me to generate a BRD first."
            )
        else:
            with st.chat_message("assistant"):
                st.markdown(bot_reply)
                with st.spinner("🔄 Generating User Stories..."):
                    flag, story_out = (
                        st.session_state.pipeline.story_generation_and_validation(
                            st.session_state.context_brd
                        )
                    )

                # ❗ CHANGE 3: DO NOT STOP, SHOW RESULTS REGARDLESS OF FLAG
                st.success("✅ Story Generation Attempt Complete!")

                stories = story_out.get("stories", {})
                try:
                    stories_str = json.dumps(stories, indent=2)
                except TypeError:
                    stories_str = str(stories)  # Fallback if structure is invalid
                    st.error("Generated stories structure is invalid.")

                st.session_state.context_stories = stories

                # Show Warning if Validation Failed
                if not flag:
                    st.warning(
                        "⚠️ **Story Validation Failed!** Please review the validation data and edit the Stories JSON to ensure valid format/completeness before continuing."
                    )

                # Show Validation Data
                with st.expander("🔬 AI Validation Data (Stories)", expanded=True):
                    # ❗ CHANGE 4: Show validation data explicitly
                    st.json(story_out.get("story_validation", {}))

                # Editable Stories Container (Always shown)
                with st.expander(
                    "📝 Review & Edit Generated Stories JSON", expanded=True
                ):
                    edited_stories_str = st.text_area(
                        "Edit Stories JSON:", stories_str, height=300
                    )

                    if st.button("Save & Confirm Stories"):
                        try:
                            st.session_state.context_stories = json.loads(
                                edited_stories_str
                            )
                            st.success(
                                "Stories saved! You can now ask: 'Push these to Jira'."
                            )
                        except json.JSONDecodeError:
                            st.error(
                                "Invalid JSON format. Please correct it before continuing."
                            )
                            st.stop()

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": "User stories generated. Review the validation and edit them above.",
                    }
                )
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": f"{json.dumps(st.session_state.context_stories, indent=2)}",
                    }
                )

    # --- CASE D: Create Jira Tickets ---
    elif intent_type == "action_jira":
        print("Running Jira ticket creation...")
        if not st.session_state.context_stories:
            st.error("⚠️ No stories found. Please generate stories first.")
        else:
            with st.chat_message("assistant"):
                st.markdown(bot_reply)
                with st.spinner("🔄 Pushing tickets to Jira..."):
                    flag, msg = st.session_state.pipeline.create_jira_tickets(
                        st.session_state.context_stories
                    )

                if flag:
                    st.success(f"✅ {msg}")
                    st.session_state.messages.append(
                        {"role": "assistant", "content": f"Success: {msg}"}
                    )
                else:
                    st.error(f"❌ Failed: {msg}")

    st.session_state.is_processing = False

if not st.session_state.is_processing:
    # This prevents the chat input from being disabled prematurely if a previous rerun occurred
    pass
