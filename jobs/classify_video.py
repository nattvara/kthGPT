import tempfile
import logging
import os.path

from tools.audio.extraction import extract_mp3_len
from tools.audio.transcription import save_text
from tools.youtube.download import download_mp3
from tools.audio.shorten import shorten_mp3
from db.models import Lecture, Analysis
from tools.text import prompts, ai
from db.crud import (
    get_lecture_by_public_id_and_language,
    save_message_for_analysis
)
import jobs


# 20min timeout
TIMEOUT = 20 * 60

# 7 minutes
SAMPLE_SIZE_SECONDS = 7 * 60

# 4 hours
MAX_ALLOWED_VIDEO_LENGTH = 4 * 60 * 60


def job(lecture_id: str, language: str):
    logger = logging.getLogger('rq.worker')

    lecture = get_lecture_by_public_id_and_language(lecture_id, language)
    if lecture is None:
        raise ValueError(f'lecture {lecture_id} not found')

    if lecture.source != Lecture.Source.YOUTUBE:
        raise ValueError(f'classification only supports youtube lectures, source was {lecture.source}')

    lecture.refresh()
    analysis = lecture.get_last_analysis()
    analysis.state = Analysis.State.CLASSIFYING
    analysis.save()
    save_message_for_analysis(analysis, 'Classifying video', 'Trying to classify if the video is relevant for kthGPT')

    temp_path = tempfile.NamedTemporaryFile(mode='w+', delete=False)
    temp_path_mp3 = download_mp3(lecture.content_link(), temp_path.name, SAMPLE_SIZE_SECONDS)

    length = extract_mp3_len(temp_path_mp3)
    if length > MAX_ALLOWED_VIDEO_LENGTH:
        logger.info(f'video was to long {length} > {MAX_ALLOWED_VIDEO_LENGTH}')
        lecture.approved = False
        lecture.save()
        temp_path.close()
        return

    shorten_mp3(temp_path_mp3, SAMPLE_SIZE_SECONDS)

    transcript_dir = f'{temp_path_mp3}.transcription'
    save_text(temp_path_mp3, lecture, transcript_dir, save_progress=False)

    transcribed_text_path = f'{transcript_dir}/{os.path.basename(temp_path_mp3)}.txt'

    with open(transcribed_text_path, 'r') as file:
        text = file.read()

    if lecture.language == Lecture.Language.ENGLISH:
        prompt = prompts.create_text_to_decide_if_video_is_appropriate_english(text)
    elif lecture.language == Lecture.Language.SWEDISH:
        prompt = prompts.create_text_to_decide_if_video_is_appropriate_swedish(text)
    else:
        raise ValueError(f'unsupported value error {lecture.language}')

    try:
        response = ai.gpt3(
            prompt,
            time_to_live=60 * 60 * 5,  # 5 hrs
            max_retries=10,
            retry_interval=[
                10,
                30,
                60,
                2 * 60,
                10 * 60,
                20 * 60,
                30 * 60,
                2 * 60 * 60,
                30 * 60,
                30 * 60,
            ],
            analysis_id=analysis.id,
        )
    except Exception as e:
        lecture.refresh()
        analysis = lecture.get_last_analysis()
        analysis.state = Analysis.State.FAILURE
        analysis.save()
        save_message_for_analysis(analysis, 'Classification failed', 'OpenAI is likely overloaded.')
        raise e

    category_is_ok = False
    if prompts.CATEGORY_RECORDED_LECTURE.lower() in response.lower():
        category_is_ok = True

    logger.info(f'response from openAI: {response}')

    lecture.approved = category_is_ok
    lecture.save()

    if category_is_ok:
        jobs.schedule_analysis_of_lecture(lecture)
    else:
        analysis = lecture.get_last_analysis()
        analysis.state = Analysis.State.DENIED
        analysis.save()

    temp_path.close()


# Test run the job
if __name__ == '__main__':
    job('L3pk_TBkihU', Lecture.Language.ENGLISH)
