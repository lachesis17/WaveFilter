import json
import math
from pathlib import Path

import h5py
import librosa
import numpy as np
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QColorDialog, QComboBox, QDialog,
                               QDialogButtonBox, QFormLayout, QLabel,
                               QPushButton, QVBoxLayout)
import pyqtgraph as pg
from scipy.signal import decimate

from src.filters import Filters

# max num samples for pyqtgraph, signal above this is decimated with
# an anti-aliasing filter on the worker thread before loading into UI
MAX_SAMPLES = 5_000_000


def decimate_signal(signal, sample_rate) -> tuple[np.ndarray, int]:
    """
    Decimates signal to MAX_SAMPLES.
    scipy.signal.decimate in chained steps of ≤8 so the
    filter remainS okay for large factors.
    """
    n = len(signal)
    if n <= MAX_SAMPLES:
        return signal, sample_rate

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


class LineColorsDialog(QDialog):
    """
    Dialog to pick colors for raw, filtered, and FFT plot lines.
    Colors are tuples of (r, g, b).
    Emits colorsChanged(dict) on color update.
    """
    colorsChanged = Signal(dict)

    def __init__(self, current_colors: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Line Colors")
        self.setMinimumWidth(300)
        self._colors = dict(current_colors)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._buttons = {}
        for key, label in (('raw', 'Raw signal'), ('filtered', 'Filtered signal'), ('fft', 'FFT')):
            btn = QPushButton()
            btn.setFixedHeight(28)
            self._update_button(btn, self._colors[key])
            btn.clicked.connect(lambda _, k=key, b=btn: self._pick_color(k, b))
            form.addRow(label + ':', btn)
            self._buttons[key] = btn

        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        reset_btn = buttons.addButton("Reset to defaults", QDialogButtonBox.ResetRole)
        reset_btn.setMinimumWidth(125)
        reset_btn.clicked.connect(self._reset_defaults)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _update_button(self, btn: QPushButton, rgb: tuple):
        r, g, b = rgb
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        text_color = '#000000' if luminance > 128 else '#ffffff'
        btn.setStyleSheet(
            f'background-color: rgb({r},{g},{b}); color: {text_color};'
        )
        btn.setText(f'rgb({r}, {g}, {b})')

    def _reset_defaults(self):
        defaults = {'raw': (200, 200, 200), 'filtered': (150, 0, 255), 'fft': (0, 200, 0)}
        for key, rgb in defaults.items():
            self._colors[key] = rgb
            self._update_button(self._buttons[key], rgb)
        self.colorsChanged.emit(dict(self._colors))

    def _pick_color(self, key: str, btn: QPushButton):
        original = self._colors[key]
        dlg = QColorDialog(QColor(*original), self)
        dlg.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog)
        dlg.setWindowTitle(f'Pick color — {key}')

        def on_live(color):
            rgb = (color.red(), color.green(), color.blue())
            self._colors[key] = rgb
            self._update_button(btn, rgb)
            self.colorsChanged.emit(dict(self._colors))

        dlg.currentColorChanged.connect(on_live)

        if dlg.exec() != QColorDialog.Accepted:
            self._colors[key] = original
            self._update_button(btn, original)
            self.colorsChanged.emit(dict(self._colors))

    def get_colors(self) -> dict:
        return dict(self._colors)


class FilterWorker(QObject):
    """
    Worker to apply a standard filter in a separate thread.
    """
    finished = Signal(object)  # tuple of filter params and result
    error = Signal(str)

    def __init__(self, signal, sample_rate, filter_type,
                 low_freq, high_freq, order,
                 filter_design, ripple, attenuation, window_arg):
        super().__init__()
        self._signal = signal
        self._sample_rate = sample_rate
        self._filter_type = filter_type
        self._low_freq = low_freq
        self._high_freq = high_freq
        self._order = order
        self._filter_design = filter_design
        self._ripple = ripple
        self._attenuation = attenuation
        self._window_arg = window_arg

    def run(self):
        try:
            result = Filters.apply_standard_filter(
                self._signal, self._sample_rate, self._filter_type,
                self._low_freq, self._high_freq, int(self._order),
                self._filter_design, self._ripple, self._attenuation,
            )
            self.finished.emit((result, self._filter_type,
                                self._low_freq, self._high_freq, self._order,
                                self._window_arg, self._filter_design,
                                self._ripple, self._attenuation))
        except Exception as e:
            print(e)
            self.error.emit(str(e))


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


class SessionSaveWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, path, raw_full, rate_full, applied_filters, start_pos, stop_pos):
        super().__init__()
        self._path = path
        self._raw_full = raw_full
        self._rate_full = rate_full
        self._applied_filters = applied_filters
        self._start_pos = start_pos
        self._stop_pos = stop_pos

    def run(self):
        try:
            # normalize to int16 for compact storage
            signal = self._raw_full
            peak = np.max(np.abs(signal)) or 1.0
            int16_data = (signal / peak * 32767).astype(np.int16)
            with h5py.File(self._path, 'w') as f:
                f.create_dataset('raw_full', data=int16_data, compression='gzip', compression_opts=9)
                f.attrs['peak'] = peak
                f.attrs['rate_full'] = self._rate_full
                f.attrs['applied_filters'] = json.dumps(self._applied_filters)
                f.attrs['start_pos'] = self._start_pos
                f.attrs['stop_pos'] = self._stop_pos
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class SessionLoadWorker(QObject):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, path):
        super().__init__()
        self._path = path

    def run(self):
        try:
            with h5py.File(self._path, 'r') as f:
                # restore from int16 using saved peak amplitude
                peak = float(f.attrs.get('peak', 1.0))
                raw_full = f['raw_full'][:].astype(np.float64) / 32767.0 * peak
                rate_full = int(f.attrs['rate_full'])
                applied_filters = json.loads(f.attrs['applied_filters'])
                start_pos = float(f.attrs.get('start_pos', 0.0))
                stop_pos = float(f.attrs.get('stop_pos', len(raw_full) / rate_full))
            display_signal, display_rate = decimate_signal(raw_full, rate_full)
            self.finished.emit((display_signal, display_rate, raw_full, rate_full, applied_filters, start_pos, stop_pos))
        except Exception as e:
            self.error.emit(str(e))


class ExportWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, path, signal, sample_rate, applied_filters):
        super().__init__()
        self._path = path
        self._signal = signal
        self._sample_rate = sample_rate
        self._applied_filters = applied_filters

    def run(self):
        try:
            # apply filters to full sample rate signal
            signal = self._signal.copy()
            for f_type, f_args in self._applied_filters:
                if f_type == "Pitch Shift":
                    signal = librosa.effects.pitch_shift(signal, sr=self._sample_rate, n_steps=f_args[0])
                else:
                    low_freq, high_freq, order = f_args[0], f_args[1], int(f_args[2])
                    filter_design = f_args[4] if len(f_args) > 4 else 'butter'
                    ripple = f_args[5] if len(f_args) > 5 else 3.0
                    attenuation = f_args[6] if len(f_args) > 6 else 60.0
                    result = Filters.apply_standard_filter(
                        signal, self._sample_rate, f_type, low_freq, high_freq, order,
                        filter_design, ripple, attenuation)
                    if result is not None:
                        signal = result

            ext = Path(self._path).suffix.lower()
            if ext in ('.wav', '.mp3'):
                import soundfile as sf
                peak = np.max(np.abs(signal)) or 1.0
                normalized = (signal / peak).astype(np.float32)
                sf.write(self._path, normalized, self._sample_rate)
            elif ext == '.xlsx':
                import pandas as pd
                time = np.arange(len(signal)) / self._sample_rate
                df = pd.DataFrame({'Time (s)': time, 'Amplitude': signal})
                df.to_excel(self._path, index=False)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class PlaybackLine(pg.InfiniteLine):
    doubleClicked = Signal()

    def mouseDoubleClickEvent(self, ev):
        self.doubleClicked.emit()
        ev.accept()
