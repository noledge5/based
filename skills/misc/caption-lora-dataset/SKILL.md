---
name: caption-lora-dataset
description: Build a captioned character LoRA training dataset from a folder of images — dedupe, rename, and caption with a Krea 2 tuned prompt, ready for ostris/ai-toolkit. Use when the user wants to caption images for LoRA training, prepare a character dataset, or asks how to caption for Krea 2 / Qwen-Image / other VLM-conditioned models.
---

# Caption a LoRA dataset

Turns a messy folder of images into an ai-toolkit dataset: `name_001.png` +
`name_001.txt` pairs, captioned against a prompt tuned for Krea 2 character
LoRAs.

Tuned for **Krea 2**, and applies unchanged to any model with a VLM text encoder
(Qwen-Image and relatives). For CLIP-era models that actually want booru tags,
this prompt is the wrong shape.

## The one rule

**Whatever you don't caption gets absorbed into the trigger token.**

So caption what should stay *changeable* (pose, framing, outfit, background) and
stay silent about what should stay *welded to the character* (face, constant
hair, eye colour). Lighting goes uncaptioned too, so the base model keeps
control of it at inference.

## Steps

### 1. Establish the character's constant traits

Ask the user which traits are identical in every image — these get injected into
the prompt as a do-not-mention list, and it's the single highest-leverage input.

The trap is hair: constant across the set → leave it out (identity); varying →
caption it (controllable). Same call applies to a signature outfit.

### 2. Run the script

```bash
pip install anthropic pillow
export ANTHROPIC_API_KEY=...

scripts/build_dataset.py -i ./raw -o ./dataset --prefix ada \
    --constant-traits "short black hair, brown eyes, freckles"
```

Start with `--dry-run` to see the rename plan, duplicate drops, and resolution
warnings without spending anything.

Useful flags:

| Flag | Why |
| --- | --- |
| `--note-quality` | Append visible defects to captions — see below |
| `--trigger ohwx` | Write a literal token instead of `[trigger]` |
| `--model claude-sonnet-5` | Cheaper per image; defaults to `claude-opus-5` |
| `--dedupe-distance 0` | Disable near-duplicate detection |
| `--overwrite` | Recaption images that already have a `.txt` |

Reruns skip images that already have captions, so an interrupted run resumes for
free.

### 3. Review before training

The script writes `_report.md` (per-image sizes, sharpness, defects, warnings)
and `_manifest.json`. **Read the report and hand-edit captions.** Auto-captions
hallucinate constant traits and miss occlusions; the edit pass is the difference
between a good LoRA and a mushy one. Check especially that no caption mentions a
declared constant trait.

### 4. Point ai-toolkit at it

Captions contain `[trigger]`, which ai-toolkit substitutes with the config's
`trigger_word` at load time — so one dataset serves any trigger word.

## Quality defects in captions

`--note-quality` appends fixed phrases (`a blurry, low-resolution photo`) to
images with visible defects. The model returns defects as a constrained enum and
the script does the wording, so the vocabulary is identical every time — which is
what makes the phrase learnable.

Use it when a poor-quality image is worth keeping anyway (the only shot from
behind, a rare expression). Do not use it as a substitute for dropping bad
images, and know it works by *contrast* — if every image is equally bad there's
nothing to contrast against and the effect is weak. Without the flag, defects are
still recorded in the report so you can decide what to cut.

## Bundled resources

- [references/caption-system-prompt.md](references/caption-system-prompt.md) —
  the captioning prompt. Copy-paste it into any other agent or VLM; substitute
  `{{CONSTANT_TRAITS}}` and `{{QUALITY_BLOCK}}` yourself if you do.
- [references/krea2-captioning-guide.md](references/krea2-captioning-guide.md) —
  why the prompt is shaped this way, dataset sizing, training settings, sources.
- [scripts/build_dataset.py](scripts/build_dataset.py) — the pipeline.
