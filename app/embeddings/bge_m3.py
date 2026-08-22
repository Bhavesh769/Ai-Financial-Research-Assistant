from FlagEmbedding import BGEM3FlagModel


class BGE_M3_Embedder:
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self.model = BGEM3FlagModel(
            model_name,
            use_fp16=False
        )

    def encode(self, texts: list[str]):
        return self.model.encode(
            texts,
            return_dense=True,
            return_sparse=True
        )