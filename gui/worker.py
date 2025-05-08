# gui/worker.py
from PyQt5.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error    = pyqtSignal(tuple)
    result   = pyqtSignal(object)

class Worker(QRunnable):
    """
    QRunnable qui exécute une fonction et émet des signaux.
    """
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self.signals.error.emit((e, tb))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()
