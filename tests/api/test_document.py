import pytest
from fastapi import UploadFile
from httpx import AsyncClient
from kgtools.schemas.preprocessing import ExtractConfig, NormalizeConfig, OCREngine

from app.schemas.document import DocState


@pytest.mark.asyncio
async def test_create_doc_api(client: AsyncClient, pdf_file: UploadFile):
    """测试文档上传API"""
    response = await client.post(
        "/documents",
        files={"file": (pdf_file.filename, await pdf_file.read())},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["document"]["title"] is not None
    assert data["document"]["state"] == DocState.UPLOADED

    await client.delete(f"/documents/{data['document']['id']}")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "ocr_engine,force_ocr",
    [(OCREngine.CNOCR, False), (OCREngine.CNOCR, True), (OCREngine.TESSERACT, True)],
)
async def test_extract_doc_text_api(
    client: AsyncClient,
    sample_doc: int,
    ocr_engine: OCREngine,
    force_ocr: bool,
):
    """测试文档文本提取API"""
    config = ExtractConfig(last_page=1, ocr_engine=ocr_engine, force_ocr=force_ocr)

    response = await client.put(
        f"/documents/{sample_doc}/extract",
        json=config.model_dump(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_doc
    assert data["state"] == DocState.EXTRACTED


@pytest.mark.asyncio
async def test_normalize_doc_text_api(client: AsyncClient, sample_doc: int):
    """测试文档文本清洗API"""
    extract_config = ExtractConfig(last_page=1)

    response = await client.put(
        f"/documents/{sample_doc}/extract",
        json=extract_config.model_dump(),
    )
    assert response.status_code == 200

    normalize_config = NormalizeConfig()

    response = await client.put(
        f"/documents/{sample_doc}/normalize",
        json=normalize_config.model_dump(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_doc
    assert data["state"] == DocState.NORMALIZED


@pytest.mark.asyncio
async def test_read_doc_api(client: AsyncClient, sample_doc: int):
    """测试获取单个文档API"""
    response = await client.get(f"/documents/{sample_doc}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_doc
    assert data["title"]


@pytest.mark.asyncio
async def test_read_docs_api(client: AsyncClient, sample_doc: int):
    """测试获取文档列表API"""
    response = await client.get("/documents?skip=0&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(doc["id"] for doc in data)


@pytest.mark.asyncio
async def test_update_doc_api(
    client: AsyncClient,
    sample_doc: int,
):
    """测试更新文档API"""
    update_data = {"title": "Updated Title"}

    response = await client.put(
        f"/documents/{sample_doc}",
        json=update_data,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["title"] == update_data["title"]


@pytest.mark.asyncio
async def test_delete_doc_api(client: AsyncClient, sample_doc: int):
    """测试删除文档API"""
    response = await client.delete(f"/documents/{sample_doc}")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Document deleted"

    # 验证文档确实被删除
    response = await client.get(f"/documents/{sample_doc}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_doc_not_found_api(client: AsyncClient):
    """测试文档不存在的情况"""
    non_existent_id = 99999

    response = await client.get(f"/documents/{non_existent_id}")
    assert response.status_code == 404

    response = await client.put(
        f"/documents/{non_existent_id}",
        json={"title": "New Title"},
    )
    assert response.status_code == 404

    response = await client.delete(f"/documents/{non_existent_id}")
    assert response.status_code == 404
