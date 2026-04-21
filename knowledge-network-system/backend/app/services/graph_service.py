from __future__ import annotations

from collections import Counter

from app.services.nlp_service import extract_entities, extract_keywords, extract_relations, normalize_token


class GraphService:
    def build_from_text(self, text: str) -> dict:
        keywords = extract_keywords(text, top_k=20)
        entities = extract_entities(text, top_k=12)
        concepts = self._merge_concepts(keywords, entities, max_count=24)
        if not concepts:
            return {
                "nodes": [],
                "edges": [],
                "keywords": [],
                "entities": [],
                "stats": {
                    "node_count": 0,
                    "edge_count": 0,
                    "keyword_count": 0,
                    "entity_count": 0,
                },
            }

        concept_counter = Counter([normalize_token(token) for token in extract_keywords(text, top_k=200)])
        relation_counts = extract_relations(text, concepts=concepts, window_size=6)

        nodes = []
        keyword_set = set(keywords)
        entity_set = set(entities)
        for concept in concepts:
            score = float(concept_counter.get(normalize_token(concept), 1))
            node_type = "entity" if concept in entity_set else "keyword"
            if concept in keyword_set and concept in entity_set:
                node_type = "hybrid"
            nodes.append({"id": concept, "label": concept, "type": node_type, "score": score})

        edges = [
            {
                "source": src,
                "target": dst,
                "weight": float(weight),
                "relation": "co_occurs",
            }
            for (src, dst), weight in sorted(relation_counts.items(), key=lambda item: item[1], reverse=True)
        ]

        if not edges and len(concepts) > 1:
            for idx in range(len(concepts) - 1):
                edges.append(
                    {
                        "source": concepts[idx],
                        "target": concepts[idx + 1],
                        "weight": 1.0,
                        "relation": "adjacent",
                    }
                )

        return {
            "nodes": nodes,
            "edges": edges,
            "keywords": keywords,
            "entities": entities,
            "stats": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "keyword_count": len(keywords),
                "entity_count": len(entities),
            },
        }

    def _merge_concepts(self, keywords: list[str], entities: list[str], max_count: int = 24) -> list[str]:
        ordered = []
        seen: set[str] = set()
        for item in entities + keywords:
            key = normalize_token(item)
            if key in seen:
                continue
            seen.add(key)
            ordered.append(item)
            if len(ordered) >= max_count:
                break
        return ordered

    def build_preview(self, text: str, max_chars: int = 500) -> str:
        normalized = " ".join(text.split())
        return normalized[:max_chars]
