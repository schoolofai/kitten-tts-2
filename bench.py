"""Kitten-TTS 2 hands-on benchmark: time each sentence, report real-time factor (RTF = generation seconds / audio seconds)."""
import argparse, json, time, os, resource, platform
import soundfile as sf
ap = argparse.ArgumentParser()
ap.add_argument("--backend", default=None)          # None = PyTorch, "mlx" = Apple GPU
ap.add_argument("--device", default=None)           # "cpu" forces CPU for PyTorch
ap.add_argument("--weights", default="packed")
ap.add_argument("--decoder", default=None)
ap.add_argument("--voice", default="Bruno")
ap.add_argument("--reference", default=None)        # clone from this wav instead of a built-in voice
ap.add_argument("--reference-text", default=None)
ap.add_argument("--runs", type=int, default=2)
ap.add_argument("--tag", required=True)
ap.add_argument("--threads", type=int, default=0)
A = ap.parse_args()
import torch
if A.threads: torch.set_num_threads(A.threads)
from kittenml import KittenTTS
SENTENCES = [
    "Kitten T T S two runs on the processor of this laptop, with no graphics card involved.",
    "Give it a few seconds of a single speaker, and it reads any new sentence in that voice.",
    "One day, a little girl named Lily found a needle in her room.",
]
kw = dict(weights=A.weights)
if A.backend: kw["backend"] = A.backend
if A.device: kw["device"] = A.device
if A.decoder: kw["decoder"] = A.decoder
t0 = time.time(); m = KittenTTS("KittenML/kitten-tts-2", **kw); load_s = time.time() - t0
spk = dict(reference=A.reference, reference_text=open(A.reference_text).read().strip() if A.reference_text else None) if A.reference else dict(voice=A.voice)
os.makedirs(f"out/{A.tag}", exist_ok=True)
rows = []
for r in range(A.runs + 1):            # run 0 = warm-up (first call compiles / caches), reported separately
    for i, s in enumerate(SENTENCES):
        t = time.time(); audio = m.generate(s, advanced={"seed": 1234 + r}, **spk); g = time.time() - t
        dur = len(audio) / m.sample_rate
        sf.write(f"out/{A.tag}/r{r}_s{i+1}.wav", audio, m.sample_rate)
        rows.append(dict(run=r, sentence=i + 1, gen_s=round(g, 3), audio_s=round(dur, 3), rtf=round(g / dur, 3)))
        print(json.dumps(rows[-1]), flush=True)
warm = [x for x in rows if x["run"] > 0]
rtfs = sorted(x["rtf"] for x in warm); med = rtfs[len(rtfs) // 2]
peak_gb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9   # macOS reports bytes
res = dict(tag=A.tag, args=vars(A), torch=torch.__version__, torch_threads=torch.get_num_threads(), machine=platform.platform(),
           load_s=round(load_s, 2), median_rtf_warm=med, min_rtf=rtfs[0], max_rtf=rtfs[-1],
           median_gen_s_warm=sorted(x["gen_s"] for x in warm)[len(warm)//2], peak_rss_gb=round(peak_gb, 2), rows=rows,
           when=time.strftime("%Y-%m-%d %H:%M:%S %Z"))
json.dump(res, open(f"out/{A.tag}/result.json", "w"), indent=1)
print("RESULT", json.dumps({k: v for k, v in res.items() if k != "rows"}))
