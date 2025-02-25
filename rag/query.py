import chromadb
from chromadb.utils import embedding_functions
import json
from typing import List, Dict

class ChromaQueryEngine:
    def __init__(self, config_path: str = "./config.json"):
        """
        初始化查询引擎
        :param config_path: 配置文件路径（默认./config.json）
        """
        self.config = self._load_config(config_path)
        self.client = chromadb.PersistentClient(path=self.config["persist_path"])
        self.sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.config["embedding_model"]
        )
        self.collection = self.client.get_collection(self.config["collection_name"], embedding_function=self.sentence_transformer_ef)

    def _load_config(self, path: str) -> Dict:
        """加载Chroma配置"""
        try:
            with open(path, 'r') as f:
                config = json.load(f)
            # 配置完整性校验
            assert all(k in config for k in ["collection_name", "persist_path"])
            return config
        except Exception as e:
            raise RuntimeError(f"配置加载失败: {str(e)}")

    def query_unique_indices(self, query_text: str, k: int = 3) -> List[str]:
        """
        执行带去重的语义查询
        :param query_text: 查询文本
        :param k: 返回结果数量
        :return: 唯一索引列表
        """
        try:
            # 动态调整返回数量（基于配置中的索引参数）
            expand_factor = self.config.get("query_expand_factor", 2)
            results = self.collection.query(
                query_texts=[query_text],
                n_results=k * expand_factor,
                include=["metadatas"]
            )
            
            # 结果去重处理
            unique_indices = []
            seen = set()
            for metadata in results["metadatas"][0]:  # 按相似度排序
                if (current_index := metadata.get("index")) and current_index not in seen:
                    unique_indices.append(current_index)
                    seen.add(current_index)
                if len(unique_indices) >= k:
                    break
            return unique_indices[:k]
        
        except Exception as e:
            print(f"查询执行异常: {str(e)}")
            return []
    def query_temp(self, query_text, k):
        query_embedding = self.sentence_transformer_ef([query_text]) # 对查询文本进行 embedding

        results = self.collection.query(
            query_embeddings=query_embedding, # 使用查询文本的 embedding 向量
            n_results=k,
            include=["documents", "metadatas", "distances"] # 返回文档内容, 元数据和距离
        )

        print(f"\n使用余弦相似度查询 '{query_text}' 的结果 (chunkId: chunk1):")
        if results["documents"]:
            for i in range(len(results["documents"][0])): # results 是嵌套列表，第一个元素是结果列表
                print(f"  Document ID: {results['ids'][0][i]}")
                print(f"  Text: {results['documents'][0][i]}")
                print(f"  Metadata: {results['metadatas'][0][i]}")
                print(f"  Distance (Cosine): {results['distances'][0][i]:.4f}") # 打印余弦距离 (越小越相似)
        else:
            print(f"  未找到与查询相关的文档。")
# 使用示例
if __name__ == "__main__":
    # 初始化时自动加载配置
    query_engine = ChromaQueryEngine()
    
    # 执行查询
    print(query_engine.query_temp("食物", k=30))