import asyncio
import uuid
from datetime import datetime
from enum import IntEnum
from typing import Optional, Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field

from app.adapters.repository import Repository
from app.application.handlers import get_prediction_result
from app.application.model import MyEfficientNet

jobs: Dict[UUID, "Job"] = {}


class JobStatus(IntEnum):
    PENDING = 0
    STARTED = 1
    DONE = 2


class Job(BaseModel):
    id_: UUID = Field(default_factory=uuid.uuid4)
    status: JobStatus
    result: Optional[UUID]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


async def add_prediction_task(
    order_id: UUID,
    model: MyEfficientNet,
    config: Dict[str, Any],
    repository: Repository,
):
    new_job = Job(status=JobStatus.PENDING, id_=order_id)
    jobs[new_job.id_] = new_job
    jobs[new_job.id_].status = JobStatus.STARTED
    result = await get_prediction_result(
        order_id,
        model,
        config,
        repository,
    )
    jobs[new_job.id_].result = result
    jobs[new_job.id_].status = JobStatus.DONE
