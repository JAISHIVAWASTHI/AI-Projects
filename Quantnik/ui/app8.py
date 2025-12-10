import streamlit as st
import json
import sys, os

# --- Path Setup ---
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)
from backend.src.agents.requirement_agent import (
    RequirementAgent,
)  # Commented out for standalone running

# --- Initialize Agent ---
# --- Initialize Agent ---
if "pipeline" not in st.session_state:
    # Define the MockPipeline class effectively acts as a backup AI
    class MockPipeline:
        def process_user_message(self, user_input, current_context=None):
            user_input = user_input.lower()
            if "brd" in user_input:
                return {
                    "type": "action_brd",
                    "message": "Starting BRD generation...",
                    "input_data": "Mock MOM Text",
                }
            if "stories" in user_input:
                return {
                    "type": "action_stories",
                    "message": "Starting Story generation...",
                    "input_data": current_context,
                }
            if "jira" in user_input:
                return {
                    "type": "action_jira",
                    "message": "Starting Jira ticket creation...",
                }
            return {
                "type": "chat",
                "message": "I'm a mock AI. Try asking me to 'Generate BRD' or 'Generate Stories'.",
            }

        def brd_generation_and_validation(self, input_text):
            is_valid = True
            validation = {
                "completeness": "85%",
                "missing_sections": ["None"],
                "tone": "Professional",
            }
            brd_text = "DRAFT BRD:\n" + "\n".join(
                [f"{i}. Requirement detail line {i}..." for i in range(1, 20)]
            )
            return is_valid, {"brd_validation": validation, "brd_text": brd_text}

        def story_generation_and_validation(self, brd_text):
            is_valid = True
            validation = {"format_check": "Pass", "story_count": 3}
            stories = {
                f"STORY-{i}": {"summary": f"User story {i}", "description": "Desc..."}
                for i in range(1, 5)
            }
            return is_valid, {"story_validation": validation, "stories": stories}

        def create_jira_tickets(self, stories_json):
            return True, f"Successfully created {len(stories_json)} Mock Jira tickets."

    # Try to load the real agent, otherwise load the Mock
    try:
        # Move import INSIDE try block to prevent immediate crash
        st.session_state.pipeline = RequirementAgent()
    except (ImportError, ModuleNotFoundError):
        print("⚠️ Backend not found. Using MockPipeline.")
        st.session_state.pipeline = MockPipeline()


st.set_page_config(page_title="Project AI Assistant", layout="wide")

# --- Session State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I am Quantnik AI, how can I assist you today?",
        }
    ]
if "context_brd" not in st.session_state:
    st.session_state.context_brd = ""
if "context_stories" not in st.session_state:
    st.session_state.context_stories = {}
if "mom_pdf_path" not in st.session_state:
    st.session_state.mom_pdf_path = None
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

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
        st.session_state.mom_pdf_path = temp_path
        st.success(f"✅ Loaded: {uploaded_file.name}")
    else:
        st.session_state.mom_pdf_path = None

# =========================================================
# 💬 CHAT INTERFACE
# =========================================================
st.title("🤖 Quantnik AI")

# --- UPDATED: Scrollable Chat History ---
# If a message is very long (like a generated BRD), wrap it in a scrollable container
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
    "Type here... (e.g., 'Generate BRD', 'Generate Stories')"
):

    st.session_state.is_processing = True

    # 1. Append User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Process Intent via Agent
    with st.spinner("Thinking..."):
        try:
            response_payload = st.session_state.pipeline.process_user_message(
                user_input, current_context=st.session_state.context_brd
            )
        except Exception as e:
            st.error(f"⚠️ An error occurred: {e}")
            st.session_state.is_processing = False
            st.stop()

    intent_type = response_payload.get("type")
    bot_reply = response_payload.get("message")
    extracted_data = response_payload.get("input_data")

    # --- CASE A: Normal Chat ---
    if intent_type == "chat":
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # --- CASE B: Generate BRD ---
    elif intent_type == "action_brd":
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

            # Determine input source
            final_input = None
            if extracted_data and len(extracted_data) > 100:  # Arbitrary length check
                final_input = extracted_data
            elif st.session_state.mom_pdf_path:
                final_input = st.session_state.mom_pdf_path
            else:
                st.error("⚠️ I need input data! Please paste text or upload a PDF.")
                st.session_state.is_processing = False
                st.stop()

            with st.spinner(f"🔄 Generating BRD..."):
                flag, brd_out = st.session_state.pipeline.brd_generation_and_validation(
                    input_text=final_input
                )

            st.success("✅ BRD Generation Attempt Complete!")
            st.session_state.context_brd = brd_out.get("brd_text", "")

            # --- UI UPDATE: SCROLLABLE CONTAINERS FOR BRD ---

            # 1. Validation Data in Scrollable Box
            with st.expander("🔬 AI Validation Data (BRD)", expanded=True):
                with st.container(height=150, border=True):
                    st.json(brd_out.get("brd_validation", {}))

            # 2. BRD Editor in Scrollable Box
            with st.expander("📄 Review & Edit Generated BRD", expanded=True):
                # We put the text area inside a container with fixed height
                with st.container(height=400, border=True):
                    edited_brd = st.text_area(
                        "Edit BRD:",
                        st.session_state.context_brd,
                        height=1000,  # Make inner height large so scrolling is handled by container
                        label_visibility="collapsed",
                    )

                if st.button("Save & Confirm BRD"):
                    st.session_state.context_brd = edited_brd
                    st.info("BRD Saved. Ask 'Generate stories' next.")

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "I have generated the BRD. Please review above.",
                }
            )
            # We append the full BRD to history, but the loop at the top handles the scrolling display
            st.session_state.messages.append(
                {"role": "assistant", "content": f"{st.session_state.context_brd}"}
            )

    # --- CASE C: Generate Stories ---
    elif intent_type == "action_stories":
        if not st.session_state.context_brd:
            st.error("⚠️ No BRD found. Please generate BRD first.")
        else:
            with st.chat_message("assistant"):
                st.markdown(bot_reply)
                with st.spinner("🔄 Generating User Stories..."):
                    flag, story_out = (
                        st.session_state.pipeline.story_generation_and_validation(
                            st.session_state.context_brd
                        )
                    )

                st.success("✅ Story Generation Attempt Complete!")
                stories = story_out.get("stories", {})

                try:
                    stories_str = json.dumps(stories, indent=2)
                except TypeError:
                    stories_str = str(stories)

                st.session_state.context_stories = stories
                # --- UI UPDATE: SCROLLABLE CONTAINERS FOR STORIES ---

                # 1. Validation Data in Scrollable Box
                with st.expander("🔬 AI Validation Data (Stories)", expanded=True):
                    with st.container(height=150, border=True):
                        st.json(story_out.get("story_validation", {}))

                # 2. Stories Editor in Scrollable Box
                with st.expander(
                    "📝 Review & Edit Generated Stories JSON", expanded=True
                ):
                    with st.container(height=400, border=True):
                        edited_stories_str = st.text_area(
                            "Edit Stories JSON:",
                            stories_str,
                            height=1000,  # Large inner height
                            label_visibility="collapsed",
                        )

                    if st.button("Save & Confirm Stories"):
                        try:
                            st.session_state.context_stories = json.loads(
                                edited_stories_str
                            )
                            st.success("Stories saved! Ask 'Push to Jira'.")
                        except json.JSONDecodeError:
                            st.error("Invalid JSON format.")

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": "User stories generated. Review above.",
                    }
                )
                st.session_state.messages.append(
                    {"role": "assistant", "content": stories_str}
                )

    # --- CASE D: Jira ---
    elif intent_type == "action_jira":
        if not st.session_state.context_stories:
            st.error("⚠️ No stories found.")
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
