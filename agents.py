from mentor_llm import MentorLLM

class Agent:
    def __init__(self, role, instructions=None):
        self.role = role
        self.instructions = instructions or ""
        self.llm = MentorLLM()

    def act(self, user_input, memory=None):
        prompt = (
            f"You are a {self.role} agent for Dexter. {self.instructions}\n"
            f"Task: {user_input}\n"
            f"Memory: {memory.mem if memory else '{}'}\n"
            "Reply with your full answer."
        )
        return self.llm.ask(prompt)

class AgentManager:
    def __init__(self):
        self.agents = {
            "code_reviewer": Agent(
                "Code Reviewer",
                "Review the code and point out any issues, bugs, or improvements. Be concise and actionable."
            ),
            "test_writer": Agent(
                "Test Writer",
                "Write high-quality unit tests for the given code/task."
            ),
            "researcher": Agent(
                "Researcher",
                "Research and summarize relevant information about the user's task."
            )
        }

    def call(self, agent_name, user_input, memory=None):
        agent = self.agents.get(agent_name)
        if not agent:
            return f"No such agent: {agent_name}"
        return agent.act(user_input, memory)
