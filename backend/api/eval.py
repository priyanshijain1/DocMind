from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.schemas import EvalRequest
from rag.evaluation import run_evaluation

router = APIRouter(prefix="/api", tags=["eval"])


@router.post("/eval")
async def eval_rag(req: EvalRequest, db: AsyncSession = Depends(get_db)):
    metrics = run_evaluation(req.test_data, user_id="anonymous")
    return metrics
