import numpy as np
import pandas as pd
import scipy.fft as fft
from scipy.signal import filtfilt, find_peaks, iirfilter, iirnotch, savgol_filter, sosfiltfilt


class Filters:
    def __init__(self) -> None:
        self._raw: np.ndarray
        self._filtered: np.ndarray
        self._time: np.ndarray
        self._df = pd.DataFrame()
        self._applied_filters: list = []

    def normalise_custom(self, arr) -> np.ndarray:
        arr = arr - np.mean(arr)
        max_val = np.max(np.abs(arr))
        if max_val == 0:
            return arr
        return arr / max_val

    def apply_fft(self, window=False, normalise=False, fft_mode='') -> pd.DataFrame:
        signal = self._raw.copy()
        time_span = np.max(self._time) - np.min(self._time)
        num_samples = len(signal)
        sample_rate = num_samples / time_span

        if window:
            win = np.hanning(num_samples)
            signal = signal * win

        if fft_mode == "DCT - Discrete cosine transform":
            fft_amp = fft.dct(signal, overwrite_x=False)
        elif fft_mode == "DST - Discrete sine transform":
            fft_amp = fft.dst(signal, overwrite_x=False)
        else:
            fft_amp = fft.fft(signal, overwrite_x=False)

        freq = np.fft.fftfreq(num_samples, 1 / sample_rate)
        positive = np.where(freq >= 0)
        freq = freq[positive]
        amp = np.abs(fft_amp)[positive]

        if 'FFT Raw Frequency' in self._df.columns:
            self._df.drop(columns=['FFT Raw Frequency', 'FFT Raw Amplitude'], inplace=True)

        df = pd.DataFrame({'FFT Raw Frequency': freq, 'FFT Raw Amplitude': amp})
        if normalise:
            max_val = np.max(np.abs(df['FFT Raw Amplitude']))
            if max_val > 0:
                df['FFT Raw Amplitude'] = df['FFT Raw Amplitude'] / max_val
        df['FFT Raw Frequency'] = df['FFT Raw Frequency'].astype(float)
        self._df = pd.concat([self._df, df], axis=1)

        return self._df

    def apply_forward_fft(self, signal, time, window):
        time_span = np.max(time) - np.min(time)
        num_samples = len(signal)
        sample_rate = num_samples / time_span

        if window:
            win = np.hanning(num_samples)
            signal = signal * win

        fft_amp = fft.fft(signal, overwrite_x=False)
        freq = np.fft.fftfreq(num_samples, 1 / sample_rate)
        positive = np.where(freq >= 0)
        freq = freq[positive]
        amp = np.abs(fft_amp)[positive]

        max_val = np.max(np.abs(amp))
        fft_amp_normalised = amp / max_val if max_val > 0 else amp

        return freq, fft_amp, fft_amp_normalised, sample_rate, num_samples

    def find_raw_peaks(self, window, low_thresh, high_thresh, amp_thresh):
        fft_freq, _, fft_amp_normalised, _, _ = self.apply_forward_fft(
            signal=self._raw, time=self._time, window=window)
        peaks, _ = find_peaks(fft_amp_normalised, height=amp_thresh)
        peak_freqs = fft_freq[peaks]

        low_freq_peaks = peak_freqs[peak_freqs < low_thresh]
        high_freq_peaks = peak_freqs[peak_freqs > high_thresh]

        low_freq_range_start = low_freq_peaks[0] if low_freq_peaks.size > 0 else None
        high_freq_range_start = high_freq_peaks[0] if high_freq_peaks.size > 0 else None

        low_f = round(low_freq_range_start, 2) if low_freq_range_start is not None else None
        high_f = round(high_freq_range_start / 1000, 2) if high_freq_range_start is not None else None

        return low_f, high_f, high_freq_range_start

    @staticmethod
    def apply_standard_filter(signal_series, sample_rate, filter_type, low_freq, high_freq, order,
                               filter_design='butter', ripple=3.0, attenuation=60.0):
        """
        Apply a filter to signal_series. Returns filtered np.ndarray or None on error.
        types: "Low Pass Filter", "High Pass Filter", "Band Pass Filter", "Band Stop Filter", "Notch Filter", "Savitzky-Golay Filter"
        designs: 'butter', 'cheby1', 'cheby2', 'ellip', 'bessel'  (ignored for Notch/SG)
        ripple: passband ripple in dB (cheby1, ellip)
        attenuation: min stopband attenuation in dB (cheby2, ellip)
        Savitzky-Golay: low_freq = window_length (odd int), order = polyorder
        """
        data = np.asarray(signal_series, dtype=float)

        if filter_type == "Savitzky-Golay Filter":
            wl = max(int(low_freq), 3)
            if wl % 2 == 0:
                wl += 1
            poly = min(int(order), wl - 1)
            try:
                return savgol_filter(data, window_length=wl, polyorder=poly)
            except ValueError as e:
                print(f"Filter error: {e}")
                return None

        def _ripple_kwargs():
            if filter_design == 'cheby1':
                return {'rp': ripple}
            elif filter_design == 'cheby2':
                return {'rs': attenuation}
            elif filter_design == 'ellip':
                return {'rp': ripple, 'rs': attenuation}
            return {}

        def _filter(data, freq, ord_):
            try:
                if filter_type == "Notch Filter":
                    b, a = iirnotch(w0=freq, Q=10, fs=sample_rate)
                    return filtfilt(b, a, data)
                elif filter_type == "Band Pass Filter":
                    sos = iirfilter(ord_, Wn=freq, fs=sample_rate, btype='bandpass',
                                    ftype=filter_design, output='sos', **_ripple_kwargs())
                elif filter_type == "Band Stop Filter":
                    sos = iirfilter(ord_, Wn=freq, fs=sample_rate, btype='bandstop',
                                    ftype=filter_design, output='sos', **_ripple_kwargs())
                elif filter_type == "Low Pass Filter":
                    sos = iirfilter(ord_, Wn=freq, fs=sample_rate, btype='lowpass',
                                    ftype=filter_design, output='sos', **_ripple_kwargs())
                elif filter_type == "High Pass Filter":
                    sos = iirfilter(ord_, Wn=freq, fs=sample_rate, btype='highpass',
                                    ftype=filter_design, output='sos', **_ripple_kwargs())
                else:
                    return None
                return sosfiltfilt(sos, data)
            except ValueError as e:
                print(f"Filter error: {e}")
                return None

        if filter_type in ("Band Pass Filter", "Band Stop Filter"):
            freq = [low_freq, high_freq]
        elif filter_type in ("Low Pass Filter", "Notch Filter"):
            freq = low_freq
        else:
            freq = high_freq

        return _filter(data, freq, order)
