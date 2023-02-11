from fastapi import Depends, APIRouter, HTTPException, Response
from typing import Union, List
from pydantic import BaseModel

from db.crud import get_all_lectures, get_lecture
from db import get_db

router = APIRouter()


class LectureOutputModel(BaseModel):
    public_id: str
    preview_uri: Union[str, None] = None
    content_link: Union[str, None] = None
    mp4_progress: int


@router.get('/lectures', dependencies=[Depends(get_db)])
def get_all() -> List[LectureOutputModel]:
    lectures = get_all_lectures()

    out = []
    for lecture in lectures:
        out.append(lecture.to_dict())

    return out


@router.get('/lectures/{public_id}/preview', dependencies=[Depends(get_db)])
def get_preview(public_id: str):
    lecture = get_lecture(public_id)
    if lecture is None:
        raise HTTPException(status_code=404)

    if lecture.img_preview is None:
        raise HTTPException(status_code=404)

    with open(lecture.img_preview, 'rb') as file:
        image_bytes: bytes = file.read()
        return Response(content=image_bytes, media_type='image/png')
