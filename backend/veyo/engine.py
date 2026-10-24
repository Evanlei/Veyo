"""One CPU predictor per process; overlapping inference fails with a retryable busy error."""
import threading
from .config import Settings


class EngineBusy(RuntimeError):
    pass


class InferenceEngine:
    def __init__(self, settings: Settings, predictor_factory=None):
        self.settings = settings
        self._factory = predictor_factory
        self._predictor = None
        self._lock = threading.Lock()
        self.last_error = None

    @property
    def status(self):
        return {"model": "DeepGaze IIE", "device": "cpu", "loaded": self._predictor is not None,
                "busy": self._lock.locked(), "engine": "deepgaze-iie", "fallback": False}

    def predict(self, image):
        if not self._lock.acquire(blocking=False):
            raise EngineBusy("The model is analyzing another creative. Try again shortly.")
        try:
            if self._predictor is None:
                if self._factory:
                    self._predictor = self._factory()
                else:
                    import torch
                    from .inference import DeepGazePredictor
                    torch.set_num_threads(self.settings.threads)
                    self._predictor = DeepGazePredictor()
            result = self._predictor.predict(image)
            self.last_error = None
            return result
        except Exception:
            self.last_error = "Inference failed. No substitute prediction was generated."
            raise
        finally:
            self._lock.release()
