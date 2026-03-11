# <img src="https://github.com/user-attachments/assets/00df788b-5ce5-4b66-8863-53c74a2e9ec7" height="30"> WaveFilter

A desktop signal processing application with PySide6. Load audio or data files, visualise the raw and filtered waveforms alongside their FFT spectra and apply one or more filters in sequence with real-time previews and playback. Supports saving and loading of sessions and export to audio or excel files. Along with filters, pitch shifting and reverse can be applied to create exportable looping samples.

![wavefilter](https://github.com/user-attachments/assets/2eb40dfb-c6f3-48df-bf79-c9797bbcd0d9)

---

## Features

- Load WAV, MP3, CSV, and Excel files
- Real-time filter preview before applying
- Playback audio with start/stop times and filters applied
- Looping playback with draggable playback head
- Stack and clear multiple filters (individual or multi-select)
- Pitch shift and reverse as additional filter types
- Trim signal to start/stop selection
- Save and load sessions (`.wavefilter` format)
- Export filtered audio to `mp3`, `wav` and `excel`
- Interactive time-domain and FFT plots
- Generate synthetic test signals (sine, square, sawtooth, triangle + noise)
- Optional hanning window
- Custom colors for plotted lines

---

## Filter Types

| Filter         | Parameters                                   | Notes                                                |
| -------------- | -------------------------------------------- | ---------------------------------------------------- |
| Low Pass       | Low Frequency, Order, Design                 | Attenuates frequencies above the cutoff              |
| High Pass      | High Frequency, Order, Design                | Attenuates frequencies below the cutoff              |
| Band Pass      | Low Frequency, High Frequency, Order, Design | Passes a frequency band, attenuates outside          |
| Band Stop      | Low Frequency, High Frequency, Order, Design | Attenuates a frequency band, passes outside          |
| Notch          | Low Frequency                                | Narrow band rejection at a single frequency          |
| Savitzky-Golay | Window Length, Poly Order                    | Polynomial smoothing filter                          |
| Pitch Shift    | Semitones (-36 to +36)                       | Shifts pitch without changing duration (via librosa) |
| Reverse        |                                              | Reverses the signal                                  |

## Filter Designs (IIR filters)

| Design       | Parameters                | Notes                                             |
| ------------ | ------------------------- | ------------------------------------------------- |
| Butterworth  |                           | Maximally flat passband, no ripple                |
| Chebyshev I  | Passband ripple (dB)      | Steeper rolloff, ripple in passband               |
| Chebyshev II | Stopband attenuation (dB) | Steeper rolloff, ripple in stopband               |
| Elliptic     | Ripple + Attenuation (dB) | Steepest rolloff, ripple in both bands            |
| Bessel       |                           | Maximally flat group delay, linear phase response |

## FFT Modes

| Mode | Description               |
| ---- | ------------------------- |
| FFT  | Fast Fourier Transform    |
| DCT  | Discrete cosine transform |
| DST  | Discrete sine transform   |

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

_Playback support demo with filters applied: low-pass, high-pass, band-pass, band-stop_
