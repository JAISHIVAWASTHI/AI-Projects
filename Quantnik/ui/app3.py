import streamlit as st
import json
import sys, os

# --- Path Setup ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from backend.src.agents.requirement_agent import RequirementAgent

# Initialize Agent
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = RequirementAgent()

st.set_page_config(page_title="Project AI Assistant", layout="centered")
st.title("🤖 Project AI Assistant")

# --- Session State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I can help you generate BRDs, User Stories, or create Jira tickets. How can I help you today?"}]

if "context_brd" not in st.session_state:
    st.session_state.context_brd = ""
if "context_stories" not in st.session_state:
    st.session_state.context_stories = {}

# --- Display Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Handle User Input ---
if user_input := st.chat_input("Type your message here..."):
    # 1. Display User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Process Intent via Agent
    with st.spinner("Thinking..."):
        # We pass current context just in case the intent relies on previous steps
        response_payload = st.session_state.pipeline.process_user_message(
            user_input, 
            current_context=st.session_state.context_brd
        )

    intent_type = response_payload.get("type")
    bot_reply = response_payload.get("message")

    # 3. Handle Actions based on Intent
    
    # --- CASE A: Normal Chat ---
    if intent_type == "chat":
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # --- CASE B: Generate BRD ---
    elif intent_type == "action_brd":
        with st.chat_message("assistant"):
            st.markdown(bot_reply) # "Sure, I'll generate the BRD..."
            
            status_placeholder = st.empty()
            status_placeholder.info("🔄 Generating BRD from input text...")
            
            # Call Actual BRD Function
            flag, brd_out = st.session_state.pipeline.brd_generation_and_validation(
                input_text=response_payload.get("input_data")
            )
            
            status_placeholder.empty()
            
            if flag:
                st.success("✅ BRD Generated!")
                st.session_state.context_brd = brd_out.get("brd_text", "")
                
                # Show Editable BRD in Chat (using expander for cleanness)
                with st.expander("📄 Review Generated BRD", expanded=True):
                    edited_brd = st.text_area("Edit BRD:", st.session_state.context_brd, height=300)
                    if st.button("Save & Confirm BRD"):
                        st.session_state.context_brd = edited_brd
                        st.info("BRD Saved. You can now ask me to generate stories.")
                
                # Add system note to history
                st.session_state.messages.append({"role": "assistant", "content": "I have generated the BRD. Please review it above."})
            else:
                st.error("❌ Failed to generate valid BRD.")

    # --- CASE C: Generate Stories ---
    elif intent_type == "action_stories":
        if not st.session_state.context_brd:
            st.error("⚠️ I don't have a BRD yet. Please ask me to generate a BRD first.")
        else:
            with st.chat_message("assistant"):
                st.markdown(bot_reply)
                with st.spinner("🔄 Generating User Stories..."):
                    flag, story_out = st.session_state.pipeline.story_generation_and_validation(st.session_state.context_brd)
                
                if flag:
                    st.session_state.context_stories = story_out.get("stories", {})
                    
                    with st.expander("📝 Review User Stories", expanded=True):
                        # Convert to JSON string for editing
                        stories_str = json.dumps(st.session_state.context_stories, indent=2)
                        edited_stories_str = st.text_area("Edit Stories JSON:", stories_str, height=300)
                        
                        if st.button("Save & Confirm Stories"):
                            try:
                                st.session_state.context_stories = json.loads(edited_stories_str)
                                st.success("Stories saved! You can now ask me to create Jira tickets.")
                            except:
                                st.error("Invalid JSON format.")

                    st.session_state.messages.append({"role": "assistant", "content": "I have generated the user stories based on the BRD."})

    # --- CASE D: Create Jira Tickets ---
    elif intent_type == "action_jira":
        if not st.session_state.context_stories:
            st.error("⚠️ I don't have any stories to push. Please generate stories first.")
        else:
             with st.chat_message("assistant"):
                st.markdown(bot_reply)
                with st.spinner("🔄 Pushing tickets to Jira..."):
                    flag, msg = st.session_state.pipeline.create_jira_tickets(st.session_state.context_stories)
                
                if flag:
                    st.success(f"✅ {msg}")
                    st.session_state.messages.append({"role": "assistant", "content": f"Success: {msg}"})
                else:
                    st.error(f"❌ Failed: {msg}")