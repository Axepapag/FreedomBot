from mentor_llm import MentorLLM

class Planner:
    def __init__(self):
        self.llm = MentorLLM()

    def plan(self, user_goal, memory=None):
        prompt = (
    "You are a task planner agent for Dexter. Given the following goal, "
    "break it down into clear, executable steps. Reply in valid JSON: {\"plan\": [ ... ]}.\n"
    f"Goal: {user_goal}\n"
    f"Memory: {memory.mem if memory else '{}'}\n"


        )
        resp = self.llm.ask(prompt)
        import json
        try:
            start = resp.find("{")
            end = resp.rfind("}")
            if start == -1 or end == -1:
                return ["Could not parse plan: " + resp]
            plan_obj = json.loads(resp[start:end+1])
            return plan_obj.get("plan", ["No plan found."])
        except Exception as e:
            return [f"Planning error: {e} | Resp: {resp}"]
