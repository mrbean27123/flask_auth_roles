from enum import Enum

class FlashError(str, Enum):
    SUCCESS = 'success'
    INFO = 'info'
    WARNING = 'warning'
    DANGER = 'danger'

    def __str__(self):
        return self.value