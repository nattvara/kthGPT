from typing import List, Optional

from db.models import Analysis, ImageUpload
from .subject import SubjectClassifier
from config.logger import log


class SubjectMultipassClassifier(SubjectClassifier):

    def __init__(
        self,
        what: str,
        priority: int,
        upload: Optional[ImageUpload] = None,
        analysis: Optional[Analysis] = None,
        samples: Optional[int] = 1,
    ):
        super().__init__(what, priority, upload, analysis)
        self.samples = samples
        self.base_classifier = SubjectClassifier(what, priority, upload, analysis)

    @staticmethod
    def create_classifier_for(
        what: str,
        priority=SubjectClassifier.Priority.DEFAULT,
        upload: Optional[ImageUpload] = None,
        analysis: Optional[Analysis] = None,
        samples: Optional[int] = 1,
    ):
        return SubjectMultipassClassifier(what, priority, upload, analysis, samples=samples)

    def classify(self, string: str, target_number_of_labels: int = 3) -> List[str]:
        subjects = []

        for i in range(self.samples):
            log().info(f'SubjectMultipassClassifier sample {i + 1}/{self.samples}')

            classification = self.base_classifier.classify(string, 4)

            for subject in classification:
                if subject not in subjects:
                    subjects.append(subject)

        if self.samples == 1:
            return subjects

        self.base_classifier.override_labels(subjects)

        validation_pass = self.base_classifier.classify(string, 0, validation_prompt=True)

        # Sometimes yields an empty result or bad labels, re-running it will ask GPT-3 again,
        # with a good chance of producing a better result
        if len(validation_pass) == 0:
            validation_pass = self.base_classifier.classify(string, 0, validation_prompt=True)

        return validation_pass
