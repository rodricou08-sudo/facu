import whisper, json, sys
m = whisper.load_model('medium', download_root=sys.argv[1])
r = m.transcribe(sys.argv[2], language='es', word_timestamps=True, condition_on_previous_text=False,
  initial_prompt="Video en español rioplatense, voseo. No tenés amigos, sos un choto, laburo, pibe, juntarte, amigo casual, Universidad de Kansas, 50 horas, 90 horas, 200 horas, matemáticas, mové el orto.")
json.dump(r, open(sys.argv[3],"w"), ensure_ascii=False)
for s in r['segments']: print(f"[{s['start']:6.2f}-{s['end']:6.2f}] {s['text']}")
