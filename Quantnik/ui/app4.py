import streamlit as st
import json
import sys, os

# --- Path Setup ---
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)
from backend.src.agents.requirement_agent import RequirementAgent

# --- Initialize Agent ---
if "pipeline" not in st.session_state:
    st.session_state.pipeline = RequirementAgent()

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

# =========================================================
# 📂 SIDEBAR: FILE UPLOADER
# =========================================================
with st.sidebar:
    st.header("📂 Input Source")
    st.write("Upload your Minutes of Meeting (MOM) here:")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:
        # Save the uploaded file to a temporary path
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
st.title("🤖 Project AI Assistant")

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle User Input
if user_input := st.chat_input(
    "Type here... (e.g., 'Generate BRD from the uploaded file')"
):

    # 1. Append User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Process Intent via Agent
    with st.spinner("Thinking..."):
        # Pass current context just in case
        response_payload = st.session_state.pipeline.process_user_message(
            user_input, current_context=st.session_state.context_brd
        )

    intent_type = response_payload.get("type")
    bot_reply = response_payload.get("message")
    extracted_data = response_payload.get("input_data")

    # 3. Handle Actions based on Intent

    # --- CASE A: Normal Chat ---
    if intent_type == "chat":
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # --- CASE B: Generate BRD (Handles PDF vs Text) ---
    elif intent_type == "action_brd":
        with st.chat_message("assistant"):
            st.markdown(bot_reply)  # "Sure, generating BRD..."

            # 🔍 INPUT SOURCE LOGIC:
            # 1. If LLM extracted text from the chat prompt, use that.
            # 2. If not, check if a PDF is uploaded in the sidebar.
            # 3. Else, error out.

            final_input = None
            source_label = ""

            if extracted_data and len(extracted_data) > 20:
                # Heuristic: If prompt has substantial text, assume it's the MOM
                final_input = extracted_data
                source_label = "chat text"
            elif st.session_state.temp_pdf_path:
                # Fallback to the uploaded PDF
                final_input = st.session_state.temp_pdf_path
                source_label = "uploaded PDF"
            else:
                st.error(
                    "⚠️ I need input data! Please paste the MOM text in the chat OR upload a PDF in the sidebar."
                )
                st.stop()

            st.info(f"🔄 Reading from {source_label} and generating BRD...")

            # Call Pipeline
            flag, brd_out = st.session_state.pipeline.brd_generation_and_validation(
                input_text=final_input
            )

            st.success("✅ BRD Generated!")
            st.session_state.context_brd = brd_out.get("brd_text", "")

            # Editable BRD Container
            with st.expander("📄 Review Generated BRD", expanded=True):
                edited_brd = st.text_area(
                    "Edit BRD:", st.session_state.context_brd, height=300
                )
                if st.button("Save & Confirm BRD"):
                    st.session_state.context_brd = edited_brd
                    st.info("BRD Saved. You can now ask: 'Generate user stories'.")

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "I have generated the BRD from your input. Please review it above.",
                }
            )


    # --- CASE C: Generate Stories ---
    elif intent_type == "action_stories":
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

                if flag:
                    st.session_state.context_stories = story_out.get("stories", {})

                    with st.expander("📝 Review User Stories", expanded=True):
                        stories_str = json.dumps(
                            st.session_state.context_stories, indent=2
                        )
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
                            except:
                                st.error("Invalid JSON format.")

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": "User stories generated. Review them above.",
                        }
                    )

    # --- CASE D: Create Jira Tickets ---
    elif intent_type == "action_jira":
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
