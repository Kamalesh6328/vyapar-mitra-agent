# -*- coding: utf-8 -*-
import os
import json
import re
from typing import List, Dict, Any, Optional

class RAGKnowledgeRetriever:
    def __init__(self, kb_path: Optional[str] = None):
        if kb_path is None:
            kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
        self.kb_path = kb_path
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.kb_path):
            with open(self.kb_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"schemes": [], "platforms": [], "fintech": {}, "market_data": {}}

    def get_all_schemes(self) -> List[Dict[str, Any]]:
        return self.data.get("schemes", [])

    def get_scheme_by_id(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        for s in self.data.get("schemes", []):
            if s.get("id") == scheme_id or scheme_id.lower() in s.get("title", "").lower():
                return s
        return None

    def search_schemes(self, query: str) -> List[Dict[str, Any]]:
        q_tokens = set(re.findall(r'\w+', query.lower()))
        results = []
        for s in self.data.get("schemes", []):
            score = 0
            text = f"{s.get('title', '')} {s.get('purpose', '')} {' '.join(s.get('eligibility', []))}".lower()
            for t in q_tokens:
                if t in text:
                    score += 1
            if score > 0:
                results.append((score, s))
        results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in results] if results else self.get_all_schemes()

    def get_platforms(self) -> List[Dict[str, Any]]:
        return self.data.get("platforms", [])

    def get_fintech_info(self) -> Dict[str, Any]:
        return self.data.get("fintech", {})

    def get_mandi_data(self, city: str = "pune") -> Dict[str, Any]:
        md = self.data.get("market_data", {})
        return md.get(city.lower(), md.get("pune", {}))

    def get_footfall_insights(self, city: str = "pune", area: str = "camp_mg_road") -> str:
        city_data = self.get_mandi_data(city)
        footfall = city_data.get("footfall", {})
        for k, v in footfall.items():
            if area.lower() in k.lower():
                return v
        return "Morning (7:30 - 10:30 AM): Office commuters. Evening (5:30 - 8:30 PM): Returning office workers and families."