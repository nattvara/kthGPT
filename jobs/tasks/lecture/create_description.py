import logging

from db.crud import get_lecture_by_public_id_and_language
import tools.text.prompts as prompts
import tools.text.ai

# 5 mins
TIMEOUT = 5 * 60


def job(lecture_id: str, language: str):
    logger = logging.getLogger('rq.worker')

    lecture = get_lecture_by_public_id_and_language(lecture_id, language)
    if lecture is None:
        raise ValueError(f'lecture {lecture_id} not found')

    analysis = lecture.get_last_analysis()

    prompt = prompts.create_description_prompt(lecture)
    response = tools.text.ai.gpt3(
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

    lecture.refresh()
    lecture.description = response
    lecture.save()

    logger.info('done.')


# Test run the job
if __name__ == '__main__':
    job('1xrERtqmX3E', 'sv')
