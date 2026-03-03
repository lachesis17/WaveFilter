import numpy as np
import math

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QLabel,
                               QVBoxLayout)

MAX_SAMPLES = 500_000


def decimate_signal(signal, sample_rate) -> tuple[np.ndarray, int]:
    """
    Decimates signal to MAX_SAMPLES.
    scipy.signal.decimate in chained steps of ≤8 so the
    filter remainS okay for large factors.
    """
    n = len(signal)
    if n <= MAX_SAMPLES:
        return signal, sample_rate

    from scipy.signal import decimate

    remaining = math.ceil(n / MAX_SAMPLES)
    while remaining > 1:
        step = min(remaining, 4)
        signal = decimate(signal, step, zero_phase=True)
        sample_rate = sample_rate / step
        remaining = math.ceil(remaining / step)

    return signal, int(sample_rate)


class ColumnPickerDialog(QDialog):
    """
    Dialog to select a signal column from an Excel/CSV file.
    """
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Signal Column")
        self.setMinimumWidth(320)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Choose the column to use as the signal:"))
        self.combo = QComboBox()
        self.combo.addItems(columns)
        layout.addWidget(self.combo)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_column(self):
        return self.combo.currentText()


class FileLoadWorker(QObject):
    """
    Worker to async load a file in a separate thread.
    """
    finished = Signal(object)  # (full_signal, full_rate, display_signal, display_rate)
    error = Signal(str)

    def __init__(self, loader_func, path):
        super().__init__()
        self._loader_func = loader_func
        self._path = path

    def run(self):
        try:
            signal, sample_rate = self._loader_func(self._path)
            display_signal, display_rate = decimate_signal(signal, sample_rate)
            self.finished.emit((signal, sample_rate, display_signal, display_rate))
        except Exception as e:
            print(e)
            self.error.emit(str(e))
