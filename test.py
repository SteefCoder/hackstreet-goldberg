# from scripts.mail import Browser, Sender, Receiver
# from colorama import Fore


# def callback(received):
#     print(Fore.GREEN + received + Fore.RESET)


# with Browser() as gmail:
#     # sender = Sender(gmail, typing_delay=0)
#     # sender.send(recv="richardkevinson279@gmail.com", msg="Module poop")
#     receiver = Receiver(gmail)
#     receiver.receive(callback)


"""
Morse Code Live Audio Decoder
------------------------------
Listens to the microphone in real-time, detects morse code signals by
amplitude thresholding, classifies dots/dashes/gaps by timing, and prints
decoded text as each word is completed.

Dependencies:
    pip install pyaudio numpy

Usage:
    python morse_decoder.py
    python morse_decoder.py --threshold 3.5   # increase for noisy rooms
    python morse_decoder.py --dot 0.1         # manually set dot duration (s)
"""

import argparse
import time
import numpy as np
from collections import deque

# ── Morse code lookup ────────────────────────────────────────────────────────
MORSE_TABLE = {
    ".-": "A",   "-...": "B", "-.-.": "C", "-..": "D",  ".": "E",
    "..-.": "F", "--.": "G",  "....": "H", "..": "I",   ".---": "J",
    "-.-": "K",  ".-..": "L", "--": "M",   "-.": "N",   "---": "O",
    ".--.": "P", "--.-": "Q", ".-.": "R",  "...": "S",  "-": "T",
    "..-": "U",  "...-": "V", ".--": "W",  "-..-": "X", "-.--": "Y",
    "--..": "Z",
    "-----": "0", ".----": "1", "..---": "2", "...--": "3", "....-": "4",
    ".....": "5", "-....": "6", "--...": "7", "---..": "8", "----.": "9",
    ".-.-.-": ".", "--..--": ",", "..--..": "?", ".----.": "'",
    "-.-.--": "!", "-..-.": "/",  "-.--.": "(",  "-.--.-": ")",
    ".-...": "&",  "---...": ":",  "-.-.-.": ";",  "-...-": "=",
    ".-.-.": "+",  "-....-": "-",  "..--.-": "_",  ".-..-.": '"',
    "...-..-": "$", ".--.-.": "@", "...---...": "SOS",
}


def symbol_to_char(morse: str) -> str:
    return MORSE_TABLE.get(morse, f"[{morse}]")


# ── Real-time morse decoder ───────────────────────────────────────────────────
class LiveMorseDecoder:
    """
    Accepts (is_signal: bool, duration: float) events and immediately
    emits decoded characters/words as they are completed.

    Timing thresholds (relative to dot duration):
        dot:           < 2× dot
        dash:          ≥ 2× dot
        intra-char gap:  < 2× dot   → keep building letter
        inter-char gap:  2–5× dot   → flush letter → print char
        word gap:        > 5× dot   → flush letter → print space
    """

    def __init__(self, dot_duration: float):
        self.dot = dot_duration
        self._symbols: list[str] = []
        self._output = ""

    def feed(self, is_signal: bool, duration: float):
        emitted = ""
        if is_signal:
            self._symbols.append("." if duration < self.dot * 2 else "-")
        else:
            if duration < self.dot * 2:
                pass  # intra-character gap
            elif duration < self.dot * 5:
                emitted = self._flush_letter()
            else:
                emitted = self._flush_letter()
                if emitted:   # only add space after a real letter
                    emitted += " "
        if emitted:
            self._output += emitted
            print(emitted, end="", flush=True)

    def _flush_letter(self) -> str:
        if not self._symbols:
            return ""
        morse = "".join(self._symbols)
        self._symbols = []
        return symbol_to_char(morse)

    def finish(self) -> str:
        """Flush whatever remains at end of stream."""
        tail = self._flush_letter()
        if tail:
            self._output += tail
            print(tail, end="", flush=True)
        print()  # final newline
        return self._output


# ── Noise-adaptive signal detector ───────────────────────────────────────────
class SignalDetector:
    """
    Converts raw audio frames into (is_signal, duration) events using
    RMS amplitude thresholding with a rolling noise baseline.
    """

    def __init__(
        self,
        sample_rate: int,
        frame_size: int,
        threshold_factor: float = 3.0,
        calibration_frames: int = 40,
    ):
        self.frame_duration = frame_size / sample_rate
        self.threshold_factor = threshold_factor
        self._noise: deque = deque(maxlen=calibration_frames)
        self._noise.extend([500.0] * calibration_frames)  # seed (int16 scale)
        self._state = False
        self._state_start = 0.0
        self._clock = 0.0
        self._callback = None

    def set_callback(self, fn):
        """fn(is_signal: bool, duration: float) called on every state change."""
        self._callback = fn

    @property
    def threshold(self) -> float:
        return float(np.mean(self._noise)) * self.threshold_factor

    def feed(self, frame: np.ndarray):
        rms = float(np.sqrt(np.mean(frame.astype(np.float64) ** 2)))
        is_signal = rms > self.threshold

        if not is_signal:
            self._noise.append(rms)  # only update baseline during silence

        if is_signal != self._state:
            duration = self._clock - self._state_start
            if self._clock > 0 and self._callback:
                self._callback(self._state, duration)
            self._state = is_signal
            self._state_start = self._clock

        self._clock += self.frame_duration

    def flush(self):
        """Emit the final in-progress segment."""
        duration = self._clock - self._state_start
        if self._callback and self._clock > 0:
            self._callback(self._state, duration)


# ── Calibration: estimate dot duration from first few seconds ─────────────────
def calibrate_dot_duration(
    stream,
    pa,
    sample_rate: int,
    frame_size: int,
    calibration_seconds: float = 10.0,
    threshold_factor: float = 3.0,
) -> float:
    """
    Record a few seconds of morse, collect signal durations,
    then estimate dot duration via 1D k-means (k=2).
    """
    print(f"  Calibrating for {calibration_seconds:.0f}s — send some morse now...")
    n_frames = int(sample_rate / frame_size * calibration_seconds)

    signal_durations = []
    detector = SignalDetector(sample_rate, frame_size, threshold_factor)

    def on_event(is_sig, dur):
        if is_sig and dur > 0.01:
            signal_durations.append(dur)

    detector.set_callback(on_event)

    for _ in range(n_frames):
        data = stream.read(frame_size, exception_on_overflow=False)
        detector.feed(np.frombuffer(data, dtype=np.int16))
    detector.flush()

    if len(signal_durations) < 2:
        print("  Not enough signal detected; using default 100ms dot.")
        return 0.1

    arr = np.array(signal_durations)
    c1, c2 = np.percentile(arr, 25), np.percentile(arr, 75)
    for _ in range(30):
        labels = np.abs(arr - c1) < np.abs(arr - c2)
        nc1 = arr[labels].mean() if labels.any() else c1
        nc2 = arr[~labels].mean() if (~labels).any() else c2
        if abs(nc1 - c1) < 1e-6 and abs(nc2 - c2) < 1e-6:
            break
        c1, c2 = nc1, nc2

    dot = min(c1, c2)
    dot = max(dot, 0.02)  # floor at 20 ms
    print(f"  Dot duration estimated: {dot*1000:.1f} ms  "
          f"(dash ≈ {dot*3*1000:.0f} ms, word gap ≈ {dot*7*1000:.0f} ms)")
    return dot


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Live morse code audio decoder")
    parser.add_argument("--threshold", type=float, default=3.0,
                        help="Noise multiplier for signal detection (default 3.0; "
                             "raise for noisy rooms)")
    parser.add_argument("--dot", type=float, default=None,
                        help="Manually set dot duration in seconds (skips calibration)")
    parser.add_argument("--rate", type=int, default=44100,
                        help="Sample rate (default 44100)")
    parser.add_argument("--framesize", type=int, default=1024,
                        help="Frames per buffer (default 1024 ≈ 23ms)")
    args = parser.parse_args()

    try:
        import pyaudio
    except ImportError:
        print("pyaudio is required:  pip install pyaudio")
        return

    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=args.rate,
        input=True,
        frames_per_buffer=args.framesize,
    )

    print("=" * 50)
    print("  Live Morse Code Decoder")
    print("=" * 50)

    # ── Determine dot duration ──
    if args.dot:
        dot_duration = args.dot
        print(f"Using manual dot duration: {dot_duration*1000:.1f} ms")
    else:
        dot_duration = calibrate_dot_duration(
            stream, pa, args.rate, args.framesize,
            calibration_seconds=5.0,
            threshold_factor=args.threshold,
        )

    # ── Live decoding loop ──
    print("\nDecoding live — press Ctrl-C to stop.\n")
    print("Output: ", end="", flush=True)

    decoder = LiveMorseDecoder(dot_duration=dot_duration)
    detector = SignalDetector(args.rate, args.framesize, args.threshold)
    detector.set_callback(decoder.feed)

    try:
        while True:
            data = stream.read(args.framesize, exception_on_overflow=False)
            detector.feed(np.frombuffer(data, dtype=np.int16))
    except KeyboardInterrupt:
        detector.flush()
        decoder.finish()
        print("\nDone.")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()


if __name__ == "__main__":
    main()
