# dexter.py
from mentor_llm import MentorLLM
from memory import Memory
from skill_registry import SkillRegistry
from sandbox import Sandbox
from logs import Logger
from knowledge_graph import KnowledgeGraph
from planner import Planner
from reflection import Reflector
from agents import AgentManager
from corrections import Corrections

class Dexter:
    def __init__(self, memory, skills, mentor, sandbox, logger, knowledge_graph):
        self.memory = memory
        self.skills = skills
        self.mentor = mentor
        self.sandbox = sandbox
        self.logger = logger
        self.knowledge_graph = knowledge_graph

        # New brain modules
        self.planner = Planner()
        self.reflector = Reflector()
        self.agent_manager = AgentManager()
        self.corrections = Corrections()

    def handle_input(self, user_input: str) -> str:
        self.memory.save_chat("user", user_input)

        # --- CORRECTION HANDLING ---
        if user_input.lower().startswith("correct:"):
            try:
                _, payload = user_input.split(":", 1)
                original, correction = payload.split("->", 1)
                original = original.strip()
                correction = correction.strip()
                self.corrections.add(original, correction, context="user correction")
                self.memory.save_chat("dexter", "Correction saved.")
                return "Correction saved and will be considered for future responses."
            except Exception as e:
                return f"Failed to save correction: {e}"

        # --- AGENT HANDLING (review/test/research) ---
        if user_input.lower().startswith("review:"):
            code = user_input[len("review:"):].strip()
            review = self.agent_manager.call("code_reviewer", code, self.memory)
            self.memory.save_chat("dexter", review)
            return review
        if user_input.lower().startswith("test:"):
            code = user_input[len("test:"):].strip()
            tests = self.agent_manager.call("test_writer", code, self.memory)
            self.memory.save_chat("dexter", tests)
            return tests
        if user_input.lower().startswith("research:"):
            topic = user_input[len("research:"):].strip()
            research = self.agent_manager.call("researcher", topic, self.memory)
            self.memory.save_chat("dexter", research)
            return research

        # --- PLANNING (multi-step/complex requests) ---
        if user_input.lower().startswith("plan:"):
            user_goal = user_input[len("plan:"):].strip()
            plan = self.planner.plan(user_goal, self.memory)
            self.memory.save_chat('dexter', f"Planning for goal: {user_goal}\nPlan: {plan}")
            response = f"Here’s my plan:\n" + "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
            return response

        # --- COMPLEXITY DETECTION & AUTO-PLANNING (optional) ---
        if self._is_complex(user_input):
            plan = self.planner.plan(user_input, self.memory)
            results = []
            for i, step in enumerate(plan):
                result, error = self._execute_step(step)
                results.append(f"Step {i+1}: {step}\nResult: {result}\n")
                reflection = self.reflector.reflect(step, result, error, self.memory)
                if not reflection.get("success", True):
                    fix = reflection.get("fix", "")
                    comment = reflection.get("comment", "")
                    results.append(f"Reflection: {comment}\nSuggested fix: {fix}\n")
                    # Optionally, auto-apply fix/patch if it's code
            final = "\n".join(results)
            self.memory.save_chat("dexter", final)
            return final

        # --- SKILL HANDLING (default intent) ---
        skill = self.skills.match_skill(user_input)
        if skill:
            try:
                output = skill.run(user_input, self)
                self.memory.save_chat("dexter", output)
                return output
            except Exception as e:
                self.memory.save_chat("dexter", f"Skill error: {e}")
                return f"Skill error: {e}"

        # --- FALLBACK TO LLM ---
        output = self.mentor.ask(user_input)
        self.memory.save_chat("dexter", output)
        return output

    def _is_complex(self, user_input):
        # Basic heuristic: long, multi-step, or uses "and/then/after"
        u = user_input.lower()
        if any(kw in u for kw in [" and ", " then ", " after ", "first", "second", "third", "next", "step"]):
            return True
        if len(u.split()) > 25:
            return True
        return False

    def _execute_step(self, step):
        # Try skill match first
        skill = self.skills.match_skill(step)
        if skill:
            try:
                return skill.run(step, self), None
            except Exception as e:
                return None, str(e)
        # Otherwise, fallback to LLM
        try:
            return self.mentor.ask(step), None
        except Exception as e:
            return None, str(e)