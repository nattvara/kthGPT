from datetime import datetime
import peewee

from .base import Base
from .message import Message


class Analysis(Base):
    lecture_id = peewee.IntegerField(null=False, index=True)  # not sure how to make this a foreign key field, due to circular imports
    state = peewee.CharField(null=False, default='waiting')
    mp4_progress = peewee.IntegerField(null=False, default=0)
    mp3_progress = peewee.IntegerField(null=False, default=0)
    transcript_progress = peewee.IntegerField(null=False, default=0)
    summary_progress = peewee.IntegerField(null=False, default=0)

    class State:
        WAITING = 'waiting'
        IDLE = 'idle'
        FAILURE = 'failure'
        DOWNLOADING = 'downloading'
        EXTRACTING_AUDIO = 'extracting_audio'
        TRANSCRIBING_LECTURE = 'transcribing_lecture'
        SUMMARISING_LECTURE = 'summarising_lecture'
        READY = 'ready'

    def refresh(self):
        update = Analysis.get(self.id)
        self.state = update.state
        self.mp4_progress = update.mp4_progress
        self.mp3_progress = update.mp3_progress
        self.transcript_progress = update.transcript_progress
        self.summary_progress = update.summary_progress

    def get_last_message(self):
        return (Message
                .filter(Message.analysis_id == self.id)
                .order_by(Message.created_at.desc())
                .first())

    def seems_to_have_crashed(self) -> bool:
        msg = self.get_last_message()
        now = datetime.now()
        return False

    def overall_progress(self):
        mp4_weight = 1
        mp3_weight = 3
        transcript_weight = 15
        summary_weight = 10

        weighted_mp4 = self.mp4_progress * mp4_weight
        weighted_mp3 = self.mp3_progress * mp3_weight
        weighted_transcript = self.transcript_progress * transcript_weight
        weighted_summary = self.summary_progress * summary_weight

        total_weight = mp4_weight + mp3_weight + transcript_weight + summary_weight
        return int((weighted_mp4 + weighted_mp3 + weighted_transcript + weighted_summary) / total_weight)

    def to_dict(self):
        msg = self.get_last_message()
        if msg is not None:
            msg_dict = msg.to_dict()
        else:
            msg_dict = None

        return {
            'analysis_id': self.id,
            'state': self.state,
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'last_message': msg_dict,
            'mp4_progress': self.mp4_progress,
            'mp3_progress': self.mp3_progress,
            'transcript_progress': self.transcript_progress,
            'summary_progress': self.summary_progress,
            'overall_progress': self.overall_progress(),
        }
