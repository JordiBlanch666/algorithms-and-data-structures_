"""Decodes AAC (.m4a/.aac) into a temporary WAV file that SDL_mixer can play."""
from __future__ import annotations

import tempfile
import wave
from pathlib import Path

import av

SAMPLE_RATE = 44100


def decode_to_wav(path: Path) -> Path:
    """Decode the audio with PyAV and save it as a 16-bit stereo WAV.

    The caller is responsible for deleting the temporary file when it is no longer needed.
    """
    temporary = tempfile.NamedTemporaryFile(prefix="sonora_", suffix=".wav", delete=False)
    decoded_path = Path(temporary.name)
    temporary.close()
    succeeded = False
    try:
        with av.open(str(path)) as container:
            if not container.streams.audio:
                raise ValueError(f"No audio stream found in {path.name}.")
            stream = container.streams.audio[0]
            resampler = av.AudioResampler(format="s16", layout="stereo", rate=SAMPLE_RATE)
            with wave.open(str(decoded_path), "wb") as output:
                output.setnchannels(2)
                output.setsampwidth(2)
                output.setframerate(SAMPLE_RATE)
                for frame in container.decode(stream):
                    for pcm_frame in resampler.resample(frame):
                        output.writeframes(bytes(pcm_frame.planes[0])[: pcm_frame.samples * 4])
                for pcm_frame in resampler.resample(None):  # flush the resampler buffer
                    output.writeframes(bytes(pcm_frame.planes[0])[: pcm_frame.samples * 4])
        succeeded = True
        return decoded_path
    finally:
        if not succeeded:
            decoded_path.unlink(missing_ok=True)
