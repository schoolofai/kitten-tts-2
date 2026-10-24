"""Demo clips from the video (MLX backend on Apple silicon). Clone demos run only if ref/reference.wav exists."""
import json, time, os, soundfile as sf
from kittenml import KittenTTS
m = KittenTTS("KittenML/kitten-tts-2", backend="mlx")
REF = None
if os.path.exists("ref/reference.wav"):
    REF = dict(reference="ref/reference.wav")
    if os.path.exists("ref/reference.txt"): REF["reference_text"] = open("ref/reference.txt").read().strip()
LONG = ("Here is a longer passage, to see how the model copes with more than one sentence. "
        "The library splits long text on sentence boundaries and generates it chunk by chunk. "
        "Then it joins the pieces, trims the silence at each edge, and adds short fades, so the seams should be hard to hear. "
        "That matters, because the team says the model can drift into repetition when it is asked for a whole script in one pass. "
        "So if you are building an audiobook or a long narration, this chunking is doing a lot of quiet work for you.")
D = [
 ("d_plain", "We won. I can hardly believe it.", dict(voice="Kiki")),
 ("d_tagged", "[excited] We won <laugh> I can hardly believe it.", dict(voice="Kiki")),
 ("d_emph", "I told you (((never))) to open that door.", dict(voice="Victor")),
 ("d_german", "Guten Morgen. Ich wünsche dir einen wunderschönen Tag.", dict(voice="German", normalize=False)),
]
if REF:
    D += [("d_clone", "This voice was cloned from a sixteen second clip, right here on a laptop.", REF), ("d_long_clone", LONG, REF)]
os.makedirs("out/demos", exist_ok=True); log = []
m.generate("Warm up.", voice="Bruno")
for name, text, kw in D:
    t = time.time(); a = m.generate(text, advanced={"seed": 77}, **kw); g = time.time() - t
    p = f"out/demos/{name}.wav"; sf.write(p, a, m.sample_rate); dur = len(a) / m.sample_rate
    log.append(dict(name=name, text=text, gen_s=round(g, 2), audio_s=round(dur, 2), rtf=round(g / dur, 3)))
    print(json.dumps(log[-1]), flush=True)
print("VOICES", len(m.available_voices))
json.dump(log, open("out/demos/log.json", "w"), indent=1)
