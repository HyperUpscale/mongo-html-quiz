class Quiz:
    def __init__(self, quiz_id, name):
        self.quiz_id = quiz_id
        self.name = name

    def to_dict(self):
        return {
            'quiz_id': self.quiz_id,
            'name': self.name
        }

class Image:
    def __init__(self, quiz_id, category, score, image_data):
        self.quiz_id = quiz_id
        self.category = category
        self.score = score
        self.image_data = image_data

    def to_dict(self):
        return {
            'quiz_id': self.quiz_id,
            'category': self.category,
            'score': self.score,
            'image_data': self.image_data
        }

class ResultImage:
    def __init__(self, quiz_id, category, score_start, score_end, result_text, image_data):
        self.quiz_id = quiz_id
        self.category = category
        self.score_start = score_start
        self.score_end = score_end
        self.result_text = result_text
        self.image_data = image_data

    def to_dict(self):
        return {
            'quiz_id': self.quiz_id,
            'category': self.category,
            'score_start': self.score_start,
            'score_end': self.score_end,
            'result_text': self.result_text,
            'image_data': self.image_data
        }