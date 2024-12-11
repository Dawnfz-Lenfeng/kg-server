from pathlib import Path

from httpx import AsyncClient


async def test_create_keyword(client: AsyncClient):
    """测试创建单个关键词"""
    response = await client.post(
        "/keywords",
        json={"name": "测试关键词"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "测试关键词"


async def test_create_keywords_for_doc(
    client: AsyncClient, sample_doc: int, tmp_path: Path
):
    """测试为文档创建关键词"""
    # 创建测试文件
    keywords_file = tmp_path / "keywords.txt"
    keywords_file.write_text("关键词1\n关键词2\n关键词3\n")

    with open(keywords_file, "rb") as f:
        response = await client.post(
            f"/keywords/{sample_doc}",
            files={"file": ("keywords.txt", f, "text/plain")},
        )

    assert response.status_code == 200
    assert len(response.json()["keywords"]) == 3


async def test_read_keywords(client: AsyncClient):
    """测试读取关键词列表"""
    # 创建测试数据
    for name in ["关键词1", "关键词2", "测试3"]:
        await client.post("/keywords", json={"name": name})

    # 测试基本查询
    response = await client.get("/keywords")
    assert response.status_code == 200
    assert len(response.json()) == 3

    # 测试搜索
    response = await client.get("/keywords?search=关键词")
    assert response.status_code == 200
    assert len(response.json()) == 2
