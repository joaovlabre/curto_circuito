"""QThread wrapper para execução do estudo sem travar a GUI."""

from PyQt6.QtCore import QThread, pyqtSignal
from ..models.network import Network
from ..models.results import StudyResults
from ..engine.study import run_study


class StudyWorker(QThread):
    result_ready = pyqtSignal(object)   # StudyResults
    error = pyqtSignal(str)

    def __init__(self, network: Network, use_cmax: bool = True) -> None:
        super().__init__()
        self._network = network
        self._use_cmax = use_cmax

    def run(self) -> None:
        try:
            results = run_study(self._network, self._use_cmax)
            self.result_ready.emit(results)
        except Exception as exc:
            self.error.emit(str(exc))
