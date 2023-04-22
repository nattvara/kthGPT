from typing import List, Optional

from db.models import Analysis, ImageUpload
import tools.text.prompts as prompts
import tools.text.ai

LABELS = [
    # Architecture
    'Sustainability Environmental Engineering',
    'Architecture',
    'History of Science, Technology Environment',

    # Computer science
    'Communication',
    'Computer Science',
    'Introductory Programming',
    'Advanced Programming Techniques',
    'Visualization and Graphics',
    'Theoretical Computer Science',
    'Software Engineering and Security',
    'Media Technology Interaction Design',
    'Speech, Music, Hearing',
    'Machine Learning and AI',

    # Electrical Engineering
    'Control Theory',
    'Communications',
    'Intelligent Systems',
    'Information Communication Technology',
    'Electrical Engineering',
    'Fusion Plasma Physics',

    # Biotechnology
    'Biotechnology',
    'Biomedical Engineering Health Systems',
    'Ergonomics and Work Environment',

    # Chemistry
    'Chemistry',
    'Organic Chemistry',
    'Inorganic Chemistry',
    'Analytical and Physical Chemistry',
    'Specialized and Applied Chemistry',

    # Industrial engineering and learning sciences
    'Energy Technology',
    'Learning in Engineering Sciences',
    'Industrial Engineering Management',
    'Industrial Economics Management',
    'Machine Design',
    'Materials Science Engineering',
    'Energy Technology',
    'Sustainable Production Development',

    # Engineering Sciences
    'Engineering Sciences',

    # Mathematics
    'Mathematics',
    'Basic Mathematics and Foundations',
    'Analysis and Calculus',
    'Algebra and Geometry',
    'Probability Theory',
    'Statistics',
    'Applied Mathematics and Computational Methods'

    # Physics
    'Acoustics',
    'Solid Mechanics',
    'Mechanics',
    'Physics',
    'Theoretical Physics',
    'Applied Physics',
]


class SubjectClassifier:

    def __init__(
        self,
        what: str,
        priority: int,
        upload: Optional[ImageUpload] = None,
        analysis: Optional[Analysis] = None,
    ) -> None:
        self.what = what
        self.priority = priority
        self.upload = upload
        self.analysis = analysis
        self.custom_labels = None

        self.lowercase_labels = {}
        for (idx, label) in enumerate(self.get_labels()):
            self.lowercase_labels[label.lower()] = idx

    class Priority:
        DEFAULT = 0
        HIGH = 1
        LOW = 2

    @staticmethod
    def create_classifier_for(
        what: str,
        priority=Priority.DEFAULT,
        upload: Optional[ImageUpload] = None,
        analysis: Optional[Analysis] = None,
    ):
        return SubjectClassifier(what, priority, upload, analysis)

    def override_labels(self, labels: List[str]):
        self.custom_labels = labels
        self.lowercase_labels = {}
        for (idx, label) in enumerate(labels):
            self.lowercase_labels[label.lower()] = idx

    def get_labels(self) -> List[str]:
        if self.custom_labels is not None:
            return self.custom_labels
        return LABELS

    def classify(
        self,
        string: str,
        target_number_of_labels: int = 3,
        validation_prompt=False
    ) -> List[str]:
        if validation_prompt:
            prompt = self.create_validation_prompt(string)
        else:
            prompt = self.create_prompt(string, target_number_of_labels)

        if self.priority == self.Priority.HIGH:
            response = self.high_priority_request(prompt)
        elif self.priority == self.Priority.LOW:
            response = self.low_priority_request(prompt)
        else:
            response = self.default_priority_request(prompt)

        classification = self.parse_response(response)
        return classification

    def create_prompt(self, text: str, target_number_of_labels: int) -> str:
        return prompts.create_classification_prompt_for_subjects(
            self.what,
            target_number_of_labels,
            self.get_labels(),
            text,
        )

    def create_validation_prompt(self, text: str) -> str:
        return prompts.create_validation_prompt_for_subjects(
            self.what,
            self.get_labels(),
            text,
        )

    def parse_response(self, gpt_response: str) -> list:
        out = []
        lines = gpt_response.split('\n')
        for line in lines:
            if line == '':
                continue

            for label in self.lowercase_labels:
                if label in line.lower():
                    original_case_label = self.get_labels()[self.lowercase_labels[label]]

                    if original_case_label not in out:
                        out.append(original_case_label)

        return out

    def default_priority_request(self, prompt: str) -> str:
        upload_id = None
        if self.upload is not None:
            upload_id = self.upload.id

        analysis_id = None
        if self.analysis is not None:
            analysis_id = self.analysis.id

        return tools.text.ai.gpt3(
            prompt,
            time_to_live=60 * 2,  # 2 mins
            max_retries=4,
            retry_interval=[
                5,
                15,
                30,
                60,
            ],
            upload_id=upload_id,
            analysis_id=analysis_id,
        )

    def high_priority_request(self, prompt: str) -> str:
        upload_id = None
        if self.upload is not None:
            upload_id = self.upload.id

        analysis_id = None
        if self.analysis is not None:
            analysis_id = self.analysis.id

        return tools.text.ai.gpt3(
            prompt,
            time_to_live=60,  # 1 mins
            max_retries=5,
            retry_interval=[
                5,
                10,
                10,
                10,
                10,
            ],
            upload_id=upload_id,
            analysis_id=analysis_id,
        )

    def low_priority_request(self, prompt: str) -> str:
        upload_id = None
        if self.upload is not None:
            upload_id = self.upload.id

        analysis_id = None
        if self.analysis is not None:
            analysis_id = self.analysis.id

        return tools.text.ai.gpt3(
            prompt,
            time_to_live=60 * 60 * 10,  # 5 hrs
            max_retries=10,
            retry_interval=[
                10,
                30,
                60,
                2 * 60,
                2 * 60,
                10 * 60,
                30 * 60,
                2 * 60 * 60,
                30 * 60,
                30 * 60,
            ],
            upload_id=upload_id,
            analysis_id=analysis_id,
        )
