import logging
import uuid

class TraceLogger:
    def __init__(self, name='project_dashboard'):
        self.logger = logging.getLogger(name)
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [trace_id=%(trace_id)s] %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def info(self, message, trace_id=None):
        extra = {'trace_id': trace_id or str(uuid.uuid4())}
        self.logger.info(message, extra=extra)
