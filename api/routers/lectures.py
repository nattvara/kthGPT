from fastapi import Depends, APIRouter, HTTPException, Response
from typing import Union, List
from pydantic import BaseModel
import random as rand

from db.crud import get_all_lectures, get_lecture_by_public_id_and_language
from db.models import Lecture
from db import get_db

router = APIRouter()


class LectureOutputModel(BaseModel):
    public_id: str
    language: str
    words: int
    length: int
    state: str
    preview_uri: Union[str, None] = None
    transcript_uri: Union[str, None] = None
    summary_uri: Union[str, None] = None
    content_link: Union[str, None] = None
    mp4_progress: int
    mp3_progress: int
    transcript_progress: int
    summary_progress: int
    overall_progress: int


class LectureSummaryOutputModel(BaseModel):
    public_id: str
    language: str
    state: str
    content_link: Union[str, None] = None
    overall_progress: int


@router.get('/lectures', dependencies=[Depends(get_db)])
def get_all(summary: Union[bool, None] = None, random: Union[bool, None] = None) -> List[Union[LectureOutputModel, LectureSummaryOutputModel]]:
    lectures = get_all_lectures()

    out = []
    for lecture in lectures:
        if random and lecture.state != Lecture.State.READY:
            continue

        if summary:
            out.append(lecture.to_summary_dict())
        else:
            out.append(lecture.to_dict())

    if random and len(out) == 0:
        return []

    if random:
        index = rand.randint(0, len(out) - 1)
        return [out[index]]

    if summary:
        out.reverse()

    return out


@router.get('/lectures/{public_id}/{language}', dependencies=[Depends(get_db)])
def get_lecture(public_id: str, language: str):
    lecture = get_lecture_by_public_id_and_language(public_id, language)
    if lecture is None:
        raise HTTPException(status_code=404)

    return lecture.to_dict()


@router.get('/lectures/{public_id}/{language}/preview', dependencies=[Depends(get_db)])
def get_preview(public_id: str, language: str):
    lecture = get_lecture_by_public_id_and_language(public_id, language)
    if lecture is None:
        raise HTTPException(status_code=404)

    if lecture.img_preview is None:
        raise HTTPException(status_code=404)

    with open(lecture.img_preview, 'rb') as file:
        image_bytes: bytes = file.read()
        return Response(content=image_bytes, media_type='image/png')


@router.get('/lectures/{public_id}/{language}/transcript', dependencies=[Depends(get_db)])
def get_transcript(public_id: str, language: str):
    lecture = get_lecture_by_public_id_and_language(public_id, language)
    if lecture is None:
        raise HTTPException(status_code=404)

    if lecture.transcript_filepath is None:
        raise HTTPException(status_code=404)

    return Response(
        content=lecture.transcript_text(),
        media_type='text/plain'
    )


@router.get('/lectures/{public_id}/{language}/summary', dependencies=[Depends(get_db)])
def get_transcript(public_id: str, language: str):
    lecture = get_lecture_by_public_id_and_language(public_id, language)
    if lecture is None:
        raise HTTPException(status_code=404)

    if lecture.summary_filepath is None:
        raise HTTPException(status_code=404)

    return Response(
        content=lecture.summary_text(),
        media_type='text/plain'
    )
