import ctypes
import sys
import time as _time
import wave
import platform
from pathlib import Path

import librosa
import numpy as np
import pandas as pd
import sounddevice as sd
from PySide6.QtCore import Qt, QThread, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QDialog, QFileDialog,
                               QInputDialog, QLabel, QMainWindow, QMessageBox,
                               QProgressBar, QTreeWidgetItem, QVBoxLayout)
import pyqtgraph as pg

from src.config import ConfigManager
from src.filters import Filters
from src.helpers import PlaybackLine, FileLoadWorker, FilterWorker, ColumnPickerDialog, LineColorsDialog
from ui.wavefilter_ui import Ui_MainWindow

appid = 'WaveFilter'
if platform.system() == 'Windows':
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.filter_obj: Filters | None = None
        self._raw_filter_visible = True
        self._filtered_filter_visible = True

        self.raw_line = None
        self.filter_line = None
        self.fft_line = None
        self._start_line = None
        self._stop_line = None

        self._config_manager = ConfigManager()

        # thread state across async
        self._load_dialog = None
        self._pending_load_path = None
        self._load_thread = None
        self._load_worker = None
        self._filter_thread = None
        self._filter_worker = None

        self._playback_line = None
        self._playback_start_wall = 0.0
        self._playback_t_offset = 0.0
        self._playback_t_stop = 0.0
        self._paused_position = None
        self._is_playing = False
        self._updating_playback_pos = False

        ext = '.ico' if platform.system() == 'Windows' else '.icns' if platform.system() == 'Darwin' else '.png'
        self._icon_play = QIcon(f'ui/icons/play{ext}')
        self._icon_pause = QIcon(f'ui/icons/pause{ext}')
        self._icon_playing = QIcon(f'ui/icons/playing{ext}')
        self._icon_stop = QIcon(f'ui/icons/stop{ext}')

        self.setWindowIcon(QIcon(f'ui/icons/icon{ext}'))

        self._setup_plots()
        self._connect_signals()
        self._filter_changed_handler()

    def _setup_plots(self):
        self.fft_plot.setLabel('left', 'Amp')
        self.fft_plot.setLabel('bottom', 'Freq (Hz)')
        self.fft_plot.showGrid(x=True, y=True, alpha=0.3)
        self.fft_legend = self.fft_plot.addLegend(offset=(-10, 10))

        self.signal_plot.setLabel('left', 'Amp')
        self.signal_plot.setLabel('bottom', 'Time (s)')
        self.signal_plot.showGrid(x=True, y=True, alpha=0.3)
        self.signal_legend = self.signal_plot.addLegend(offset=(-10, -10))

    def _connect_signals(self):
        self.open_button.clicked.connect(self._load_file)
        self.generate_button.clicked.connect(self._generate_test_signal)
        self.play_button.clicked.connect(self._toggle_playback)
        self.stop_button.clicked.connect(self._stop_audio)
        self.apply_fft_button.clicked.connect(self._apply_fft_handler)
        self.apply_filter_button.clicked.connect(self._apply_filter_committed)
        self.clear_button.clicked.connect(self._clear_filters)

        self.preview_check.toggled.connect(self._preview_toggled)

        self.raw_visible_check.toggled.connect(lambda s: self._handle_filters_visible(s, 'raw'))
        self.filtered_visible_check.toggled.connect(lambda s: self._handle_filters_visible(s, 'filtered'))

        self.filter_combo.currentIndexChanged.connect(self._filter_changed_handler)

        for spinbox in (self.filter_low_spin, self.filter_high_spin):
            spinbox.valueChanged.connect(self._on_filter_param_changed)
        self.filter_order_spin.valueChanged.connect(self._on_filter_param_changed)
        self.window_check_filter.toggled.connect(self._on_filter_param_changed)
        self.filter_combo.currentIndexChanged.connect(self._on_filter_param_changed)
        self.filter_design_combo.currentIndexChanged.connect(self._filter_changed_handler)
        self.filter_design_combo.currentIndexChanged.connect(self._on_filter_param_changed)
        self.ripple_spin.valueChanged.connect(self._on_filter_param_changed)
        self.attenuation_spin.valueChanged.connect(self._on_filter_param_changed)

        for spinbox in (self.low_peak_freq_spin, self.high_peak_freq_spin,
                        self.min_peak_amp_spin, self.kalman_noise_spin):
            spinbox.valueChanged.connect(self._on_filter_param_changed)
        self.kalman_check.toggled.connect(self._on_filter_param_changed)
        self.normalize_check.toggled.connect(self._on_filter_param_changed)
        self.window_check_fft.toggled.connect(self._on_filter_param_changed)
        self.fft_mode_combo.currentIndexChanged.connect(self._on_filter_param_changed)

        self.actionLine_Colors.triggered.connect(self._open_line_colors_dialog)

    def _preview_toggled(self, checked):
        if not checked:
            self._apply_all_filters()
            self._replot()
            self._populate_legend()
        else:
            self._apply_filter_preview()

    def _on_filter_param_changed(self):
        if self.preview_check.isChecked():
            self._apply_filter_preview()

    def _filter_changed_handler(self):
        filter_type = self.filter_combo.currentText()

        self.label_filter_low.setText("Low Frequency")
        self.label_filter_high.setText("High Frequency")
        self.label_filter_order.setText("Order")
        self.filter_low_spin.setSuffix(" Hz")

        if filter_type == "Savitzky-Golay Filter":
            self.filter_low_spin.setEnabled(True)
            self.filter_high_spin.setEnabled(False)
            self.label_filter_low.setText("Window Length")
            self.label_filter_order.setText("Poly Order")
            self.filter_low_spin.setSuffix("")
            self._set_design_visible(False)
        elif filter_type == "IFFT / Kalman Filter":
            self.filter_low_spin.setEnabled(False)
            self.filter_high_spin.setEnabled(False)
            self._set_design_visible(False)
        elif filter_type == "Notch Filter":
            self.filter_low_spin.setEnabled(True)
            self.filter_high_spin.setEnabled(False)
            self._set_design_visible(False)
        elif filter_type == "Low Pass Filter":
            self.filter_low_spin.setEnabled(True)
            self.filter_high_spin.setEnabled(False)
            self._set_design_visible(True)
        elif filter_type == "High Pass Filter":
            self.filter_low_spin.setEnabled(False)
            self.filter_high_spin.setEnabled(True)
            self._set_design_visible(True)
        elif filter_type in ("Band Pass Filter", "Band Stop Filter"):
            self.filter_low_spin.setEnabled(True)
            self.filter_high_spin.setEnabled(True)
            self._set_design_visible(True)

    def _set_design_visible(self, visible: bool):
        self.label_filter_design.setVisible(visible)
        self.filter_design_combo.setVisible(visible)
        if visible:
            design = self.filter_design_combo.currentText()
            show_ripple = design in ("Chebyshev I", "Elliptic")
            show_atten = design in ("Chebyshev II", "Elliptic")
        else:
            show_ripple = False
            show_atten = False
        self.label_ripple.setVisible(show_ripple)
        self.ripple_spin.setVisible(show_ripple)
        self.label_attenuation.setVisible(show_atten)
        self.attenuation_spin.setVisible(show_atten)

    def _load_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open File", self._config_manager.get_last_directory(),
            "Audio & Data Files (*.wav *.mp3 *.xlsx *.xls *.csv);;WAV (*.wav);;MP3 (*.mp3);;Excel (*.xlsx *.xls);;CSV (*.csv);;All Files (*)"
        )
        if not path:
            return
        self._config_manager.update_last_directory(path)

        suffix = Path(path).suffix.lower()

        # dialogs need to stay in main thread
        if suffix in ('.xlsx', '.xls', '.csv'):
            try:
                signal, sample_rate = self._load_spreadsheet(path, suffix)
            except Exception as e:
                QMessageBox.critical(self, "Load error", str(e))
                return
            if signal is None:
                return
            self._finish_load(path, signal, sample_rate)
            return

        if suffix == '.wav':
            loader = self._load_wav
        elif suffix == '.mp3':
            loader = self._load_mp3
        else:
            QMessageBox.warning(self, "Unsupported format", f"Cannot load '{suffix}' files.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Loading")
        dialog.setModal(True)
        dialog.setFixedWidth(400)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Loading file, please wait..."))
        bar = QProgressBar()
        bar.setRange(0, 0)
        layout.addWidget(bar)
        dialog.show()

        self._pending_load_path = path
        self._load_dialog = dialog

        thread = QThread()
        worker = FileLoadWorker(loader, path)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self._on_file_loaded, Qt.ConnectionType.QueuedConnection)
        worker.error.connect(self._on_file_load_error, Qt.ConnectionType.QueuedConnection)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self._load_thread = thread
        self._load_worker = worker
        thread.start()

    def _on_file_loaded(self, result):
        full_signal, full_rate, display_signal, display_rate = result
        self._finish_load(self._pending_load_path, display_signal, display_rate, full_signal, full_rate)
        self._load_dialog.close()
        self._load_thread.quit()

    def _on_file_load_error(self, msg):
        self._load_dialog.close()
        QMessageBox.critical(self, "Load error", msg)
        self._load_thread.quit()

    def _finish_load(self, path, signal, sample_rate, full_signal=None, full_rate=None):
        n = len(signal)
        time = np.arange(n) / sample_rate

        fo = Filters()
        fo._raw = signal.astype(float)
        fo._filtered = fo._raw.copy()
        fo._time = time
        fo._applied_filters = []
        fo._raw_full = (full_signal if full_signal is not None else signal).astype(float)
        fo._rate_full = int(full_rate if full_rate is not None else sample_rate)
        self.filter_obj = fo

        duration = n / sample_rate
        self.file_label.setText(Path(path).name)
        self.info_label.setText(
            f"Sample Rate: {sample_rate} Hz  |  Samples: {n}  |  Duration: {duration:.3f} s"
        )

        self._clear_plots()
        self._init_playback_lines()
        self._refresh()
        self.play_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def _generate_test_signal(self):
        """
        Generate a randomised synthetic signal.
        Picks 2 to 4 components with randomly chosen wave shapes
        (sine, square, sawtooth, triangle), frequencies, amplitudes,
        adds gaussian noise, normalised to -1, 1.
        """
        from scipy.signal import square, sawtooth

        sample_rate = 8_000
        duration = 3.0
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        rng = np.random.default_rng()

        wave_builders = {
            'sine':     lambda f: np.sin(2 * np.pi * f * t),
            'square':   lambda f: square(2 * np.pi * f * t),
            'sawtooth': lambda f: sawtooth(2 * np.pi * f * t),
            'triangle': lambda f: sawtooth(2 * np.pi * f * t, width=0.5),
        }

        n_components = int(rng.integers(2, 5))
        wave_types = rng.choice(list(wave_builders.keys()), size=n_components, replace=True)
        freqs = rng.integers(50, 3_500, size=n_components)
        amps = rng.uniform(0.2, 0.8, size=n_components)
        amps = amps / amps.sum()  # sum to ~1 before noise

        signal = sum(
            amps[i] * wave_builders[wave_types[i]](freqs[i])
            for i in range(n_components)
        )
        signal += rng.normal(0, rng.uniform(0.05, 0.15), len(t))
        signal = signal / np.max(np.abs(signal))

        fo = Filters()
        fo._raw = signal
        fo._filtered = signal.copy()
        fo._time = t
        fo._applied_filters = []
        fo._raw_full = signal.copy()
        fo._rate_full = sample_rate
        self.filter_obj = fo

        components_str = '  +  '.join(
            f"{wave_types[i]} {freqs[i]} Hz" for i in range(n_components)
        )
        self.file_label.setText("Test Signal (generated)")
        self.info_label.setText(
            f"Sample Rate: {sample_rate} Hz  |  Samples: {len(t)}  |  Duration: {duration:.1f} s"
            f"  |  {components_str}  +  noise"
        )
        self._clear_plots()
        self._init_playback_lines()
        self._refresh()
        self.play_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def _load_wav(self, path):
        with wave.open(path, 'rb') as wf:
            sample_rate = wf.getframerate()
            num_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            num_frames = wf.getnframes()
            raw = wf.readframes(num_frames)

        if sample_width == 1:
            data = np.frombuffer(raw, dtype=np.uint8)
            signal = (data.astype(float) - 128.0) / 128.0
        elif sample_width == 2:
            data = np.frombuffer(raw, dtype=np.int16)
            signal = data.astype(float) / 32768.0
        elif sample_width == 3:
            data = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3 * num_channels)
            # pad 3-byte samples to int32
            padded = np.zeros((len(data), num_channels), dtype=np.int32)
            for ch in range(num_channels):
                for i in range(len(data)):
                    b = data[i, ch * 3: ch * 3 + 3]
                    val = int.from_bytes(b, 'little', signed=True)
                    padded[i, ch] = val
            signal = padded[:, 0].astype(float) / 8388608.0
            signal = signal / np.max(np.abs(signal))
            return signal, sample_rate
        elif sample_width == 4:
            data = np.frombuffer(raw, dtype=np.int32)
            signal = data.astype(float) / 2147483648.0
        else:
            raise ValueError(f"Unsupported sample width: {sample_width}")

        if num_channels > 1:
            data_reshaped = signal.reshape(-1, num_channels)
            signal = data_reshaped[:, 0]

        signal = signal / np.max(np.abs(signal))
        return signal, sample_rate

    def _load_mp3(self, path):
        signal, sample_rate = librosa.load(path, sr=None, mono=True)
        signal = signal / np.max(np.abs(signal))
        return signal.astype(float), int(sample_rate)

    def _load_spreadsheet(self, path, suffix):
        if suffix == '.csv':
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)

        if df.empty or len(df.columns) == 0:
            raise ValueError("The spreadsheet is empty.")

        cols = list(df.columns)
        if len(cols) == 1:
            col = cols[0]
        else:
            dlg = ColumnPickerDialog(cols, self)
            if dlg.exec() != QDialog.Accepted:
                return None, None
            col = dlg.selected_column()

        signal = df[col].dropna().to_numpy(dtype=float)

        sr, ok = QInputDialog.getDouble(
            self, "Sample Rate",
            "Enter the sample rate (Hz):", 1000.0, 0.001, 10_000_000.0, 3
        )
        if not ok:
            return None, None

        return signal, sr

    def _init_playback_lines(self):
        if self.filter_obj is None:
            return
        t_max = float(self.filter_obj._time[-1]) if len(self.filter_obj._time) > 0 else 1.0
        self._start_line = PlaybackLine(
            pos=0.0, angle=90, movable=True,
            pen=pg.mkPen(color=(0, 180, 80), width=2, style=Qt.DashLine),
            hoverPen=pg.mkPen(color=(255, 255, 255), width=3),
            label='▶ {value:.2f}s',
        )
        self._start_line.label.fill = pg.mkBrush(20, 20, 20)
        self._start_line.label.color = pg.mkBrush(0, 180, 80)
        self._start_line.label.orthoPos = 0.96
        self._start_line.doubleClicked.connect(lambda: self._start_line.setValue(0.0))
        self._start_line.sigPositionChanged.connect(self._clamp_playback_start)

        self._stop_line = PlaybackLine(
            pos=t_max, angle=90, movable=True,
            pen=pg.mkPen(color=(200, 0, 0), width=2, style=Qt.DashLine),
            hoverPen=pg.mkPen(color=(255, 255, 255), width=3),
            label='■ {value:.2f}s',
        )
        self._stop_line.label.fill = pg.mkBrush(20, 20, 20)
        self._stop_line.label.color = pg.mkBrush(200, 0, 0)
        self._stop_line.label.orthoPos = 0.96
        self._stop_line.doubleClicked.connect(
            lambda: self._stop_line.setValue(float(self.filter_obj._time[-1]))
        )
        self._stop_line.sigPositionChanged.connect(self._clamp_playback_stop)

        self._playback_line = PlaybackLine(
            pos=0.0, angle=90, movable=True,
            pen=pg.mkPen(color=(255, 255, 255), width=1),
            hoverPen=pg.mkPen(color=(255, 255, 0), width=2),
            label='⏵ {value:.2f}s',
        )
        self._playback_line.label.fill = pg.mkBrush(20, 20, 20)
        self._playback_line.label.color = pg.mkBrush(255, 255, 255)
        self._playback_line.label.orthoPos = 0.96
        self._playback_line.setVisible(False)
        self._playback_line.doubleClicked.connect(lambda: self._playback_line.setValue(self._start_line.value()) if self._start_line else None)
        self._playback_line.sigPositionChanged.connect(self._on_playback_line_dragged)

        self.signal_plot.addItem(self._start_line)
        self.signal_plot.addItem(self._stop_line)
        self.signal_plot.addItem(self._playback_line)

    def _clamp_playback_start(self):
        if self._start_line is None or self._stop_line is None:
            return
        v = self._start_line.value()
        clamped = max(0.0, min(v, self._stop_line.value() - 0.001))
        if clamped != v:
            self._start_line.setValue(clamped)

    def _clamp_playback_stop(self):
        if self._start_line is None or self._stop_line is None or self.filter_obj is None:
            return
        t_max = float(self.filter_obj._time[-1])
        v = self._stop_line.value()
        clamped = min(t_max, max(v, self._start_line.value() + 0.001))
        if clamped != v:
            self._stop_line.setValue(clamped)

    def _clear_plots(self):
        self.fft_plot.clear()
        self.signal_plot.clear()
        self.fft_legend = self.fft_plot.addLegend(offset=(-10, 10))
        self.signal_legend = self.signal_plot.addLegend(offset=(-10, -10))
        self.raw_line = None
        self.filter_line = None
        self.fft_line = None
        self._start_line = None
        self._stop_line = None
        self._playback_line = None
        self.preview_check.setChecked(False)
        for attr in ('low_f_line', 'high_f_line'):
            if hasattr(self, attr):
                delattr(self, attr)

    def _refresh(self):
        self._populate_filter_list()
        self._apply_all_filters()
        self._replot()
        self._populate_legend()

    def _apply_all_filters(self):
        if self.filter_obj is None:
            return
        self.filter_obj._filtered = self.filter_obj._raw.copy()
        for f_type, f_args in self.filter_obj._applied_filters:
            self._apply_filter(filter_type=f_type, apply=False, stack=True, _args=f_args)

        self._apply_fft()

    def _apply_fft(self, _args=None):
        if self.filter_obj is None:
            return None, None

        if _args is None:
            _args = [
                self.window_check_fft.isChecked(),
                self.low_peak_freq_spin.value(),
                self.high_peak_freq_spin.value(),
                self.min_peak_amp_spin.value(),
                self.kalman_check.isChecked(),
                self.kalman_noise_spin.value(),
            ]

        fft_df = self.filter_obj.apply_fft(
            window=_args[0] if isinstance(_args, (list, tuple)) else self.window_check_fft.isChecked(),
            normalise=self.normalize_check.isChecked(),
            fft_mode=self.fft_mode_combo.currentText(),
        )

        if 'FFT Raw Frequency' not in fft_df.columns:
            return None, None

        freq = fft_df['FFT Raw Frequency'].to_numpy()
        amp = fft_df['FFT Raw Amplitude'].to_numpy()

        if self.fft_line is None:
            colors = self._config_manager.get_line_colors()
            self.fft_line = self.fft_plot.plot(
                freq, amp,
                pen=pg.mkPen(color=colors['fft'], width=2), name="FFT"
            )
            self.fft_line.setDownsampling(auto=True, method='peak')
            self.fft_line.setClipToView(True)
        else:
            self.fft_line.setData(x=freq, y=amp)

        try:
            ifft_filter, low_f, high_f, high_freq_range_start, kalman_args = \
                self.filter_obj.find_raw_peaks(_args)
        except Exception as e:
            print(f"Peak detection error: {e}")
            return None, None

        self._draw_peak_lines(low_f, high_f, high_freq_range_start)
        return ifft_filter, kalman_args

    def _apply_fft_handler(self):
        self._apply_fft([
            self.window_check_fft.isChecked(),
            self.low_peak_freq_spin.value(),
            self.high_peak_freq_spin.value(),
            self.min_peak_amp_spin.value(),
            self.kalman_check.isChecked(),
            self.kalman_noise_spin.value(),
        ])

    def _draw_peak_lines(self, low_f, high_f, high_freq_range_start):
        if low_f is not None:
            if not hasattr(self, 'low_f_line'):
                self.low_f_line = pg.InfiniteLine(
                    pos=low_f, angle=90,
                    pen=pg.mkPen(color='w', width=2, style=Qt.DashLine),
                    movable=False, label=f"Low Frequency Start: {low_f} Hz"
                )
                self.low_f_line.label.fill = pg.mkBrush(20, 20, 20)
                self.low_f_line.label.color = pg.mkBrush(255, 255, 255)
                self.low_f_line.label.orthoPos = 0.9
                self.fft_plot.addItem(self.low_f_line)
            else:
                self.low_f_line.setVisible(True)
                self.low_f_line.setPos(low_f)
                self.low_f_line.label.setText(f"Low Frequency Start: {low_f} Hz")
        else:
            if hasattr(self, 'low_f_line'):
                self.low_f_line.setVisible(False)

        if high_f is not None and high_freq_range_start is not None:
            if not hasattr(self, 'high_f_line'):
                self.high_f_line = pg.InfiniteLine(
                    pos=high_freq_range_start, angle=90,
                    pen=pg.mkPen(color='w', width=2, style=Qt.DashLine),
                    movable=False, label=f"High Frequency Start: {high_f} kHz"
                )
                self.high_f_line.label.fill = pg.mkBrush(20, 20, 20)
                self.high_f_line.label.color = pg.mkBrush(255, 255, 255)
                self.high_f_line.label.orthoPos = 0.75
                self.fft_plot.addItem(self.high_f_line)
            else:
                self.high_f_line.setVisible(True)
                self.high_f_line.setPos(high_freq_range_start)
                self.high_f_line.label.setText(f"High Frequency Start: {high_f} kHz")
        else:
            if hasattr(self, 'high_f_line'):
                self.high_f_line.setVisible(False)

        self.fft_plot.update()

    def _get_sample_rate(self):
        t = self.filter_obj._time
        return 1.0 / (t[1] - t[0]) if len(t) > 1 else 1.0

    def _get_filter_params(self):
        return (
            self.window_check_filter.isChecked(),
            self.filter_low_spin.value(),
            self.filter_high_spin.value(),
            self.filter_order_spin.value(),
            {
                "Butterworth": "butter",
                "Chebyshev I": "cheby1",
                "Chebyshev II": "cheby2",
                "Elliptic": "ellip",
                "Bessel": "bessel",
            }.get(self.filter_design_combo.currentText(), "butter"),
            self.ripple_spin.value(),
            self.attenuation_spin.value(),
        )

    def _apply_filter(self, filter_type: str, apply=False, stack=False, _args=None):
        if self.filter_obj is None:
            return

        sample_rate = self._get_sample_rate()

        if stack:
            _signal = self.filter_obj._filtered
        else:
            _signal = self.filter_obj._raw

        signal_series = pd.Series(_signal)

        if filter_type == "IFFT / Kalman Filter":
            ifft_args = _args if _args is not None else [
                self.window_check_fft.isChecked(),
                self.low_peak_freq_spin.value(),
                self.high_peak_freq_spin.value(),
                self.min_peak_amp_spin.value(),
                self.kalman_check.isChecked(),
                self.kalman_noise_spin.value(),
            ]
            result, kalman_args = self._apply_fft(_args=ifft_args)
            if result is None:
                return

            if self.window_check_filter.isChecked():
                win = np.hanning(len(result))
                result = result * win

            result = self.filter_obj.normalise_custom(result)
            self.filter_obj._filtered = result

            if apply:
                self.filter_obj._applied_filters.append((filter_type, kalman_args))
            return

        if _args is not None:
            low_freq, high_freq, order, window_arg = _args[0], _args[1], _args[2], _args[3]
            filter_design = _args[4] if len(_args) > 4 else 'butter'
            ripple = _args[5] if len(_args) > 5 else 3.0
            attenuation = _args[6] if len(_args) > 6 else 60.0
        else:
            window_arg, low_freq, high_freq, order, filter_design, ripple, attenuation = self._get_filter_params()

        result = Filters.apply_standard_filter(
            signal_series, sample_rate, filter_type, low_freq, high_freq, int(order),
            filter_design, ripple, attenuation,
        )
        if result is None:
            return

        if window_arg:
            win = np.hanning(len(result))
            result = result * win

        result = self.filter_obj.normalise_custom(result)
        self.filter_obj._filtered = pd.Series(result)

        if apply:
            self.filter_obj._applied_filters.append(
                (filter_type, [round(low_freq, 1), round(high_freq, 1), order, window_arg,
                               filter_design, round(ripple, 1), round(attenuation, 1)])
            )

    def _apply_filter_preview(self):
        if self.filter_obj is None:
            return
        self.filter_obj._filtered = self.filter_obj._raw.copy()
        for f_type, f_args in self.filter_obj._applied_filters:
            self._apply_filter(filter_type=f_type, apply=False, stack=True, _args=f_args)
        self._apply_filter(filter_type=self.filter_combo.currentText(), apply=False, stack=True)
        self._replot()
        self._populate_legend()

    def _keep_playback_position(self):
        pos = self._playback_line.value() if self._playback_line and self._playback_line.isVisible() else None
        self._stop_audio()
        if pos and self._playback_line:
            self._playback_line.setValue(pos)
            self._playback_line.setVisible(True)
            self._paused_position = pos

    def _apply_filter_committed(self):
        if self.filter_obj is None:
            return
        self._keep_playback_position()
        filter_type = self.filter_combo.currentText()

        if filter_type == "IFFT / Kalman Filter":
            self._apply_filter(filter_type=filter_type, apply=True, stack=False)
            self.preview_check.setChecked(False)
            self._refresh()
            return

        sample_rate = self._get_sample_rate()
        signal = np.asarray(self.filter_obj._raw, dtype=float)
        window_arg, low_freq, high_freq, order, filter_design, ripple, attenuation = self._get_filter_params()

        self.apply_filter_button.setEnabled(False)
        self.apply_filter_button.setText("Applying...")

        thread = QThread()
        worker = FilterWorker(signal, sample_rate, filter_type,
                              low_freq, high_freq, order,
                              filter_design, ripple, attenuation, window_arg)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)  # stop thread event loop on finish
        worker.finished.connect(self._on_filter_done, Qt.ConnectionType.QueuedConnection)
        worker.error.connect(self._on_filter_error, Qt.ConnectionType.QueuedConnection)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self._filter_thread = thread
        self._filter_worker = worker
        thread.start()

    def _on_filter_done(self, payload):
        result, filter_type, low_freq, high_freq, order, window_arg, filter_design, ripple, attenuation = payload
        if self._filter_thread is not None:
            self._filter_thread.quit()
            self._filter_thread.wait()  # block until thread stops before dropping references
            self._filter_thread = None
            self._filter_worker = None
        if result is not None:
            if window_arg:
                win = np.hanning(len(result))
                result = result * win
            result = self.filter_obj.normalise_custom(result)
            self.filter_obj._applied_filters.append(
                (filter_type, [round(low_freq, 1), round(high_freq, 1), order, window_arg,
                               filter_design, round(ripple, 1), round(attenuation, 1)])
            )
            self.preview_check.blockSignals(True)
            self.preview_check.setChecked(False)
            self.preview_check.blockSignals(False)
            self._refresh()
        self.apply_filter_button.setEnabled(True)
        self.apply_filter_button.setText("Apply Filter")

    def _on_filter_error(self, msg):
        if self._filter_thread is not None:
            self._filter_thread.quit()
            self._filter_thread.wait()
            self._filter_thread = None
            self._filter_worker = None
        self.apply_filter_button.setEnabled(True)
        self.apply_filter_button.setText("Apply Filter")
        QMessageBox.critical(self, "Filter error", msg)

    def _clear_filters(self):
        if self.filter_obj is None:
            return
        self._keep_playback_position()
        self.filter_obj._applied_filters = []
        self.filter_obj._filtered = self.filter_obj._raw.copy()
        self.preview_check.setChecked(False)
        self._refresh()

    def _toggle_playback(self):
        if self._is_playing:
            self._pause_audio()
        else:
            self._play_audio()

    def _play_audio(self):
        if self.filter_obj is None:
            return
        signal = np.asarray(self.filter_obj._raw_full, dtype=float)
        sample_rate = self.filter_obj._rate_full
        for f_type, f_args in self.filter_obj._applied_filters:
            low_freq, high_freq, order = f_args[0], f_args[1], int(f_args[2])
            filter_design = f_args[4] if len(f_args) > 4 else 'butter'
            ripple = f_args[5] if len(f_args) > 5 else 3.0
            attenuation = f_args[6] if len(f_args) > 6 else 60.0
            result = Filters.apply_standard_filter(
                signal, sample_rate, f_type, low_freq, high_freq, order,
                filter_design, ripple, attenuation)
            if result is not None:
                signal = result
        signal = np.asarray(signal, dtype=np.float32)

        t_region_start = 0.0
        t_region_stop = len(signal) / sample_rate
        if self._start_line and self._stop_line:
            t_region_start = min(self._start_line.value(), self._stop_line.value())
            t_region_stop = max(self._start_line.value(), self._stop_line.value())

        resume_offset = 0.0
        if self._paused_position is not None:
            resume_offset = self._paused_position - t_region_start
            self._paused_position = None

        i_start = max(0, int(t_region_start * sample_rate))
        i_stop = min(len(signal), int(t_region_stop * sample_rate))
        if i_start >= i_stop:
            return
        signal = signal[i_start:i_stop]

        max_val = np.max(np.abs(signal))
        if max_val > 0:
            signal = signal / max_val
        valid_rates = {8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000}
        if sample_rate not in valid_rates:
            signal = librosa.resample(signal, orig_sr=sample_rate, target_sr=22050)
            sample_rate = 22050

        if resume_offset > 0:
            resume_samples = int(resume_offset * sample_rate)
            signal = np.roll(signal, -resume_samples)

        sd.play(signal, sample_rate, loop=True)

        self._playback_start_wall = _time.monotonic() - resume_offset
        self._playback_t_offset = t_region_start
        self._playback_t_stop = t_region_stop
        self._playback_duration = t_region_stop - t_region_start
        self._is_playing = True

        if self._playback_line:
            self._updating_playback_pos = True
            self._playback_line.setValue(t_region_start + resume_offset)
            self._updating_playback_pos = False
            self._playback_line.setVisible(True)

        self.play_button.setIcon(self._icon_pause)
        self.play_button.setText(" Pause")
        self.stop_button.setEnabled(True)

        self._playback_timer = QTimer(self)
        self._playback_timer.timeout.connect(self._check_playback)
        self._playback_timer.start(50)

    def _pause_audio(self):
        elapsed = _time.monotonic() - self._playback_start_wall
        if self._playback_duration > 0:
            looped = elapsed % self._playback_duration
        else:
            looped = 0.0
        self._paused_position = self._playback_t_offset + looped
        sd.stop()
        if hasattr(self, '_playback_timer'):
            self._playback_timer.stop()
        self._is_playing = False
        self.play_button.setIcon(self._icon_play)
        self.play_button.setText("Play")

    def _check_playback(self):
        try:
            active = sd.get_stream().active
        except (AttributeError, RuntimeError):
            active = False

        if active:
            elapsed = _time.monotonic() - self._playback_start_wall
            if self._playback_duration > 0:
                looped = elapsed % self._playback_duration
            else:
                looped = 0.0
            current_t = self._playback_t_offset + looped
            if self._playback_line:
                self._updating_playback_pos = True
                self._playback_line.setValue(current_t)
                self._updating_playback_pos = False
        else:
            self._playback_timer.stop()
            self._is_playing = False
            self._paused_position = None
            self.play_button.setIcon(self._icon_play)
            self.play_button.setText("Play")
            self.stop_button.setEnabled(False)
            if self._playback_line:
                self._playback_line.setVisible(False)

    def _stop_audio(self):
        sd.stop()
        if hasattr(self, '_playback_timer'):
            self._playback_timer.stop()
        self._is_playing = False
        self._paused_position = None
        self.play_button.setIcon(self._icon_play)
        self.play_button.setText("Play")
        self.play_button.setEnabled(self.filter_obj is not None)
        self.stop_button.setEnabled(False)
        if self._playback_line:
            self._playback_line.setVisible(False)

    def _on_playback_line_dragged(self):
        if self._updating_playback_pos:
            return
        if not self._playback_line or not self._start_line or not self._stop_line:
            return
        t_lo = self._start_line.value()
        t_hi = self._stop_line.value()
        v = self._playback_line.value()
        clamped = max(t_lo, min(v, t_hi))
        if clamped != v:
            self._playback_line.setValue(clamped)
            return
        if self._is_playing:
            sd.stop()
            if hasattr(self, '_playback_timer'):
                self._playback_timer.stop()
            self._is_playing = False
            self._paused_position = clamped
            self._play_audio()
        elif self._paused_position:
            self._paused_position = clamped

    def _populate_filter_list(self):
        self.filter_tree.clear()
        if self.filter_obj is None:
            return
        for f_type, f_args in self.filter_obj._applied_filters:
            item = QTreeWidgetItem([str(f_type), str(f_args)])
            self.filter_tree.addTopLevelItem(item)

    def _open_line_colors_dialog(self):
        original = self._config_manager.get_line_colors()
        dlg = LineColorsDialog(original, self)
        dlg.colorsChanged.connect(self._apply_line_colors)
        if dlg.exec() == LineColorsDialog.Accepted:
            self._config_manager.set_line_colors(dlg.get_colors())
        else:
            self._apply_line_colors(original)

    def _apply_line_colors(self, colors: dict):
        if self.raw_line is not None:
            self.raw_line.setPen(pg.mkPen(color=colors['raw'], width=2))
        if self.filter_line is not None:
            self.filter_line.setPen(pg.mkPen(color=colors['filtered'], width=2))
        if self.fft_line is not None:
            self.fft_line.setPen(pg.mkPen(color=colors['fft'], width=2))

    def _reset_plot_lines(self):
        if self.raw_line is not None:
            self.signal_plot.removeItem(self.raw_line)
            self.raw_line = None
        if self.filter_line is not None:
            self.signal_plot.removeItem(self.filter_line)
            self.filter_line = None
        if self.fft_line is not None:
            self.fft_plot.removeItem(self.fft_line)
            self.fft_line = None
        self._replot()
        self._apply_fft()

    def _replot(self):
        if self.filter_obj is None:
            return
        time = self.filter_obj._time
        raw = np.asarray(self.filter_obj._raw)
        filtered = np.asarray(self.filter_obj._filtered)

        if self.raw_line is None:
            colors = self._config_manager.get_line_colors()
            self.raw_line = self.signal_plot.plot(
                time, raw,
                pen=pg.mkPen(color=colors['raw'], width=2), name="Raw"
            )
            self.filter_line = self.signal_plot.plot(
                time, filtered,
                pen=pg.mkPen(color=colors['filtered'], width=2), name="Filtered"
            )
            for line in (self.raw_line, self.filter_line):
                line.setDownsampling(auto=True, method='peak')
                line.setClipToView(True)
            self.signal_plot.setYRange(-1.4, 1.4)
        else:
            self.raw_line.setData(x=time, y=raw)
            if len(filtered) == len(time):
                self.filter_line.setData(x=time, y=filtered)

        self._handle_plot_visible('raw')
        self._handle_plot_visible('filtered')

    def _handle_filters_visible(self, state, signal: str):
        if signal == 'raw':
            self._raw_filter_visible = state
        elif signal == 'filtered':
            self._filtered_filter_visible = state
        self._handle_plot_visible(signal)

    def _handle_plot_visible(self, signal: str):
        for item in self.signal_plot.listDataItems():
            if hasattr(item, 'name') and item.name():
                if item.name() == 'Raw' and signal == 'raw':
                    item.setVisible(self._raw_filter_visible)
                elif item.name() == 'Filtered' and signal == 'filtered':
                    item.setVisible(self._filtered_filter_visible)
        self._populate_legend()

    def _populate_legend(self):
        if self.signal_legend:
            self.signal_legend.clear()
        if self.fft_legend:
            self.fft_legend.clear()

        for item in self.signal_plot.listDataItems():
            if item.isVisible() and hasattr(item, 'name') and item.name():
                self.signal_legend.addItem(item, item.name())

        for item in self.fft_plot.listDataItems():
            if item.isVisible() and hasattr(item, 'name') and item.name():
                self.fft_legend.addItem(item, item.name())


def main():
    pg.setConfigOptions(antialias=False)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
