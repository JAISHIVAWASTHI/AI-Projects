"""
Author: Jaishiv Awasthi
Date: 3 Nov 2025
"""

import sys, os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
            )
        )
    )
)

import json
import re
from typing import List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_community.document_loaders import PyPDFLoader
from backend.src.models.llama import LLAMA
from backend.src.models.deep_seek_r1_t2 import DEEPSEEKR1T2
from backend.src.prompts.prompt import PromptManager
from backend.src.services.jira_servies import JIRASERVICE
from backend.src.utils.jira_handler import create_jira_ticket
from backend.src.utils.tools import (
    save_text_to_file,
    read_text_to_file,
    load_dict_json,
    save_dict_json,
    convert_to_project_key,
)


class RequirementAgent:
    """Requirement Extraction Agent"""

    def __init__(self):
        # self.llm_bot = LLAMA()
        self.llm_bot = DEEPSEEKR1T2()
        self.prompts = PromptManager()
        self.jira_service = JIRASERVICE()

    def read_pdf_file(self, file_path: str) -> str:
        """Read PDF safely and return text."""
        try:
            loader = PyPDFLoader(file_path)
            pages = loader.load()

            if not pages:
                raise ValueError("PDF loaded but pages are empty.")

            text = "\n".join(p.page_content.strip() for p in pages if p.page_content)
            return text or ""

        except FileNotFoundError:
            print(f"PDF not found: {file_path}")
            return ""

        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""

    def generate_brd(self, pdf_text: str) -> str:
        """Generate BRD from PDF text via LLM."""
        if not pdf_text.strip():
            return False, "No PDF text provided to generate BRD"

        prompt = self.prompts.get_prompt("generate_brd", PDF_TEXT=pdf_text)

        try:
            response = self.llm_bot.llm_bot(prompt)
            return True, response.strip()

        except Exception as e:
            print(f"BRD generation failed: {e}")
            return False, "Failed to generate BRD"

    def validate_brd_completeness(self, brd_text: str, minimum_confidence: int = 50):
        """Validate BRD completeness and readiness to generate user stories."""
        if not brd_text or len(brd_text.strip()) < 50:
            return False, {
                "missing_sections": ["Entire document"],
                "completeness_confidence": 0,
                "comments": "BRD content too short or missing.",
            }

        # Generate validation prompt
        validation_prompt = self.prompts.get_prompt(
            "validate_brd_completeness", BRD_TEXT=brd_text
        )

        # Run through LLM
        validation_output = self.llm_bot.llm_bot(validation_prompt).strip()
        try:
            validation_json = json.loads(validation_output)
        except json.JSONDecodeError:
            # Try extracting the JSON part
            match = re.search(r"\{.*\}", validation_output, re.DOTALL)
            if match:
                cleaned_text = match.group(0)
            else:
                cleaned_text = validation_output

            # Fix unquoted keys: {is_complete: true} → {"is_complete": true}
            cleaned_text = re.sub(
                r"([{,]\s*)([A-Za-z0-9_]+)\s*:", r'\1"\2":', cleaned_text
            )

            try:
                validation_json = json.loads(cleaned_text)
            except Exception as e:
                print(f"JSON parsing failed: {e}")
                return False, {
                    "missing_sections": ["Parsing Error"],
                    "completeness_confidence": 0,
                    "comments": "Model output not valid JSON.",
                    "raw_output": validation_output,
                }

        # Validate fields
        # is_complete = (
        #     validation_json.get("is_complete", False)
        #     and validation_json.get("completeness_confidence", 0) >= minimum_confidence
        # )

        # TODO correct the logic
        is_complete = (
            validation_json.get("completeness_confidence", 0) >= minimum_confidence
        )

        return is_complete, validation_json

    def parse_json_from_model(self, response: str) -> List[Dict[str, Any]]:
        """Force-extract JSON cleanly even if LLM adds markdown/noise"""
        try:
            return json.loads(response)
        except:
            match = re.search(r"\[.*\]", response, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except:
                    pass
        return []

    def parse_and_repair_json_from_model(self, text: str):
        """
        Extracts and repairs JSON from LLM output.
        """
        try:
            # Step 1: Extract JSON using regex
            json_match = re.search(r"\{[\s\S]*\}", text.strip())
            if not json_match:
                raise ValueError("No JSON found in model output")

            json_str = json_match.group(0)

            # Step 2: Auto-fix common JSON issues ------------------

            # Remove duplicate keys or broken repeated blocks
            json_str = re.sub(r",\s*}", "}", json_str)
            json_str = re.sub(r",\s*]", "]", json_str)

            # Fix missing commas between objects
            json_str = re.sub(r"\}\s*\{", "}, {", json_str)

            # Remove repeated incomplete objects (common LLM hallucination)
            json_str = re.sub(r"\{[^{}]*$", "", json_str)

            # Step 3: Try normal JSON parsing
            try:
                return json.loads(json_str)
            except:
                pass  # fallback to repair

            # Step 4: If still failing, use JSON repair
            from json_repair import repair_json

            fixed = repair_json(json_str)

            return json.loads(fixed)

        except Exception as e:
            print("JSON parsing failed:", e)
            return {}

    def generate_user_stories(self, brd_text: str):
        """Create Jira-ready user stories from BRD"""
        if not brd_text.strip():
            return {}

        prompt = self.prompts.get_prompt("user_story", BRD_TEXT=brd_text)

        try:
            raw = self.llm_bot.llm_bot(prompt)
            stories = self.parse_and_repair_json_from_model(raw)
            if not isinstance(stories, dict):
                print("Parsed result is not a dict")
                return {}

            return stories

        except Exception as e:
            print(f"Failed to generate user stories: {e}")
            return {}

    def user_story_validator(self, text: str, minimum_confidence: int = 70):
        """User story validator"""
        try:
            # Try to parse directly
            json_data = json.loads(text)
        except json.JSONDecodeError:
            # Clean up JSON-like text (handles cases like missing quotes or trailing commas)
            cleaned_text = re.search(r"\{.*\}", text, re.DOTALL)
            if cleaned_text:
                try:
                    json_data = json.loads(cleaned_text.group())
                except Exception as e:
                    raise ValueError(f"Unable to parse JSON from response: {e}")
            else:
                raise ValueError("No valid JSON object found in response")

        # Step 2: Extract confidence as integer or float
        confidence_value = json_data.get("alignment_confidence", "0")
        if isinstance(confidence_value, str):
            confidence_value = re.findall(r"\d+", confidence_value)
            confidence_value = float(confidence_value[0]) if confidence_value else 0.0

        # Step 3: Check threshold
        is_aligned = confidence_value >= minimum_confidence

        return is_aligned, json_data

    def detect_pdf_input(self, input_text: str) -> str:
        """
        Detect whether the given input is:
        - A PDF file path
        - Raw PDF text content
        - Invalid input

        Returns:
        "pdf_path" → if valid PDF file path
        "pdf_text" → if text content (not a file)
        "invalid"  → if neither
        """

        # Strip whitespace
        cleaned = input_text.strip()

        # Case 1: Check if it's an actual file path
        if cleaned.lower().endswith(".pdf") and os.path.exists(cleaned):
            return "pdf_path"

        # Case 2: Input resembles raw PDF text
        # Common indicators of extracted PDF text
        pdf_indicators = [
            "page",
            "section",
            "table",
            "abstract",
            "purpose",
            "scope",
            "objective",
            "requirement",
            "introduction",
            "background",
            "mom",
            "minutes of meeting",
        ]

        # Make sure it's not accidentally a short string
        if len(cleaned) > 100:
            matches = sum(1 for x in pdf_indicators if x.lower() in cleaned.lower())
            if matches >= 2:
                return "pdf_text"

        # When the file path doesn't exist but looks like a PDF path
        if cleaned.lower().endswith(".pdf") and not os.path.exists(cleaned):
            return "invalid"

        # Not PDF text and not a valid path
        return "invalid"

    def brd_generation_and_validation(self, input_text):
        """BRD Generation and Validation"""
        val = self.detect_pdf_input(input_text)
        if val == "pdf_path":
            text = self.read_pdf_file(input_text)
        elif val == "pdf_text":
            text = input_text
        else:
            return False, {
                "brd_text": " Invalid Input file/text",
                "brd_validation": {},
            }
        flag, brd_text = self.generate_brd(text)
        if not flag:
            return False, {
                "brd_text": "Failed to generate BRD Text",
                "brd_validation": {},
            }
        save_text_to_file(
            brd_text, r"D:\AI\AI-Projects/Product_generatror\docs\brd.txt"
        )
        is_complete, validation_json = self.validate_brd_completeness(brd_text)

        print(
            "BRD Completeness Confidence:",
            validation_json.get("completeness_confidence"),
        )
        print("BRD Status:", "Complete" if is_complete else "Incomplete")
        print("Missing Sections:", validation_json.get("missing_sections"))

        if not is_complete:
            print("Aborting: BRD is not complete enough to generate user stories.")
            return False, {
                "brd_validation": validation_json,
                "brd_text": brd_text,
            }

        return True, {
            "brd_validation": validation_json,
            "brd_text": brd_text,
        }

    def story_generation_and_validation(self, brd_text):
        """Story geneartion and validation"""
        # print("Reading BRD Text......")
        # brd_text = read_text_to_file(
        #     r"D:\AI\AI-Projects/Product_generatror\docs\brd.txt"
        # )
        print("Generating User Stories......")
        stories = self.generate_user_stories(brd_text)
        if not stories:
            return False, {
                "stories": "failed to generate stories",
                "story_validation": {},
            }

        validation_prompt = self.prompts.get_prompt(
            "validate_story_with_brd",
            BRD_TEXT=brd_text,
            STORIES_TEXT=str(stories),
        )
        print("Validating User Stories........")
        validation_output = self.llm_bot.llm_bot(validation_prompt)

        try:
            is_valid, validation_json = self.user_story_validator(validation_output)
        except Exception as e:
            print(f"Error during validation: {e}")
            return False, {
                "story_validation": {"Error": "Failed to validate stories"},
                "stories": stories,
            }

        print("Validation Confidence:", validation_json.get("alignment_confidence"))
        print("Validation Status:", "Passed" if is_valid else "Failed")
        # save_dict_json(
        #     "D:\\AI\\AI-Projects\\Product_generatror\\docs\\user_stories.json", stories
        # )
        return True, {
            "story_validation": validation_json,
            "stories": stories,
        }

    def create_jira_tickets(self, data):
        """create jira ticket"""
        # flag, data = load_dict_json(
        #     "D:\\AI\\AI-Projects\\Product_generatror\\docs\\user_stories.json"
        # )
        # if not flag:
        #     return False, "Failed to load user stories"
        # data["project_title"] = data["project_title"]
        data["project_key"] = convert_to_project_key(data["project_key"])

        try:
            return self.jira_service.jira_runner(data)

        except Exception as e:
            print("Error:- ", e)
            return False, "Failed to execute"

    def runner(self, pdf_path: str):
        """Main LangGraph pipeline runner"""

        def step_read_pdf(state):
            text = self.read_pdf_file(pdf_path)
            return {"pdf_text": text}

        def step_brd(state):
            flag, brd = self.generate_brd(state["pdf_text"])
            if not flag:
                raise ValueError("BRD generation failed — got empty text.")
            save_text_to_file(brd, r"D:\AI\AI-Projects/Product_generatror\docs\brd.txt")
            return {"brd_text": brd}

        def step_validate_brd(state):
            """Step: Validate BRD completeness before generating stories."""
            brd_text = state.get("brd_text", "")
            if not brd_text:
                raise KeyError("Missing BRD text for validation.")

            is_complete, validation_json = self.validate_brd_completeness(brd_text)

            print(
                "BRD Completeness Confidence:",
                validation_json.get("completeness_confidence"),
            )
            print("BRD Status:", "Complete" if is_complete else "Incomplete")
            print("Missing Sections:", validation_json.get("missing_sections"))

            if not is_complete:
                print("Aborting: BRD is not complete enough to generate user stories.")
                return {
                    "abort": True,
                    "brd_validation": validation_json,
                    "message": "BRD is incomplete — please review missing sections before proceeding.",
                }

            return {
                "abort": False,
                "brd_validation": validation_json,
                "brd_text": brd_text,
                "message": "BRD validated successfully.",
            }

        def step_user_stories(state):
            stories = self.generate_user_stories(state["brd_text"])
            if not stories:
                raise ValueError("User story generation failed — got empty stories.")
            return {
                "stories": stories,
                "brd_validation": state["brd_validation"],
                "brd_text": state["brd_text"],
            }

        def step_validate_stories(state):
            validation_prompt = self.prompts.get_prompt(
                "validate_story_with_brd",
                BRD_TEXT=state.get("brd_text", ""),
                STORIES_TEXT=str(state.get("stories", "")),
            )

            validation_output = self.llm_bot.llm_bot(validation_prompt)

            try:
                is_valid, validation_json = self.user_story_validator(validation_output)
            except Exception as e:
                print(f"Error during validation: {e}")
                return {
                    "validation_result": "Error during story validation",
                    "confidence": 0,
                    "story_validation": {},
                    "stories": state["stories"],
                    "brd_validation": state["brd_validation"],
                    "brd_text": state["brd_text"],
                }

            print("Validation Confidence:", validation_json.get("alignment_confidence"))
            print("Validation Status:", "Passed" if is_valid else "Failed")

            return {
                "validation_result": "Passed" if is_valid else "Failed",
                "confidence": validation_json.get("alignment_confidence"),
                "story_validation": validation_json,
                "stories": state["stories"],
                "brd_validation": state["brd_validation"],
                "brd_text": state["brd_text"],
            }

        # Build LangGraph
        graph = StateGraph(dict)
        graph.add_node("read_pdf", step_read_pdf)
        graph.add_node("create_brd", step_brd)
        graph.add_node("validate_brd", step_validate_brd)
        graph.add_node("create_stories", step_user_stories)
        graph.add_node("validate_stories", step_validate_stories)

        graph.set_entry_point("read_pdf")
        graph.add_edge("read_pdf", "create_brd")
        graph.add_edge("create_brd", "validate_brd")
        graph.add_conditional_edges(
            "validate_brd",
            lambda state: "end" if state.get("abort") else "continue",
            {"end": END, "continue": "create_stories"},
        )

        graph.add_edge("create_stories", "validate_stories")
        graph.add_edge("validate_stories", END)

        app = graph.compile()
        return app.invoke({})

    def process_user_message(self, user_input, current_context=None):
        """
        Analyzes user input to determine intent:
        1. General Chat -> Returns a chat response.
        2. BRD Gen -> Triggers BRD generation.
        3. Story Gen -> Triggers Story generation.
        4. Jira Ticket -> Triggers Jira creation.
        """

        # 1. Define the System Prompt for Intent Classification
        classification_prompt = f"""
        You are an intelligent project manager assistant. analyze the user's input and classify their intent into exactly one of these categories:
        
        1. "GENERAL_CHAT": The user is greeting, asking a general question, or making small talk.
        2. "GENERATE_BRD": The user wants to generate a Business Requirement Document (BRD) from raw text or MOM.
        3. "GENERATE_STORIES": The user wants to generate User Stories from a BRD.
        4. "CREATE_TICKETS": The user wants to push/create tickets on Jira.

        User Input: "{user_input}"
        
        Return your response in strict JSON format like this:
        {{
            "intent": "CATEGORY_NAME",
            "reply": "A polite, short response to the user acknowledging the action or answering their chat.",
            "data": "Extracted relevant text from input if applicable (e.g., the MOM text for BRD gen)"
        }}
        """

        # 2. Call the LLM
        # Assuming self.llm_bot.llm_bot returns a string response
        try:
            print("Classifying user intent...")
            response_text = self.llm_bot.llm_bot(classification_prompt)
            if not response_text:
                raise ValueError("Failed to run LLM")
            # Clean up potential markdown formatting from LLM (e.g., ```json ... ```)
            response_text = (
                response_text.replace("```json", "").replace("```", "").strip()
            )
            parsed_response = json.loads(response_text)
        except Exception as e:
            # Fallback if LLM fails or returns bad JSON
            return {
                "intent": "GENERAL_CHAT",
                "reply": "I'm sorry, I couldn't understand that. Could you please rephrase?",
                "data": None,
                "error": str(e),
            }

        intent = parsed_response.get("intent")
        reply = parsed_response.get("reply")
        data = parsed_response.get("data")

        # 3. Route based on Intent
        result_payload = {"type": "chat", "message": reply}

        if intent == "GENERATE_BRD":
            # If the user provided the text in the prompt, use it. Otherwise, asking might be needed.
            # Ideally, you pass the 'data' to your function.
            result_payload["type"] = "action_brd"
            result_payload["input_data"] = (
                data or user_input
            )  # Fallback to full input if extraction failed

        elif intent == "GENERATE_STORIES":
            result_payload["type"] = "action_stories"
            result_payload["input_data"] = (
                current_context  # Might need previous BRD context
            )

        elif intent == "CREATE_TICKETS":
            result_payload["type"] = "action_jira"
            result_payload["input_data"] = (
                current_context  # Might need previous Stories context
            )

        return result_payload


# kk = RequirementAgent()
# print(
#     kk.runner("D:\AI\AI-Projects\Product_generatror\docs\MOM of calculator project.pdf")
# )
text = """
--
# ** Minutes of Meeting (MOM)**
**Project:** Calculator Application Development
**Date:** 12-11-2025
**Time:** 11:00 AM – 12:00 PM IST
**Location:** Project Conference Room / MS Teams
**Meeting Type:** Requirement Gathering & Project Kick-off Meeting--
## **1. Attendees**
| Name                   
 | 
Role                           
 |
| ----------------------- | ------------------------------- |
| **Mr. Rohan Verma**     | Product Manager                 
| **Ms. Neha Kapoor**     | Business Analyst               
| **Mr. Amit Sharma**     | Engineering Manager             
| **Ms. Priya Nair**     
 | 
QA Lead                         
| **Mr. Siddharth Singh** | UX/UI Designer                 
| **Mr. Rajeev Mehta**    | Project Sponsor                 
|
|
 |
 |
|
|
| **Mr. Jaishiv Awasthi** | AI/ML & Software Engineer (Dev) |--
## **2. Meeting Objective**
To gather and finalize the business requirements for the **Calculator Application**, establish 
scope, define features, identify constraints, and outline next steps to proceed with BRD creation 
and story development.--
## **3. Project Overview**
The goal is to develop a **simple, cross-platform Calculator Application** supporting basic 
arithmetic operations with clean UI, high accuracy, and error-free handling.
The calculator will be initially available as a **web application**, with future consideration for 
mobile.
--
## **4. Business Requirements Discussed**
### **4.1 Core Features**
1. **Addition (+)**
2. **Subtraction (–)**
3. **Multiplication (×)**
4. **Division (÷)**
5. **Clear / Reset functionality**
6. **Decimal number support**
7. **Keyboard input support**
8. **Responsive UI for web**--
### **4.2 Non-Functional Requirements**
1. **Performance:**
 * All operations should respond within **<100 ms**.
2. **Usability:**
 * Buttons must be large, clear, and accessible.
3. **Compatibility:**
 * Supports Chrome, Firefox, Edge (latest 2 versions).
4. **Scalability:**
 * Architecture prepared for adding advanced functions later.
5. **Security:**
 * No user data stored; safe execution in browser sandbox.
6. **Reliability:**
 * Controlled error handling such as division by zero.
--
### **4.3 User Interface Requirements**
1. Simple, clean layout with a keypad and display area.
2. Display area should show:
 * ongoing input
 * last operation performed
 * result
3. Mobile-friendly layout using responsive design.--
### **4.4 Constraints & Known Limitations**
* Initial phase includes **only basic arithmetic**.
* No scientific calculator features in Phase-1.
* No user login or persistence required.--
## **5. Technical Requirements**
1. **Frontend:** React / HTML+CSS+JS (final tech to be confirmed by engineering team).
2. **Backend:** Not required (client-side logic only).
3. **Testing:** Cypress or Jest for unit/UI tests.
4. **Deployment:** GitHub Pages / AWS S3 (final choice pending).--
## **6. Risks Identified**
1. Scope creep if advanced calculator features are requested later.
2. UI-performance issues on low-end mobile browsers (low impact).--
## **7. Deliverables & Owners**
| Deliverable                 
 | 
Owner                             
| Target Date |
| ---------------------------- | --------------------------------- | ----------- |
| Create BRD                   
| Business Analyst (Neha Kapoor)    | 15-11-2025  |
| UI Mockups                   
| Jira Stories                 
| UX Designer (Siddharth Singh)     | 17-11-2025  |
| Engineering Manager (Amit Sharma) | 20-11-2025  |
| Development Repository Setup | Dev Lead (Jaishiv Awasthi)       
 | 
| QA Test Plan                 
| QA Lead (Priya Nair)             
 | 
22-11-2025  |
25-11-2025  |--
## **8. Decisions Taken**
1. Phase-1 will include only basic features (Add, Sub, Mul, Div).
2. UI will be minimalistic and responsive.
3. Development will follow agile with 2-week sprints.
4. No backend server for v1.--
## **9. Action Items**
| Action Item                       
 | 
Owner           
| Deadline   |
| ---------------------------------- | --------------- | ---------- |
| Prepare BRD draft for approval     | Neha Kapoor     | 15-11-2025 |
| Create initial UI wireframes       
| Siddharth Singh | 17-11-2025 |
| Confirm tech stack after PoC       
| Amit Sharma     | 18-11-2025 |
| Set up Git repo + boilerplate code | Jaishiv Awasthi | 22-11-2025 |--
## **10. Next Meeting**
**Date:** 18-11-2025
**Agenda:**
* Review BRD
* Finalize UI
* Create sprint-1 plan--
## **11. Meeting Notes Summary**
The team aligned on creating a simple, accurate, browser-based calculator with basic features. 
UI will be easy-to-use, and architecture will allow future expansion. BA will draft BRD based on 
this MOM.--
"""
# print(kk.process_user_message(text))

# print(kk.brd_generation_and_validation(text))
# print(kk.story_generation_and_validation())
# print(kk.create_jira_tickets())

# print(kk.parse_and_repair_json_from_model(""))
