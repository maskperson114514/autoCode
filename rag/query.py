# 导入必要的库和模块
import chromadb  # ChromaDB客户端库，用于向量数据库操作
from chromadb.utils import embedding_functions  # 嵌入函数工具，用于文本向量化
import json  # 用于处理JSON配置文件
from typing import List, Dict  # 类型提示支持

class ChromaQueryEngine:
    """基于ChromaDB的查询引擎，支持元数据过滤和相似度阈值控制"""
    
    def __init__(self, config_path: str = "./config.json"):
        """
        初始化查询引擎
        :param config_path: 配置文件路径（默认./config.json）
            配置文件需包含:
            - collection_name: 集合名称
            - persist_path: 数据库持久化存储路径
            - embedding_model: 嵌入模型名称（如'all-MiniLM-L6-v2'）
        """
        # 加载配置文件并校验完整性
        self.config = self._load_config(config_path)
        
        # 创建持久化客户端实例（数据存储在本地磁盘）
        self.client = chromadb.PersistentClient(path=self.config["persist_path"])
        
        # 初始化句子嵌入模型（用于将文本转换为向量）
        self.sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.config["embedding_model"]
        )
        
        # 获取指定集合（类似数据库表），并绑定嵌入函数
        self.collection = self.client.get_collection(
            self.config["collection_name"],
            embedding_function=self.sentence_transformer_ef
        )

    def _load_config(self, path: str) -> Dict:
        """加载并验证配置文件
        :return: 包含配置参数的字典
        :raises RuntimeError: 文件读取失败或配置不完整时抛出
        """
        try:
            with open(path, 'r') as f:
                config = json.load(f)
            # 校验必要配置项存在性
            assert all(k in config for k in ["collection_name", "persist_path", "embedding_model"])
            return config
        except Exception as e:
            raise RuntimeError(f"配置加载失败: {str(e)}")
    
    def query(self, query_text: str, k: int = 3, max_distance: float = 300) -> tuple:
        """
        执行相似性查询，支持去重和相似度控制
        :param query_text: 查询文本（需包含语义信息）
        :param k: 最大返回结果数（默认3）
        :param max_distance: 最大允许余弦距离（默认300，值越大相似度越低）
        :return: tuple（匹配的source列表，对应的距离列表）
        """
        # 生成查询文本的嵌入向量（转换为768/384维等向量）
        query_embedding = self.sentence_transformer_ef([query_text])
        
        queried_id = ["null"]  # 已查询ID列表（初始占位避免空值）
        distance = []  # 相似度距离记录
        
        # 分页式查询（每次取1个结果，循环k次）
        for _ in range(k):
            try:
                results = self.collection.query(
                    query_embeddings=query_embedding,  # 使用查询向量
                    n_results=1,  # 每次取1个结果（实现分页）
                    where={"source": {"$nin": queried_id}},  # 排除已查询ID（基于metadata）
                    include=["metadatas", "distances"]  # 返回元数据和距离
                )
            except Exception as e:
                # 查询异常时返回当前结果（如集合不存在或数据不足）
                return (queried_id[1:], distance)
            
            # 获取当前结果的余弦距离（Chroma使用余弦距离，0-完全相似，>1不相似）
            current_distance = results['distances'][0][0]
            
            # 超过阈值时提前终止查询
            if current_distance >= max_distance:
                return (queried_id[1:], distance)
            
            # 记录结果信息
            queried_id.append(results['metadatas'][0][0]['source'])
            distance.append(current_distance)
        
        # 返回最终结果（去除初始占位符）
        return (queried_id[1:], distance)

# 使用示例
if __name__ == "__main__":
    # 初始化查询引擎（自动加载默认路径配置）
    query_engine = ChromaQueryEngine()
    
    # 参数说明：查询文本，最多3个结果，最大距离300
    print(query_engine.query("自定义物品", k=3))