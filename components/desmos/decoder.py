import pyaudio
import numpy as np
from .commons import *


class DesmosDecoder:
    def __init__(self, callback):
        self.callback = callback
        self.CHUNK = 4096       # samples per frame
        self.RATE = 44100       # sample self.RATE (Hz)

    def _get_frequency(self, data):
        # Apply Hanning window to reduce spectral leakage
        window = np.hanning(len(data))
        windowed = data * window

        # FFT
        fft = np.abs(np.fft.rfft(windowed))
        freqs = np.fft.rfftfreq(len(data), 1.0 / self.RATE)

        # Only look at human hearing range 80Hz–2000Hz
        min_idx = np.searchsorted(freqs, 80)
        max_idx = np.searchsorted(freqs, 2000)
        fft_range = fft[min_idx:max_idx]
        freqs_range = freqs[min_idx:max_idx]

        # Find peak frequency
        peak_idx = np.argmax(fft_range)
        peak_freq = freqs_range[peak_idx]
        amplitude = fft_range[peak_idx]

        return peak_freq, amplitude
    
    def decode(self, callback):
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )

        char_stream = ""
        reset_char = True
        started = False
        count = 0
        last_detected = ""

        try:
            while True:
                raw = stream.read(self.CHUNK, exception_on_overflow=False)
                data = np.frombuffer(raw, dtype=np.int16).astype(np.float32)

                freq, amplitude = self._get_frequency(data)
                break_outer = False

                # Only print if loud enough (not silence)
                if amplitude > 5000:
                    # convert frequency to the fucking chars
                    for char, range in char_to_freq_range.items():
                        if range[0] <= freq <= range[1]:
                            if char == last_detected:
                                count += 1
                            else:
                                last_detected = char
                                count = 1

                            if count < 5:
                                continue
                                
                            if char == "@":
                                started = True

                            if char == "!":
                                break_outer = True
                                break

                            if char == "|":
                                reset_char = True
                            elif reset_char and started:
                                if char != "@":
                                    char_stream += char
                                    reset_char = False

                            break
                    if not started:
                        print("Waiting...")
                    else:
                        print(char_stream, freq)
                else:
                    print(f"🔇 silence", end="\n", flush=True)
                
                if break_outer:
                    print("broken outer")
                    print(f"final message: {char_stream}")
                    self.callback(char_stream)
                    break

        except KeyboardInterrupt:
            print("\nStopped.")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()