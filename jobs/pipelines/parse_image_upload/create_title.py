import tools.text.prompts
from db.crud import (
    get_image_upload_by_public_id
)
import tools.text.ai


def job(image_id: str):
    upload = get_image_upload_by_public_id(image_id)
    if upload is None:
        raise ValueError(f'image {image_id} was not found')

    prompt = tools.text.prompts.create_title_from_assignment(upload)

    try:
        response = tools.text.ai.gpt3(
            prompt,
            time_to_live=60 * 2,  # 2 mins
            max_retries=5,
            retry_interval=[
                5,
                10,
                10,
                30,
                30,
            ],
            upload_id=upload.id,
        )

        upload.refresh()
        upload.title = response
        upload.create_title_ok = True
        upload.create_title_failure_reason = None

        upload.save()
    except Exception as e:
        upload.refresh()
        upload.create_title_ok = False
        upload.create_title_failure_reason = str(e)
        upload.save()
        raise e
