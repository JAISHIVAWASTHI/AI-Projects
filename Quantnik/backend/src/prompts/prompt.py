import os
import yaml


class PromptManager:
    def __init__(self, prompt_dir="D:\AI\AI-Projects\Quantnik/backend\src\prompts"):
        self.prompt_dir = prompt_dir

    def load_prompt(self, prompt_name: str) -> dict:
        file_path = os.path.join(self.prompt_dir, f"{prompt_name}.yaml")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        prompt_data = self.load_prompt(prompt_name)
        prompt_template = prompt_data["template"]

        # Replace placeholders like {{PDF_TEXT}}
        for key, value in kwargs.items():
            placeholder = f"{{{{{key}}}}}"
            prompt_template = prompt_template.replace(placeholder, value)

        return prompt_template


# kk = PromptManager()
# print(kk.get_prompt("generate_brd"))
