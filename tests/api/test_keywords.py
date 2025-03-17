from pathlib import Path

from httpx import AsyncClient

from app.schemas.subject import Subject


async def test_create_keyword(client: AsyncClient):
    """测试创建单个关键词"""
    response = await client.post(
        "/keywords",
        json={"name": "测试关键词", "subject": Subject.ECONOMICS},
    )

    assert response.status_code == 200
    keyword = response.json()
    assert keyword["name"] == "测试关键词"
    assert keyword["subject"] == Subject.ECONOMICS

    await client.delete(f"/keywords/{keyword['id']}")


async def test_create_keywords_for_doc(
    client: AsyncClient, sample_doc: int, tmp_path: Path
):
    """测试为文档创建关键词"""
    # 创建测试文件
    keywords_file = tmp_path / "keywords.txt"
    keywords_file.write_text("关键词1\n关键词2\n关键词3\n", encoding="utf-8")

    response = await client.post(
        f"/keywords/{sample_doc}",
        files={"file": ("keywords.txt", keywords_file.read_bytes())},
    )

    assert response.status_code == 200

    assert len(response.json()["keywords"]) == 3

    for name in ["关键词1", "关键词2", "关键词3"]:
        await client.delete(f"/keywords/name/{name}")


async def test_read_keywords(client: AsyncClient):
    """测试读取关键词列表"""
    # 创建测试数据
    names = ["关键词1", "关键词2", "测试3"]
    for name in names:
        await client.post("/keywords", json={"name": name})

    # 测试基本查询
    response = await client.get("/keywords")
    assert response.status_code == 200
    assert len(response.json()) == 3

    # 测试搜索
    response = await client.get("/keywords?search=关键词")
    assert response.status_code == 200
    assert len(response.json()) == 2

    for name in names:
        await client.delete(f"/keywords/name/{name}")
