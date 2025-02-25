

import chromadb
from chromadb.utils import embedding_functions
import json
import uuid
from typing import List, Tuple, Optional


def extract_values_to_array(data, result_array=None):
  """
  递归地从字典或列表中提取所有值，并将它们放入一个数组中。

  Args:
    data: 要处理的字典或列表。
    result_array: (可选) 用于存储值的现有数组。 如果为None，则创建一个新数组。

  Returns:
    包含所有值的数组。
  """

  if result_array is None:
    result_array = []

  if isinstance(data, dict):
    for value in data.values():
      extract_values_to_array(value, result_array)  # 递归处理值
  elif isinstance(data, list):
    for item in data:
      extract_values_to_array(item, result_array)  # 递归处理列表中的每个项目
  else:
    result_array.append(data)  # 如果不是字典或列表，则添加值

  return result_array



class ChromaConfigurator:
    def __init__(self, 
                collection_name: str = "default_collection",
                persist_path: str = "./chroma_data",
                embedding_model: Optional[str] = 'shibing624/text2vec-base-chinese'):
        """
        初始化Chroma配置器
        :param collection_name: 集合名称（3-63字符，支持小写字母、数字、下划线）
        :param persist_path: 持久化存储路径
        :param embedding_model: 嵌入模型名称（默认使用all-MiniLM-L6-v2）
        """
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function= sentence_transformer_ef,
        )
        
        self.config = {
            "collection_name": collection_name,
            "persist_path": persist_path,
            "embedding_model": embedding_model
        }
        
        config_path = f"config.json"
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def add_documents(self, keyId: str, items: List[str]) -> bool:
        """
        添加文档并自动生成嵌入
        :param items: 待添加的文本数组
        :return: (操作状态, 配置文件路径)
        """
        try:
            # 生成唯一ID和元数据
            ids = [str(uuid.uuid4()) for _ in items]
            metadatas = [{"source": keyId}]*len(items)
            
            # 执行文档添加（自动生成嵌入）
            self.collection.add(
                documents=items,
                metadatas=metadatas,
                ids=ids
            )
            
            # 导出配置文件
                
            return True
            
        except Exception as e:
            print(f"文档添加失败: {str(e)}")
            return (False, "")

if __name__ == "__main__":
  # 使用示例
  configurator = ChromaConfigurator(
      collection_name="mc_fabric_coll",
      persist_path="./mc_fabric"
  )

  items = {
    "核心主题": "创建 Minecraft 物品",
    "核心概念定义": "注册表：Minecraft 中存储所有物品的地方。",
    "目的": "指导用户注册、添加纹理、模型和命名 Minecraft 物品。",
    "组成部分": [
      "物品类准备",
      "物品注册",
      "添加到物品组",
      "物品命名",
      "添加纹理和模型",
      "添加物品模型描述",
      "使物品可堆肥或作为燃料",
      "添加基本的合成配方",
      "自定义物品提示"
    ],
    "特征": [
      "物品需要注册才能在游戏中使用",
      "物品可以通过 Items.Settings 类配置属性",
      "物品需要纹理和模型才能在游戏中显示",
      "物品可以通过语言文件进行命名",
      "物品可以添加到物品组以便在创造模式中找到",
      "可以通过 Fabric API 添加额外属性，例如可堆肥性或燃料值",
      "可以添加合成配方来定义如何合成物品",
      "可以自定义物品的提示信息"
    ],
    "要素之间的关系": [
      "注册物品需要先准备物品类",
      "添加纹理和模型依赖于物品的注册",
      "物品命名需要创建语言文件",
      "将物品添加到物品组需要在初始化方法中完成",
      "物品模型描述JSON引用了物品的模型",
      "添加合成配方需要创建JSON文件"
    ],
    "应用场景": [
      "模组开发",
      "自定义 Minecraft 游戏内容"
    ]
  }
  items = extract_values_to_array(items)
  success = configurator.add_documents("foo1413",items)
  print(f"操作状态: {success} ")
