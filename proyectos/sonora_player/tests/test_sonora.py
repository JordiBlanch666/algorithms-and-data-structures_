"""Tests for the logic that doesn't need the window: python -m unittest discover tests"""
import math
import struct
import sys
import tempfile
import unittest
import wave
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sonora.lyrics import NOT_FOUND, fetch_lrclib, parse_lrc, parse_lrc_entries  # noqa: E402
from sonora.metadata import format_time, read_track  # noqa: E402


def make_wav(path: Path, seconds: float = 1.0, rate: int = 44100) -> Path:
    """Generate a 440 Hz tone as a 16-bit stereo WAV."""
    with wave.open(str(path), "wb") as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(rate)
        samples = bytearray()
        for i in range(int(seconds * rate)):
            value = int(12000 * math.sin(2 * math.pi * 440 * i / rate))
            samples += struct.pack("<hh", value, value)
        out.writeframes(bytes(samples))
    return path


class TestTime(unittest.TestCase):
    def test_format_time(self):
        self.assertEqual(format_time(0), "0:00")
        self.assertEqual(format_time(65.9), "1:05")
        self.assertEqual(format_time(-3), "0:00")


class TestLyrics(unittest.TestCase):
    LRC = "[ar:Artist]\n[00:12.50]First line\n[00:05.00]Intro\n[01:02]Chorus\n[00:20.00]\n"

    def test_parse_lrc_entries_sorts_and_converts_timestamps(self):
        self.assertEqual(
            parse_lrc_entries(self.LRC),
            [(5.0, "Intro"), (12.5, "First line"), (62.0, "Chorus")],
        )

    def test_line_with_several_timestamps(self):
        entries = parse_lrc_entries("[00:10.00][00:40.00]Repeated line")
        self.assertEqual([t for t, _ in entries], [10.0, 40.0])

    def test_parse_lrc_strips_timestamps(self):
        self.assertEqual(parse_lrc(self.LRC), "Intro\n\nFirst line\n\nChorus")

    def test_parse_lrc_plain_text(self):
        self.assertEqual(parse_lrc("Hello\n\nWorld"), "Hello\n\nWorld")

    def test_fetch_lrclib_offline_does_not_crash(self):
        from urllib.error import URLError
        with mock.patch("sonora.lyrics.urlopen", side_effect=URLError("offline")):
            self.assertIn("Couldn't connect", fetch_lrclib("Song", "Artist"))

    def test_fetch_lrclib_404(self):
        from urllib.error import HTTPError
        error = HTTPError("url", 404, "Not Found", {}, None)
        with mock.patch("sonora.lyrics.urlopen", side_effect=error):
            self.assertEqual(fetch_lrclib("Song", "Artist"), NOT_FOUND)


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.folder = Path(tempfile.mkdtemp())

    def test_artist_and_title_from_file_name(self):
        track = read_track(make_wav(self.folder / "My Band - My Song.wav"))
        self.assertEqual((track.artist, track.title), ("My Band", "My Song"))
        self.assertAlmostEqual(track.duration, 1.0, places=2)

    def test_no_dash_means_unknown_artist(self):
        track = read_track(make_wav(self.folder / "demo.wav"))
        self.assertEqual((track.artist, track.title), ("Unknown artist", "demo"))


class TestAacDecoding(unittest.TestCase):
    """Creates an .m4a (AAC, like iTunes purchases) and checks that it decodes to WAV."""

    def test_m4a_to_wav(self):
        try:
            import av
        except ImportError:
            self.skipTest("PyAV is not installed")
        from sonora.audio import decode_to_wav

        folder = Path(tempfile.mkdtemp())
        wav = make_wav(folder / "tone.wav", seconds=2.0)
        m4a = folder / "tone.m4a"
        with av.open(str(wav)) as source, av.open(str(m4a), "w") as target:
            stream = target.add_stream("aac", rate=44100)
            for frame in source.decode(audio=0):
                for packet in stream.encode(frame):
                    target.mux(packet)
            for packet in stream.encode(None):
                target.mux(packet)

        decoded = decode_to_wav(m4a)
        try:
            with wave.open(str(decoded), "rb") as result:
                self.assertEqual(result.getnchannels(), 2)
                self.assertEqual(result.getframerate(), 44100)
                duration = result.getnframes() / result.getframerate()
            self.assertAlmostEqual(duration, 2.0, delta=0.1)
        finally:
            decoded.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
