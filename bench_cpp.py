"""Kitten-TTS 2 on the optimised C++ CPU runtime (kitten_tts_cpp, llama.cpp fork). Same three sentences, RTF per sentence."""
import argparse, json, time, os, resource, platform
import soundfile as sf
ap = argparse.ArgumentParser()
ap.add_argument("--decoder", default="default"); ap.add_argument("--threads", type=int, default=8)
ap.add_argument("--voice", default="Bruno"); ap.add_argument("--runs", type=int, default=2); ap.add_argument("--tag", required=True)
A = ap.parse_args()
from kitten_tts_cpp import KittenTTS
SENTENCES = [
    "Kitten T T S two runs on the processor of this laptop, with no graphics card involved.",
    "Give it a few seconds of a single speaker, and it reads any new sentence in that voice.",
    "One day, a little girl named Lily found a needle in her room.",
]
kw = dict(threads=A.threads)
if A.decoder != "default": kw["decoder"] = A.decoder
t0 = time.time(); m = KittenTTS("KittenML/kitten-tts-2", **kw); load_s = time.time() - t0
os.makedirs(f"out/{A.tag}", exist_ok=True); rows = []
for r in range(A.runs + 1):
    for i, s in enumerate(SENTENCES):
        p = f"out/{A.tag}/r{r}_s{i+1}.wav"
        t = time.time(); m.generate_to_file(s, p, voice=A.voice); g = time.time() - t
        dur = sf.info(p).duration
        rows.append(dict(run=r, sentence=i + 1, gen_s=round(g, 3), audio_s=round(dur, 3), rtf=round(g / dur, 3)))
        print(json.dumps(rows[-1]), flush=True)
rep = getattr(m, "last_report", None)
warm = [x for x in rows if x["run"] > 0]; rtfs = sorted(x["rtf"] for x in warm)
res = dict(tag=A.tag, args=vars(A), machine=platform.platform(), load_s=round(load_s, 2), median_rtf_warm=rtfs[len(rtfs)//2],
           min_rtf=rtfs[0], max_rtf=rtfs[-1], median_gen_s_warm=sorted(x["gen_s"] for x in warm)[len(warm)//2],
           peak_rss_gb=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9, 2), rows=rows, last_report=str(rep)[:2000],
           when=time.strftime("%Y-%m-%d %H:%M:%S %Z"))
json.dump(res, open(f"out/{A.tag}/result.json", "w"), indent=1)
print("RESULT", json.dumps({k: v for k, v in res.items() if k not in ("rows", "last_report")}))
