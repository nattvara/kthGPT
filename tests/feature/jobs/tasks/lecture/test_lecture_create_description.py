from jobs.tasks.lecture import create_description


def test_create_description_job_saves_description(mocker, analysed_lecture):
    description = 'a lecture about the meaning of life'
    mocker.patch('tools.text.ai.gpt3', return_value=description)

    # Classify the video
    create_description.job(analysed_lecture.public_id, analysed_lecture.language)
    analysed_lecture.refresh()

    assert analysed_lecture.description == description
