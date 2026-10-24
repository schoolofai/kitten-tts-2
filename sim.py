"""Speaker similarity of generated clips vs your reference clip (Resemblyzer). Usage: python sim.py out/mlx_clone ref/reference.wav"""
import sys, glob, os, json
from resemblyzer import VoiceEncoder, preprocess_wav
enc = VoiceEncoder("cpu", verbose=False); ref = enc.embed_utterance(preprocess_wav(sys.argv[2])); R = {}
for f in sorted(glob.glob(f"{sys.argv[1]}/*.wav")):
    R[os.path.basename(f)[:-4]] = round(float(enc.embed_utterance(preprocess_wav(f)) @ ref), 3)
print(json.dumps(R, indent=1))
