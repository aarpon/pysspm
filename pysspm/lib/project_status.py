from enum import StrEnum


class ProjectStatus(StrEnum):
    new = ("new",)
    feedback = ("feedback",)
    in_progress = ("in progress",)
    waiting_for_data = ("waiting for data",)
    superseded = ("superseded",)
    dropped = ("dropped",)
    completed = ("completed",)

    def is_open(self):
        if self.value in ["new", "feedback", "in progress", "waiting for data"]:
            return True
        return False
