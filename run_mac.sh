#!/bin/bash
# Kitten-TTS 2 on Apple silicon: the three ways we timed in the video, one at a time.
# Needs uv (https://docs.astral.sh/uv/). Everything stays inside this folder (three venvs + out/).
set -e
cd "$(dirname "$0")"
uv venv -q -p 3.12 .venv     && VIRTUAL_ENV=$PWD/.venv     uv pip install -q kittenml soundfile
uv venv -q -p 3.12 .venv-mlx && VIRTUAL_ENV=$PWD/.venv-mlx uv pip install -q "kittenml[mlx]" soundfile
uv venv -q -p 3.12 .venv-cpp && VIRTUAL_ENV=$PWD/.venv-cpp uv pip install -q kitten_tts_cpp soundfile
CLONE=(); [ -f ref/reference.wav ] && CLONE=(--reference ref/reference.wav) && [ -f ref/reference.txt ] && CLONE+=(--reference-text ref/reference.txt)
T="/usr/bin/time -l"
$T .venv/bin/python bench.py --device cpu --tag cpu_voice 2>&1 | tee cpu_voice.log | grep -E "RESULT|peak memory footprint"
[ ${#CLONE[@]} -gt 0 ] && $T .venv/bin/python bench.py --device cpu "${CLONE[@]}" --tag cpu_clone 2>&1 | tee cpu_clone.log | grep -E "RESULT|peak memory footprint"
$T .venv-cpp/bin/python bench_cpp.py --threads 8 --tag cpp_voice 2>&1 | tee cpp_voice.log | grep -E "RESULT|peak memory footprint"
$T .venv-cpp/bin/python bench_cpp.py --threads 8 --decoder student_w4 --tag cpp_voice_w4 2>&1 | tee cpp_voice_w4.log | grep -E "RESULT|peak memory footprint"
$T .venv-mlx/bin/python bench.py --backend mlx --tag mlx_voice 2>&1 | tee mlx_voice.log | grep -E "RESULT|peak memory footprint"
[ ${#CLONE[@]} -gt 0 ] && $T .venv-mlx/bin/python bench.py --backend mlx "${CLONE[@]}" --tag mlx_clone 2>&1 | tee mlx_clone.log | grep -E "RESULT|peak memory footprint"
.venv-mlx/bin/python demos.py
echo "Done. Audio in out/, numbers in out/*/result.json"
