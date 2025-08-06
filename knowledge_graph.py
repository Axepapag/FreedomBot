import json
import time
from collections import defaultdict

class KnowledgeGraph:
    """
    Ultra-maximal, persistent knowledge graph for Dexter:
    - Stores concepts with meaning, tags, meta, and relations
    - Tracks confidence, last-seen timestamps
    - Full CRUD, learning, enrichment, and forgetting
    - Relations are symmetric by default (can be made directional)
    - Persistent disk storage (auto-saves to 'data/knowledge.json')
    """

    def __init__(self, filename: str = "data/knowledge.json"):
        self.filename = filename
        self.concepts = {}  # key -> {'meaning': str, 'tag': str, 'meta': dict}
        self.relations = defaultdict(list)  # key -> list of (relation_type, target)
        self.confidence = defaultdict(lambda: 1.0)
        self.timestamps = {}
        self.load()

    def learn(self, concept, meaning, tag=None, related_to=None, relation_type="related_to", meta=None):
        key = concept.lower()
        if key not in self.concepts:
            self.concepts[key] = {
                "meaning": meaning.strip(),
                "tag": tag or "concept",
                "meta": meta or {}
            }
            self.confidence[key] = 1.0
            self.timestamps[key] = time.time()

        if related_to:
            for target in related_to:
                tgt = target.lower()
                self.relations[key].append((relation_type, tgt))
                self.relations[tgt].append((relation_type, key))  # symmetric for now

        self.save()

    def decay_confidence(self, concept, minutes_passed):
        key = concept.lower()
        if key in self.confidence:
            self.confidence[key] *= 0.95 ** (minutes_passed / 5)
            self.timestamps[key] = time.time()
            self.save()

    def reinforce(self, concept):
        key = concept.lower()
        self.confidence[key] = min(self.confidence[key] * 1.1, 1.0)
        self.timestamps[key] = time.time()
        self.save()

    def get_related(self, concept, relation_filter=None):
        key = concept.lower()
        links = self.relations.get(key, [])
        if relation_filter:
            return [tgt for rel, tgt in links if rel == relation_filter]
        return [tgt for _, tgt in links]

    def get_summary(self):
        return {
            'concepts': {
                k: {
                    **v,
                    "confidence": self.confidence[k],
                    "last_seen": self.timestamps[k]
                } for k, v in self.concepts.items()
            },
            'relations': {
                k: self.relations[k] for k in self.relations
            }
        }

    def query(self, concept):
        key = concept.lower()
        if key not in self.concepts:
            return f"No data on '{concept}'."
        data = self.concepts[key]
        rels = self.relations.get(key, [])
        return {
            "meaning": data["meaning"],
            "tag": data["tag"],
            "meta": data["meta"],
            "confidence": self.confidence[key],
            "last_seen": self.timestamps[key],
            "related": rels
        }

    def forget(self, concept):
        key = concept.lower()
        self.concepts.pop(key, None)
        self.confidence.pop(key, None)
        self.timestamps.pop(key, None)
        if key in self.relations:
            for _, tgt in self.relations[key]:
                self.relations[tgt] = [(rel, k) for rel, k in self.relations[tgt] if k != key]
            del self.relations[key]
        self.save()

    def save(self):
        try:
            data = {
                "concepts": self.concepts,
                "relations": {k: list(v) for k, v in self.relations.items()},
                "confidence": dict(self.confidence),
                "timestamps": self.timestamps
            }
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[KnowledgeGraph] Save error: {e}")

    def load(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.concepts = data.get("concepts", {})
                self.relations = defaultdict(list, {k: [tuple(x) for x in v] for k, v in data.get("relations", {}).items()})
                self.confidence = defaultdict(lambda: 1.0, data.get("confidence", {}))
                self.timestamps = data.get("timestamps", {})
        except Exception:
            self.concepts = {}
            self.relations = defaultdict(list)
            self.confidence = defaultdict(lambda: 1.0)
            self.timestamps = {}
