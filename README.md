# Kitten-TTS 2 on a Mac: voice cloning, speed and memory, measured

▶ **Video:** https://youtu.be/UWT9aXJOeL8 (ProAI Clips)

The scripts behind the ProAI Clips hands-on with [Kitten-TTS 2](https://huggingface.co/KittenML/kitten-tts-2), KittenML's 1.7B open-weight text-to-speech model. They time the model three ways on Apple silicon (PyTorch on the CPU, MLX on the GPU, and KittenML's C++ runtime), log peak memory, and run the cloning and expression-tag demos from the video.

## Quick start (video: [0:34](https://youtu.be/UWT9aXJOeL8?t=34))

```bash
git clone https://github.com/schoolofai/kitten-tts-2
cd kitten-tts-2
# optional, for the cloning tests: add ref/reference.wav (see ref/README.md)
./run_mac.sh
```

Needs [uv](https://docs.astral.sh/uv/) and an Apple silicon Mac. Everything installs into three venvs inside this folder; nothing global is touched. The model (about 1 GB) downloads from Hugging Face on first run, no login needed. The first run of each path is slower because it downloads and loads the weights.

Expected output: one `RESULT {...}` line per test plus a `peak memory footprint` line, then `Done. Audio in out/, numbers in out/*/result.json`.

## Step by step

Which Mac you need (video: [0:40](https://youtu.be/UWT9aXJOeL8?t=40)): on our M4 Max the C++ runtime peaked at about 1.4 GB and MLX at about 5.5 GB, so the C++ path fits an 8 GB Mac and MLX a 16 GB Mac. Only the M4 Max was measured; other chips will be slower.

### 1. First voice, plain PyTorch install (video: [2:46](https://youtu.be/UWT9aXJOeL8?t=166))

```bash
uv venv -p 3.12 .venv && VIRTUAL_ENV=$PWD/.venv uv pip install kittenml soundfile
/usr/bin/time -l .venv/bin/python bench.py --device cpu --tag cpu_voice
```

Expected: three JSON lines per run (`{"run": 0, "sentence": 1, "gen_s": ..., "audio_s": ..., "rtf": ...}`), run 0 is the warm-up, then `RESULT {"tag": "cpu_voice", ... "median_rtf_warm": ...}`. On our M4 Max: median RTF 2.151 (0.46x real time).

### 2. Cloning (video: [3:21](https://youtu.be/UWT9aXJOeL8?t=201))

Put a 5-30 second clip of one speaker at `ref/reference.wav` (and, optionally, its exact transcript at `ref/reference.txt` so the model skips transcription).

```bash
.venv/bin/python bench.py --device cpu --reference ref/reference.wav --reference-text ref/reference.txt --tag cpu_clone
.venv/bin/python sim.py out/cpu_clone ref/reference.wav
```

Expected: `RESULT {"tag": "cpu_clone", ...}`, then `sim.py` prints a speaker-similarity score per file (open-source Resemblyzer encoder; install it with `uv pip install resemblyzer` in that venv). Our clones scored about 0.91 against the reference; a built-in voice scored about 0.55.

### 3. Speed test: PyTorch vs C++ vs MLX (video: [4:23](https://youtu.be/UWT9aXJOeL8?t=263))

```bash
uv venv -p 3.12 .venv-cpp && VIRTUAL_ENV=$PWD/.venv-cpp uv pip install kitten_tts_cpp soundfile
/usr/bin/time -l .venv-cpp/bin/python bench_cpp.py --threads 8 --tag cpp_voice
/usr/bin/time -l .venv-cpp/bin/python bench_cpp.py --threads 8 --decoder student_w4 --tag cpp_voice_w4

uv venv -p 3.12 .venv-mlx && VIRTUAL_ENV=$PWD/.venv-mlx uv pip install "kittenml[mlx]" soundfile
/usr/bin/time -l .venv-mlx/bin/python bench.py --backend mlx --tag mlx_voice
```

Three fixed sentences, three runs each, first run discarded as warm-up. Expected: a `RESULT` line per test. Ours are in the table below.

### 4. Expression tags and the long passage (video: [6:12](https://youtu.be/UWT9aXJOeL8?t=372))

```bash
.venv-mlx/bin/python demos.py
```

Runs a plain line, the same line with `[excited]` and a laugh tag, an emphasis line, a German voice and, if `ref/reference.wav` exists, a long cloned passage. Expected: one JSON line per demo, then `VOICES 115` (the voice count in kittenml 0.9.6). Tags are beta: they steer delivery rather than guarantee it.

## What we measured

MacBook Pro, Apple M4 Max (12P+4E cores), 128 GB unified memory, macOS 15.6.1. kittenml 0.9.6, kitten_tts_cpp 0.2.0, packed weights. RTF = generation seconds / audio seconds (lower is faster). Peak memory = "peak memory footprint" from `/usr/bin/time -l`. Raw numbers in `results/`.

| Path | Median RTF | × real time | Peak memory |
|---|---|---|---|
| PyTorch, CPU, built-in voice | 2.151 | 0.46× | 4.04 GB |
| PyTorch, CPU, cloned voice | 3.193 | 0.31× | 4.08 GB |
| MLX (GPU), built-in voice | 0.274 | 3.6× | 5.23 GB |
| MLX (GPU), cloned voice | 0.278 | 3.6× | 5.54 GB |
| C++ runtime, 8 threads, default decoder | 0.859 | 1.16× | 1.42 GB |
| C++ runtime, 8 threads, student_w4 decoder | 0.841 | 1.19× | 1.13 GB |

A 35.5-second cloned passage on MLX took 7.0 seconds.

## Limits (video: [6:50](https://youtu.be/UWT9aXJOeL8?t=410))

- KittenML says long single passes can truncate or drift into repetition; the library splits text by sentence. Our 35-second passage still had one small stumble, so listen back before you publish.
- The docs say the Python package is for demo use and isn't optimised for speed.
- Cloning on the C++ runtime needs an offline Python preparation step (see its README), so it isn't tested here.

## Licence notes

- Kitten-TTS 2 weights are under the Stellon Labs Community License (see the [model card](https://huggingface.co/KittenML/kitten-tts-2)): free for research, non-commercial and limited commercial use until you or your affiliates pass USD 1 million in annual revenue or funding, with attribution. The `kittenml` package is Apache 2.0. The MIT licence here covers only these scripts.
- Only clone a voice you have permission to use. No audio is shipped in this repo.

## Sources

- https://huggingface.co/KittenML/kitten-tts-2
- https://github.com/KittenML/KittenTTS
- https://github.com/KittenML/KittenTTS/blob/main/docs/mlx.md
- https://github.com/KittenML/kitten-tts-2-cpp
