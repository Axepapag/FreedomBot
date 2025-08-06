from mentor_llm import MentorLLM

class Reflector:
    def __init__(self):
        self.llm = MentorLLM()

    def reflect(self, step, result, error=None, memory=None):
        prompt = (
            "You are a self-improvement agent for Dexter. Analyze the following step, "
            "its result, and any error. Was it successful? If not, suggest how to fix or improve it. "
            "Reply in valid JSON: {\"success\": bool, \"fix\": \"\", \"comment\": \"\"}\n"
            f"Step: {step}\n"
            f"Result: {result}\n"
            f"Error: {error or ''}\n"
            f"Memory: {memory.mem if memory else '{}'}\n"
        )
        resp = self.llm.ask(prompt)
        import json
        try:
            start = resp.find("{")
            end = resp.rfind("}")
            if start == -1 or end == -1:
                return {"success": False, "fix": "", "comment": "Could not parse reflection."}
            obj = json.loads(resp[start:end+1])
            return obj
        except Exception as e:
            return {"success": False, "fix": "", "comment": f"Reflection error: {e} | Resp: {resp}"}
