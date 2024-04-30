def calculate_score(question_timer: float, response_time: float, max_score: float, attempt_no: int):
    return 1 - (response_time / question_timer) / 2 * max_score  # TODO: factor in reattempts if needed

