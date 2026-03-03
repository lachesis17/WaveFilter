# <img src="https://github.com/user-attachments/assets/d65cd88b-a1d4-43c9-b8f4-cbc5e2ac436b" height="28"> WaveFilter

A desktop signal processing application with PySide6. Load audio or data files, visualise the raw and filtered waveforms alongside their FFT spectra and apply one or more filters in sequence with real-time previews and playback.

![wavefilter](https://github.com/user-attachments/assets/fae6cdc3-1597-46fa-bb25-5a7f445315c1)

---

## Features

- Load WAV, MP3, CSV, and Excel files
- Generate synthetic test signals (sine, square, sawtooth, triangle + noise)
- Interactive time-domain and FFT plots
- Real-time filter preview before applying
- Stack and clear multiple filters
- Optional hanning window
- Playback audio with start/stop times and filters applied
- Custom colors for plotted lines

---

## Filter Types

| Filter         | Parameters                                         | Notes                                                                              |
| -------------- | -------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Low Pass       | Low Frequency, Order, Design                       | Attenuates frequencies above the cutoff                                            |
| High Pass      | High Frequency, Order, Design                      | Attenuates frequencies below the cutoff                                            |
| Band Pass      | Low Frequency, High Frequency, Order, Design       | Passes a frequency band, attenuates outside                                        |
| Band Stop      | Low Frequency, High Frequency, Order, Design       | Attenuates a frequency band, passes outside                                        |
| Notch          | Low Frequency                                      | Narrow band rejection at a single frequency                                        |
| Savitzky-Golay | Window Length, Poly Order                          | Polynomial smoothing filter                                                        |
| IFFT / Kalman  | Window, Low/High/Amplitude threshold, Kalman noise | Peak-based frequency isolation via inverse FFT, with optional Kalman pre-smoothing |

## Filter Designs (IIR filters)

| Design       | Parameters                | Notes                                             |
| ------------ | ------------------------- | ------------------------------------------------- |
| Butterworth  |                           | Maximally flat passband, no ripple                |
| Chebyshev I  | Passband ripple (dB)      | Steeper rolloff, ripple in passband               |
| Chebyshev II | Stopband attenuation (dB) | Steeper rolloff, ripple in stopband               |
| Elliptic     | Ripple + Attenuation (dB) | Steepest rolloff, ripple in both bands            |
| Bessel       |                           | Maximally flat group delay, linear phase response |

## FFT Modes

| Mode  | Description                                 |
| ----- | ------------------------------------------- |
| FFT   | Fast Fourier Transform                      |
| IFFT  | Inverse FFT                                 |
| RFFT  | FFT of strictly real-valued sequence        |
| IRFFT | Inverse of RFFT                             |
| HFFT  | FFT of a Hermitian sequence (real spectrum) |
| IHFFT | Inverse of HFFT                             |
| DCT   | Discrete cosine transform                   |
| IDCT  | Inverse DCT                                 |
| DST   | Discrete sine transform                     |
| IDST  | Inverse DST                                 |

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

## Compiling

Both OS versions will compile to `/output` dir.

### Windows

Uses [auto-py-to-exe](https://github.com/brentvollebregt/auto-py-to-exe) with the config in `compile/`.

The batch file changes dir to the project root before launching auto-py-to-exe, using the `wavefilter-autopytoexe.json` as a saved config with relative paths.
```
./compile/compile.bat
```

Or manually from the project root dir:

```
auto-py-to-exe --config compile/wavefilter-autopytoexe.json
```

### macOS

The shell script replaces icon files for macOS, recompiles the ui as well as an inline temp python hook to handle relative paths when compiled on mac through pyinstaller.
```
./compile/compile_mac.sh
```

---

## Releases

Just download the `*.7z` zip from [releases](https://github.com/lachesis17/WaveFilter/releases) and extract then run `WaveFilter.exe`. You could add a shortcut to it!

---

https://github.com/user-attachments/assets/886a6ad0-9bb2-4962-a376-e0cd3b3d0077

*Playback support demo with filters applied: low-pass, high-pass, band-pass, band-stop*
