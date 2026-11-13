"""Local embedder (fastembed, ONNX). Model: BAAI/bge-small-en-v1.5, 384 dims."""
from typing import Protocol


class Embedder(Protocol):
    model_name: str
    dimensions: int
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, question: str) -> list[float]: ...


class MyEmbedder:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        from fastembed import TextEmbedding
        self.model_name = model_name
        self._m = TextEmbedding(model_name=model_name)
        self.dimensions = len(next(iter(self._m.embed(["dimension probe"]))))

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [v.tolist() for v in self._m.passage_embed(texts)]

    def embed_query(self, question: str) -> list[float]:
        return next(iter(self._m.query_embed(question))).tolist()