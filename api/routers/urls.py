from fastapi import Depends, APIRouter, HTTPException
from urllib.parse import urlparse
from pydantic import BaseModel
import re

from db.crud import get_url_by_sha, get_lecture_by_public_id_and_language
from db.models import URL, Lecture
from db import get_db

from jobs import (
    get_queue,
    capture_preview,
    download_lecture,
    extract_audio,
    transcribe_audio,
    summarise_transcript,
)
from tools.web.crawler import get_m3u8
from rq import Queue


router = APIRouter()


class InputModel(BaseModel):
    url: str
    language: str


class OutputModel(BaseModel):
    uri: str


@router.post('/url', dependencies=[Depends(get_db)])
def parse_url(input_data: InputModel, queue: Queue = Depends(get_queue)) -> OutputModel:
    domain = urlparse(input_data.url).netloc
    if not domain.endswith('play.kth.se'):
        raise HTTPException(status_code=400, detail='Unsupported domain')

    if input_data.language == str(Lecture.Language.ENGLISH):
        lang = Lecture.Language.ENGLISH
    elif input_data.language == str(Lecture.Language.SWEDISH):
        lang = Lecture.Language.SWEDISH
    else:
        raise HTTPException(status_code=400, detail='Unsupported language')

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

    lecture = get_lecture_by_public_id_and_language(url.lecture_id, lang)
    if lecture is None:
        lecture = Lecture(public_id=url.lecture_id, language=lang)
        lecture.save()

        queue.enqueue(capture_preview.job, lecture.public_id, lecture.language)
        with queue.connection.pipeline() as pipe:
            jobs = queue.enqueue_many(
                [
                    queue.prepare_data(download_lecture.job, [lecture.public_id, lecture.language]),
                    queue.prepare_data(extract_audio.job, [lecture.public_id, lecture.language]),
                    Queue.prepare_data(transcribe_audio.job, [lecture.public_id, lecture.language], timeout=transcribe_audio.TRANSCRIPTION_JOB_TIMEOUT),
                    Queue.prepare_data(summarise_transcript.job, [lecture.public_id, lecture.language], timeout=summarise_transcript.SUMMARY_JOB_TIMEOUT),
                ],
                pipeline=pipe,
            )
            pipe.execute()

    return {
        'uri': url.lecture_uri(lang)
    }
