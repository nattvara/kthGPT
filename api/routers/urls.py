from fastapi import Depends, APIRouter, HTTPException
from urllib.parse import urlparse
from pydantic import BaseModel
import re

from db.crud import get_url_by_sha, get_lecture_by_public_id
from db.models import URL, Lecture
from db import get_db

from jobs import get_queue, capture_preview, download_lecture
from tools.web.crawler import get_m3u8
from rq import Queue


router = APIRouter()


class InputModel(BaseModel):
    url: str


class OutputModel(BaseModel):
    url: str
    url_hash: str
    lecture_id: str


@router.post('/url', dependencies=[Depends(get_db)])
def parse_url(input_data: InputModel, queue: Queue = Depends(get_queue)) -> OutputModel:
    domain = urlparse(input_data.url).netloc
    if not domain.endswith('play.kth.se'):
        raise HTTPException(status_code=400, detail='Unsupported domain')

    sha = URL.make_sha(input_data.url)
    url = get_url_by_sha(sha)

    if url is None:
        url = URL(
            url=input_data.url,
            url_hash=URL.make_sha(input_data.url)
        )

        try:
            content_url = urlparse(get_m3u8(input_data.url)).path
        except:
            raise HTTPException(status_code=500, detail='Something went wrong while trying to get the lecture video')

        regex = r'^.*entryId\/(\w*)\/.*$'
        matches = re.finditer(regex, content_url, re.MULTILINE)
        match = next(matches)

        if not match:
            raise HTTPException(status_code=400, detail='Could not find the lecture id')

        url.lecture_id = match.group(1)
        url.save()

    lecture = get_lecture_by_public_id(url.lecture_id)
    if lecture is None:
        lecture = Lecture(public_id=url.lecture_id)
        lecture.save()

        queue.enqueue(capture_preview.job, lecture.public_id)
        queue.enqueue(download_lecture.job, lecture.public_id)

    return url.to_dict()
