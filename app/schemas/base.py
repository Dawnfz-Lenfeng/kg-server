from pydantic import BaseModel, ConfigDict, Field


class SetOperation(BaseModel):
    """集合操作基础模型"""

    add: list[int] | None = Field(None, description="要添加的ID列表", examples=[[1, 2]])
    remove: list[int] | None = Field(
        None, description="要移除的ID列表", examples=[[3, 4]]
    )


class DocBrief(BaseModel):
    """文档简要信息（用于关联展示）"""

    id: int = Field(..., description="文档ID")
    title: str = Field(..., description="文档标题")

    model_config = ConfigDict(from_attributes=True)


class KeywordBrief(BaseModel):
    """关键词简要信息（用于关联展示）"""

    id: int = Field(..., description="关键词ID")
    name: str = Field(..., description="关键词名称")

    model_config = ConfigDict(from_attributes=True)
