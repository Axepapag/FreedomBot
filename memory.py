import os
import time
import json
import psutil
from collections import deque
from typing import List, Dict, Any

class Memory:
    """
    Dexter's RAM-aware memory system:
    - Maintains short-term memory within 25%–80% of available system RAM
    - Stores excess into long-term disk memory
    - Provides recent context for LLM prompting
    - Robust against disk corruption or I/O errors
    """

    MIN_RAM_PERCENT = 25
    MAX_RAM_PERCENT = 80
    MEMORY_CHECK_INTERVAL = 5  # seconds

    def __init__(self,
                 short_term_path: str = "data/memory.json",
                 long_term_path: str = "memory/memory.json"):

        self.short_term_path = short_term_path
        self.long_term_path = long_term_path
        self.short_term_memory = deque()
        self.long_term_memory = []

        self.last_check = 0
        self.load()

    def load(self):
        def safe_load(path):
            if not os.path.exists(path):
                return []
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Memory Load Error: {path}] {e}")
                return []

        self.short_term_memory = deque(safe_load(self.short_term_path))
        self.long_term_memory = safe_load(self.long_term_path)

    def save(self):
        os.makedirs(os.path.dirname(self.short_term_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.long_term_path), exist_ok=True)

        try:
            with open(self.short_term_path, 'w', encoding='utf-8') as f:
                json.dump(list(self.short_term_memory), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Memory Save Error: short-term] {e}")

        try:
            with open(self.long_term_path, 'w', encoding='utf-8') as f:
                json.dump(self.long_term_memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Memory Save Error: long-term] {e}")

    def add_interaction(self, user_input: str, dexter_response: str, priority: float = 0.5):
        entry = {
            "timestamp": time.time(),
            "user_input": user_input,
            "dexter_response": dexter_response,
            "priority": priority
        }
        self.short_term_memory.append(entry)
        self._adjust_memory()
        self.save()

    def recall_recent(self, n: int = 10) -> List[Dict[str, Any]]:
        return list(self.short_term_memory)[-n:]

    def recall_all(self) -> List[Dict[str, Any]]:
        return list(self.short_term_memory)

    def _adjust_memory(self):
        now = time.time()
        if now - self.last_check < self.MEMORY_CHECK_INTERVAL:
            return

        vm = psutil.virtual_memory()
        total_ram = vm.total
        available_ram = vm.available
        ram_used = self._estimate_ram_usage()

        max_allowed = total_ram * (self.MAX_RAM_PERCENT / 100)
        min_target = total_ram * (self.MIN_RAM_PERCENT / 100)

        # Too big → dump lowest priority/oldest
        while ram_used > max_allowed and len(self.short_term_memory) > 1:
            removed = self.short_term_memory.popleft()
            self.long_term_memory.append(removed)
            ram_used = self._estimate_ram_usage()

        # Too small → reload best memories from long-term
        while ram_used < min_target and len(self.long_term_memory) > 0:
            candidate = self.long_term_memory.pop()
            self.short_term_memory.append(candidate)
            ram_used = self._estimate_ram_usage()

        self.last_check = now

    def _estimate_ram_usage(self) -> int:
        """Estimate memory size in bytes of current short-term memory"""
        return sum(len(json.dumps(item).encode("utf-8")) for item in self.short_term_memory)

    def clear_short_term(self):
        self.short_term_memory.clear()
        self.save()

    def clear_long_term(self):
        self.long_term_memory.clear()
        self.save()

    def clear_all(self):
        self.clear_short_term()
        self.clear_long_term()

    def get_context(self, count: int = 10) -> str:
        """
        Returns the last N memory entries as formatted prompt context.
        """
        recent = list(self.short_term_memory)[-count:]
        return "\n".join(
            f"User: {entry['user_input']}\nDexter: {entry['dexter_response']}"
            for entry in recent if 'user_input' in entry and 'dexter_response' in entry
        )

    def __len__(self):
        return len(self.short_term_memory)
