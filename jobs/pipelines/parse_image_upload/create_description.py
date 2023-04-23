from db.models import ImageUpload
import tools.text.prompts
from db.crud import (
    get_image_upload_by_public_id
)
import tools.text.ai


def job(image_id: str, language: str):
    upload = get_image_upload_by_public_id(image_id)
    if upload is None:
        raise ValueError(f'image {image_id} was not found')

    if language == ImageUpload.Language.ENGLISH:
        prompt = tools.text.prompts.describe_text_content_in_image_english(upload)
    elif language == ImageUpload.Language.SWEDISH:
        prompt = tools.text.prompts.describe_text_content_in_image_swedish(upload)
    else:
        raise ValueError(f'unkown language {language}')

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
        if language == ImageUpload.Language.ENGLISH:
            upload.description_en = response
            upload.create_description_en_ok = True
            upload.create_description_en_failure_reason = None
        elif language == ImageUpload.Language.SWEDISH:
            upload.description_sv = response
            upload.create_description_sv_ok = True
            upload.create_description_sv_failure_reason = None
        else:
            raise ValueError(f'unkown language {language}')

        upload.save()
    except Exception as e:
        upload.refresh()
        if language == ImageUpload.Language.ENGLISH:
            upload.create_description_en_ok = False
            upload.create_description_en_failure_reason = str(e)
        elif language == ImageUpload.Language.SWEDISH:
            upload.create_description_sv_ok = False
            upload.create_description_sv_failure_reason = str(e)
        else:
            raise ValueError(f'unkown language {language}')

        upload.save()
        raise e
