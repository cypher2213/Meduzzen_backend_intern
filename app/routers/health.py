from fastapi import APIRouter
from app.services.connect_service import connection_check
router = APIRouter()

@router.get('/')
async def health_check():
  connection_res = await connection_check()
  return connection_res
  
