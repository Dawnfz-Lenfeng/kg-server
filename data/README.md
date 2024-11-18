# 文档存放说明

## 目录结构
```
data/
├── 金融/              # 金融相关文献
├── 经济/              # 经济相关文献
├── 统计/              # 统计相关文献
├── 数据科学/           # 数据科学相关文献
└── README.md
```

## 文件命名规范
- 使用有意义的文件名
- 避免特殊字符
- 建议使用中文命名
- 示例：`金融市场分析.pdf`

## 文件要求
- 支持格式：PDF、TXT
- 最大大小：待定
- 文件编码：UTF-8

## 使用说明
1. 将文档按学科分类存放
2. 保持文件夹结构清晰
3. 遵循命名规范
4. 定期整理文档

## 批量上传
```bash
# 上传金融文献
python -m scripts.upload_docs --folder "data/金融" --subject 1

# 上传经济文献
python -m scripts.upload_docs --folder "data/经济" --subject 2

# 上传统计文献
python -m scripts.upload_docs --folder "data/统计" --subject 3

# 上传数据科学文献
python -m scripts.upload_docs --folder "data/数据科学" --subject 4
