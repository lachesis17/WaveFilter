# WaveFilter

A desktop signal processing application with PySide6. Load audio or data files, visualise the raw and filtered waveforms alongside their FFT spectra and apply one or more filters in sequence with real-time previews.

## Features

- Load WAV, MP3, CSV, and Excel files
- Generate synthetic test signals (sine, square, sawtooth, triangle + noise)
- Interactive time-domain and FFT plots
- Real-time filter preview before applying
- Stack and clear multiple filters

## Filter Types

| Filter         | Notes                                                                              |
| -------------- | ---------------------------------------------------------------------------------- |
| Low Pass       | Attenuates frequencies above the cutoff                                            |
| High Pass      | Attenuates frequencies below the cutoff                                            |
| Band Pass      | Passes a frequency band, attenuates outside                                        |
| Band Stop      | Attenuates a frequency band, passes outside                                        |
| Notch          | Narrow band rejection at a single frequency                                        |
| Savitzky-Golay | Polynomial smoothing filter                                                        |
| IFFT / Kalman  | Peak-based frequency isolation via inverse FFT, with optional Kalman pre-smoothing |

### Filter Designs (IIR filters)

Butterworth, Chebyshev I, Chebyshev II, Elliptic, Bessel

## FFT Modes

FFT, IFFT, RFFT, IRFFT, HFFT, IHFFT, DCT, IDCT, DST, IDST

---

### Install dependencies

```
pip install -r requirements.txt
```

### Compile UI after editing `ui/wavefilter.ui`

```powershell
pyside6-uic ui/wavefilter.ui | Out-File -FilePath ui/wavefilter_ui.py
```

---

## Compiling to .exe

Uses [auto-py-to-exe](https://github.com/brentvollebregt/auto-py-to-exe) with the config in `compile/`.

### batch script (recommended)

Run `compile/compile.bat` from anywhere. It changes dir to the project root before launching auto-py-to-exe, using the `wavefilter-autopytoexe.json` as a saved config with relative paths.

### manual

Run from the **project root directory** so relative paths in the config resolve correctly:

```
auto-py-to-exe --config compile/wavefilter-autopytoexe.json
```

## Releases

Just download the `*.7z` zip from (here), extract then run `WaveFilter.exe`. You could add a shortcut to it!
