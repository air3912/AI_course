from __future__ import annotations

from collections import Counter
import re

STOPWORDS = {
    "the",
    "and",
    "for",
    "that",
    "with",
    "from",
    "this",
    "have",
    "will",
    "into",
    "your",
    "you",
    "are",
    "was",
    "were",
    "课程",
    "知识",
    "分析",
    "我们",
    "以及",
    "一个",
    "可以",
}


def split_sentences(text: str) -> list[str]:
    chunks = re.split(r"[。！？!?;\n\r]+", text)
    return [chunk.strip() for chunk in chunks if chunk and chunk.strip()]


def tokenize_text(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9\-]{1,}|[A-Z]{2,}|\d+|[\u4e00-\u9fff]{2,}", text)


def normalize_token(token: str) -> str:
    return token.lower().strip()


def extract_keywords(text: str, top_k: int = 20) -> list[str]:
    tokens = [normalize_token(token) for token in tokenize_text(text)]
    words = [token for token in tokens if len(token) > 1 and token not in STOPWORDS]
    counter = Counter(words)
    return [word for word, _ in counter.most_common(top_k)]


def extract_entities(text: str, top_k: int = 15) -> list[str]:
    english_entities = re.findall(r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+|[A-Z]{2,})\b", text)
    chinese_entities = re.findall(r"[\u4e00-\u9fff]{2,8}(?:系统|模型|网络|方法|算法|平台|框架)", text)
    entities = [item.strip() for item in english_entities + chinese_entities if item.strip()]
    counter = Counter(entities)
    return [item for item, _ in counter.most_common(top_k)]


def extract_relations(text: str, concepts: list[str], window_size: int = 5) -> dict[tuple[str, str], int]:
    if not concepts:
        return {}

    concept_norm_map = {normalize_token(item): item for item in concepts}
    relation_counter: Counter[tuple[str, str]] = Counter()

    for sentence in split_sentences(text):
        tokens = [normalize_token(token) for token in tokenize_text(sentence)]
        sentence_concepts = [token for token in tokens if token in concept_norm_map]
        for idx, source in enumerate(sentence_concepts):
            end = min(idx + window_size, len(sentence_concepts))
            for j in range(idx + 1, end):
                target = sentence_concepts[j]
                if source == target:
                    continue
                pair = tuple(sorted((source, target)))
                relation_counter[pair] += 1
    return dict(relation_counter)
