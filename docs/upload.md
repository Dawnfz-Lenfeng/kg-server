# 文档上传指南

### 使用上传脚本

我们提供了文档上传脚本 `scripts/upload_docs.py`，支持单个和批量上传。

#### 1. 单个文件上传
```bash
# 上传单个PDF文件（指定标题）
python -m scripts.upload_docs --file "data/金融市场.pdf" --title "金融市场分析" --subject 1

# 上传单个PDF文件（使用文件名作为标题）
python -m scripts.upload_docs --file "data/金融市场.pdf" --subject 1
```

#### 2. 批量上传
```bash
# 上传整个文件夹中的PDF文件
python -m scripts.upload_docs --folder "data/金融文献" --subject 1
```

#### 学科ID对照表
| ID | 学科 | 说明 |
|----|------|------|
| 1 | 金融 | 金融理论、金融市场、投资学等 |
| 2 | 经济 | 宏观经济、微观经济、政治经济学等 |
| 3 | 统计 | 统计理论、统计方法、数理统计等 |
| 4 | 数据科学 | 机器学习、数据挖掘、人工智能等 |

#### 注意事项
1. 确保文件存在且可读
2. 文件大小不超过20MB
3. 仅支持PDF和TXT格式
4. 使用正确的学科ID
5. 文件名避免使用特殊字符