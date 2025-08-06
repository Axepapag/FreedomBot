from dexter import Dexter
from mentor_llm import MentorLLM
from memory import Memory
from skill_registry import SkillRegistry
from sandbox import Sandbox
from logs import Logger

def main():
    memory = Memory("data/memory.json")
    logger = Logger("data/log.txt")
    skills = SkillRegistry()
    sandbox = Sandbox()
    mentor = MentorLLM()
    dexter = Dexter(memory, skills, mentor, sandbox, logger)

    print("\nDexter CLI. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"): break
        dexter_response = dexter.handle_input(user_input)
        print(f"Dexter: {dexter_response}\n")

if __name__ == "__main__":
    main()
