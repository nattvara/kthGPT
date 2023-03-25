from db.models import Lecture, Analysis, Message
from db.crud import save_message_for_analysis
from jobs.tasks.lecture import clean_lecture


def test_clean_lecture_deletes_all_but_last_message_for_lecture():
    lecture = Lecture(
        public_id='some_id',
        language=Lecture.Language.SWEDISH,
    )
    lecture.save()
    analysis = Analysis(lecture_id=lecture.id, state=Analysis.State.READY)
    analysis.save()

    save_message_for_analysis(analysis, 'some title', 'msg 1')
    save_message_for_analysis(analysis, 'some title', 'msg 2')
    save_message_for_analysis(analysis, 'some title', 'msg 3')
    save_message_for_analysis(analysis, 'some title', 'msg 4')

    clean_lecture.job(lecture.public_id, lecture.language)

    messages = Message.filter(Message.analysis_id == analysis.id)
    assert len(messages) == 1
