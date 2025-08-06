import json
import os

class Corrections:
    def __init__(self, path="data/corrections.json"):
        self.path = path
        self.corrections = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.corrections, f, indent=2)

    def add(self, original, correction, context=None):
        self.corrections.append({
            "original": original,
            "correction": correction,
            "context": context,
        })
        self.save()

    def last(self, n=5):
        return self.corrections[-n:]
