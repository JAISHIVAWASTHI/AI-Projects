import streamlit as st
import json
import sys, os
import time

# --- Path Setup ---
# Ensure the backend module is discoverable
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)
from backend.src.agents.requirement_agent import RequirementAgent

try:
    st.session_state.pipeline = RequirementAgent()
except ImportError:
    # --- MOCK PIPELINE FOR DEMO/TESTING ---
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
            time.sleep(1)
            is_valid = False
            validation = {
                "completeness": "40%",
                "missing_sections": ["Scope", "Success Criteria"],
            }
            brd_text = "DRAFT BRD:\n1. Objective: Project automation.\n2. Needs: Convert input to BRD, stories, and Jira tickets.\n---\n(Edit me to fix validation issues!)"
            return is_valid, {"brd_validation": validation, "brd_text": brd_text}

        def story_generation_and_validation(self, brd_text):
            time.sleep(1)
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
            time.sleep(1)
            num_tickets = len(stories_json)
            return True, f"Successfully created {num_tickets} Mock Jira tickets."

    st.session_state.pipeline = MockPipeline()

if "is_processing" not in st.session_state:
    st.session_state.is_processing = (
        False  # New state variable for sequential guardrail
    )


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


# --- HELPER FUNCTION: Stop Execution ---
def stop_execution():
    """Resets context and shows a message when the user stops the pipeline."""
    st.session_state.context_brd = ""
    st.session_state.context_stories = {}
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": "⛔ Pipeline stopped by the user. Context cleared. Please provide new input to start over.",
        }
    )
    st.session_state.is_processing = False
    st.rerun()


# --- HELPER FUNCTION: Save BRD and continue to next step (rerun) ---
def save_brd_and_continue(edited_brd):
    st.session_state.context_brd = edited_brd

    # ⭐ FIX 1: Add the final, edited BRD to the chat history
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": f"**✅ Confirmed BRD (Ready for Stories):**\n\n```markdown\n{edited_brd}\n```",
        }
    )
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": "BRD saved. You can now ask: **'Generate user stories'**.",
        }
    )
    st.session_state.is_processing = False
    st.rerun()


# --- HELPER FUNCTION: Save Stories and continue to next step (rerun) ---
def save_stories_and_continue(edited_stories_str):
    try:
        final_stories_json = json.loads(edited_stories_str)
        st.session_state.context_stories = final_stories_json

        # ⭐ FIX 2: Add the final, edited Stories JSON to the chat history
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": f"**✅ Confirmed User Stories (Ready for JIRA):**\n\n```json\n{edited_stories_str}\n```",
            }
        )
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": "Stories saved. You can now ask: **'Push these to Jira'**.",
            }
        )
        st.session_state.is_processing = False
        st.rerun()
    except json.JSONDecodeError:
        st.error("Invalid JSON format. Please correct it before continuing.")
        # Do not rerun or clear processing if the save fails due to bad JSON
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
        st.markdown(msg["content"])

# Handle User Input
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
    with st.spinner("Step 1/4: Analyzing intent..."):
        response_payload = st.session_state.pipeline.process_user_message(
            user_input, current_context=st.session_state.context_brd
        )

    intent_type = response_payload.get("type")
    bot_reply = response_payload.get("message")
    extracted_data = response_payload.get("input_data")

    # 3. Handle Actions based on Intent

    with st.chat_message("assistant"):
        st.markdown(bot_reply)

        # --- CASE A: Normal Chat ---
        if intent_type == "chat":
            st.session_state.messages.append(
                {"role": "assistant", "content": bot_reply}
            )
            st.session_state.is_processing = False

        # --- CASE B: Generate BRD (Handles PDF vs Text) ---
        elif intent_type == "action_brd":

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
                st.session_state.is_processing = False
                st.stop()

            # ❗ Use spinner for pipeline step
            with st.spinner(
                f"Step 2/4: Generating BRD from {source_label} and running validation..."
            ):
                flag, brd_out = st.session_state.pipeline.brd_generation_and_validation(
                    input_text=final_input
                )

            # --- Output & Review ---

            if not flag:
                st.warning(
                    "⚠️ **BRD Validation Failed!** Please review the validation data and edit the BRD to ensure completeness before continuing."
                )
            else:
                st.success("✅ BRD Generation and Validation Complete.")

            brd_text = brd_out.get("brd_text", "")
            st.session_state.context_brd = brd_text

            # Show Validation Data
            with st.expander("🔬 AI Validation Data (BRD)", expanded=False):
                st.json(brd_out.get("brd_validation", {}))

            # Editable BRD Container (Always shown)
            with st.expander("✏️ Review & Edit BRD", expanded=True):
                # Use st.form to group the text area and buttons for clearer reruns
                with st.form("brd_edit_form"):
                    edited_brd = st.text_area(
                        "Edit the BRD content here:",
                        brd_text,
                        height=300,
                        key="brd_editor",
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        # Call the helper function to save and proceed
                        st.form_submit_button(
                            "Save & Generate Stories ➡️",
                            type="primary",
                            on_click=save_brd_and_continue,
                            args=(edited_brd,),
                        )
                    with col2:
                        st.form_submit_button(
                            "Stop Pipeline ❌", on_click=stop_execution
                        )

            # If we reach here, the user is still in the review step (no button clicked yet)
            # Re-enable processing if they haven't explicitly stopped or proceeded
            st.session_state.is_processing = False
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "BRD generation complete. **Review the text above**, edit if needed, and click 'Save & Generate Stories' to proceed, or 'Stop Pipeline' to exit.",
                }
            )

        # --- CASE C: Generate Stories ---
        elif intent_type == "action_stories":
            if not st.session_state.context_brd:
                st.error("⚠️ I don't have a BRD yet. Please generate a BRD first.")
                st.session_state.is_processing = False
                st.rerun()
            else:
                # ❗ Use spinner for pipeline step
                with st.spinner(
                    "Step 3/4: Generating User Stories and running validation..."
                ):
                    flag, story_out = (
                        st.session_state.pipeline.story_generation_and_validation(
                            st.session_state.context_brd
                        )
                    )

                # --- Output & Review ---
                if not flag:
                    st.warning(
                        "⚠️ **Story Validation Failed!** Please review the validation data and ensure the Stories JSON is correct."
                    )
                else:
                    st.success("✅ Story Generation and Validation Complete.")

                stories = story_out.get("stories", {})
                try:
                    stories_str = json.dumps(stories, indent=2)
                except TypeError:
                    stories_str = str(stories)
                    st.error("Generated stories structure is invalid.")

                st.session_state.context_stories = stories

                # Show Validation Data
                with st.expander("🔬 AI Validation Data (Stories)", expanded=False):
                    st.json(story_out.get("story_validation", {}))

                # Editable Stories Container (Always shown)
                with st.expander("✏️ Review & Edit Stories JSON", expanded=True):
                    with st.form("stories_edit_form"):
                        edited_stories_str = st.text_area(
                            "Edit the Stories JSON here:",
                            stories_str,
                            height=300,
                            key="stories_editor",
                        )

                        col1, col2 = st.columns(2)
                        with col1:
                            # Call the helper function to save and proceed
                            st.form_submit_button(
                                "Save & Create JIRA Tickets 🚀",
                                type="primary",
                                on_click=save_stories_and_continue,
                                args=(edited_stories_str,),
                            )
                        with col2:
                            st.form_submit_button(
                                "Stop Pipeline ❌", on_click=stop_execution
                            )

                # Re-enable processing if they haven't explicitly stopped or proceeded
                st.session_state.is_processing = False
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": "Stories generation complete. **Review the JSON above**, edit if needed, and click 'Save & Create JIRA Tickets' to proceed, or 'Stop Pipeline' to exit.",
                    }
                )

        # --- CASE D: Create Jira Tickets ---
        elif intent_type == "action_jira":
            if not st.session_state.context_stories:
                st.error("⚠️ No stories found. Please generate stories first.")
                st.session_state.is_processing = False
                st.rerun()
            else:
                # ❗ Use spinner for pipeline step
                with st.spinner("Step 4/4: Pushing tickets to Jira..."):
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

                # Clear context after final step
                st.session_state.context_brd = ""
                st.session_state.context_stories = {}
                st.session_state.is_processing = False

    # The use of st.form ensures that the on_click actions trigger the rerun
    # and update the messages correctly before the next interaction.
    if st.session_state.is_processing:
        # If the processing flag is still True (meaning no save/stop button was hit,
        # or the LLM intent was chat/failed intent), we must reset it or the input will be disabled.
        st.session_state.is_processing = False

    st.rerun()
