from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Dict
from typing import List


@dataclass
class AgentConfig:
    name: str
    settings: Dict
    system: str
    bio: List[str]
    lore: List[str]
    adjectives: List[str]
    topics: List[str]
    style: Dict
    goals_template: List[str]
    facts_template: List[str]
    knowledge: List[str]
    search_queries: List[str]

    extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_json(cls, data: dict):
        known_fields = [
            "name",
            "settings",
            "system",
            "bio",
            "lore",
            "adjectives",
            "topics",
            "style",
            "goals_template",
            "facts_template",
            "knowledge",
            "search_queries",
        ]
        # Separate known fields and extra fields
        kwargs = {key: value for key, value in data.items() if key in known_fields}
        extra_fields = {
            key: value for key, value in data.items() if key not in known_fields
        }
        # Pass known fields to the dataclass, and store extra fields
        return cls(**kwargs, extra_fields=extra_fields)
