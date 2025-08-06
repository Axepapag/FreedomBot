import importlib.util, os, re
import difflib
from config import SKILLS_DIR

class SkillRegistry:
    """
    Maximal, robust skill registry:
    - Supports built-in and disk-based dynamic skills
    - Fuzzy matching, keyword, and pattern-based matching
    - Safe fallback for no skills, fully pluggable
    """

    def __init__(self, skills_dir=None, logger=None):
        self.skills_dir = skills_dir or SKILLS_DIR
        self.logger = logger or (lambda m: None)
        self.disk_skills = self._load_skills()
        self.builtin_skills = [
            {"name": "weather", "keywords": ["forecast", "weather", "temperature"]},
            {"name": "news", "keywords": ["headlines", "news", "updates"]},
            {"name": "joke", "keywords": ["joke", "funny", "humor"]},
            # Add more built-ins here...
        ]

    def _load_skills(self):
        if not os.path.exists(self.skills_dir): os.makedirs(self.skills_dir)
        skills = []
        for fname in os.listdir(self.skills_dir):
            if fname.endswith('.py') and fname != "__init__.py":
                try:
                    mod_name = fname[:-3]
                    path = os.path.join(self.skills_dir, fname)
                    spec = importlib.util.spec_from_file_location(mod_name, path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, "Skill"): skills.append(mod.Skill())
                except Exception as e:
                    self.logger(f"Skill load error {fname}: {e}")
        return skills

    def match_skill(self, user_input, cutoff=0.6):
        """
        Tries to match user_input to a skill, prioritizing disk skills, then built-ins.
        Returns the best matching skill object or dict, or None.
        """
        # Try disk-based skills (object-based)
        for skill in self.disk_skills:
            if hasattr(skill, 'match') and skill.match(user_input):
                return skill

        # Try built-in skills (keyword and fuzzy)
        user_input = user_input.lower().strip()
        all_keywords = []
        skill_map = {}

        for skill in self.builtin_skills:
            keywords = [skill["name"].lower()] + [k.lower() for k in skill.get("keywords", [])]
            for kw in keywords:
                all_keywords.append(kw)
                skill_map[kw] = skill

        # Fuzzy match
        best_matches = difflib.get_close_matches(user_input, all_keywords, n=1, cutoff=cutoff)
        if best_matches:
            matched_keyword = best_matches[0]
            return skill_map[matched_keyword]

        # Substring search fallback
        for kw in all_keywords:
            if kw in user_input or user_input in kw:
                return skill_map[kw]

        return None

    def _get_skill_name(self, skill):
        """Return a display name for a skill (object or dict)."""
        if hasattr(skill, 'name'):
            return getattr(skill, 'name')
        if isinstance(skill, dict) and 'name' in skill:
            return skill['name']
        return str(skill)

    def _execute_skill(self, skill, user_input, context=None):
        """Execute a skill, handling both object and dict skills."""
        if hasattr(skill, 'act'):
            return skill.act(user_input, context)
        if isinstance(skill, dict) and 'name' in skill:
            # Simulate a skill result
            return f"[{skill['name'].capitalize()} skill invoked for: '{user_input}']"
        return "[Unknown skill type]"

    def list_skills(self):
        """List all loaded skill names (disk and built-in)."""
        disk = [self._get_skill_name(s) for s in self.disk_skills]
        builtin = [s['name'] for s in self.builtin_skills]
        return disk + builtin

    def register(self, skill):
        """Register a new in-memory skill object (hot-reload)."""
        self.disk_skills.append(skill)

    def unregister(self, name):
        """Remove a skill by name."""
        self.disk_skills = [s for s in self.disk_skills if self._get_skill_name(s) != name]