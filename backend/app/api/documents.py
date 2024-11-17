from fastapi import APIRouter

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)

@router.get("/")
async def get_documents():
    return {"message": "Documents endpoint"}
