import traceback
from memory import Memory
from mentor_llm import MentorLLM
from reflection import Reflector
from skill_registry import SkillRegistry
from sandbox import test_code
import os
import re

class DexterBrain:
    def __init__(self):
        self.memory = Memory()
        self.llm = MentorLLM()
        self.reflector = Reflector()
        self.skills = SkillRegistry()
        self.pending_patch = None

    def handle_input(self, user_input: str) -> dict:
        try:
            # Handle patch confirmation
            if user_input.strip().lower() == "yes" and self.pending_patch:
                success = self.apply_patch(self.pending_patch)
                self.pending_patch = None
                return {"response": "✅ Patch applied successfully." if success else "❌ Patch failed."}

            if user_input.strip().lower() == "no" and self.pending_patch:
                self.pending_patch = None
                return {"response": "❎ Patch cancelled."}

            # Execute matching skill if exists
            skill_output = self.skills.match_and_run(user_input)
            if skill_output:
                self.memory.add_interaction(user_input, skill_output, priority=0.8)
                return {"response": skill_output}

            # Otherwise, use LLM to respond
            context = self.memory.get_context()
            response = self.llm.ask(user_input, context)

            # Check for patch intent
            if self._looks_like_patch_request(user_input, response):
                if test_code(response):
                    self.pending_patch = response
                    return {
                        "response": (
                            f"Mentor generated this code (sandbox test PASSED):\n"
                            f"{response}\n\n"
                            "Apply this patch? Reply with 'yes' to apply, or 'no' to cancel."
                        )
                    }

            self.memory.add_interaction(user_input, response, priority=0.5)
            return {"response": response}

        except Exception as e:
            return {
                "error": str(e),
                "trace": traceback.format_exc()
            }

    def _looks_like_patch_request(self, user_input: str, llm_response: str) -> bool:
        code_block_present = "```python" in llm_response
        trigger_keywords = ["patch", "fix", "update", "modify", "change", "replace", "code"]
        user_asked_for_patch = any(k in user_input.lower() for k in trigger_keywords)
        return code_block_present and user_asked_for_patch

    def apply_patch(self, code_block: str) -> bool:
        try:
            code = re.search(r"```python(.*?)```", code_block, re.DOTALL).group(1).strip()
            filepath = "skills/manual_patch.py"
            os.makedirs("skills", exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
            return True
        except Exception as e:
            print(f"[Patch Error] {e}")
            return False