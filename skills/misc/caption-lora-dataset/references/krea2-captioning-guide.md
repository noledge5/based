# Captioning for Krea 2 character LoRAs

Background for [`caption-system-prompt.md`](caption-system-prompt.md). Read this
when you need to adapt the prompt, not to run the tool.

## Why natural language, not tags

Krea 2 conditions on **Qwen3-VL-4B-Instruct**, tapped across twelve intermediate
layers, feeding a 12.9B single-stream MMDiT. The text encoder is an
instruction-tuned vision-language model, not a CLIP-style bag-of-tokens encoder —
it parses grammar. Danbooru-style tag soup underperforms plain descriptive
sentences on this architecture, the same way it does on Qwen-Image.

Krea's own trainer auto-captions datasets with this exact Qwen-VL model, which is
a strong hint about what the conditioner wants to read.

## The one rule that matters

**Whatever you do not describe gets absorbed into the trigger token.**

That single mechanic drives every other decision:

| Goal | Do |
| --- | --- |
| Character's face stays locked to the trigger | Never caption eye colour, face shape, or constant hair |
| Outfit stays swappable at inference | Caption the outfit in every image where it's visible |
| Lighting stays controllable | Never caption lighting |
| Pose stays controllable | Caption pose and framing every time |

The `--constant-traits` flag operationalises the first row: whatever you list
there is injected into the prompt as a do-not-mention list.

### The hair nuance

Hair is the trait people get wrong most often.

- Hair is **identical in every image** → do not caption it. It's identity, and it
  should bind to the trigger.
- Hair **varies across the dataset** (different lengths, styles, colours) → do
  caption it, so it becomes controllable rather than an averaged mess.

Same logic applies to a signature outfit. Decide whether you want it welded to
the character or promptable, then caption accordingly.

## Should you caption quality defects?

Yes — with three conditions.

**The mechanic.** Uncaptioned artefacts land in the weights. If a third of your
set is soft or JPEG-mangled and nothing says so, the LoRA learns
"this character = slightly mushy". Caption the defect and it binds to those words
instead; omit the words at inference and you get clean output. This is the same
mechanism as quality tags in SD1.5/SDXL training.

**Condition 1 — you need contrast.** This works because the model can compare
flagged against unflagged images inside your set. If *every* image is equally
bad there's nothing to contrast, and you're relying purely on the base model's
prior for "blurry". It still helps a little, but much less.

**Condition 2 — it's damage control, not a substitute for curation.** Dropping a
bad image beats captioning it. Reach for defect captioning when the image is
genuinely irreplaceable — the only shot from behind, the only instance of a rare
expression — and mediocre quality is the price of keeping it.

**Condition 3 — vocabulary consistency beats vocabulary richness.** A defect
phrase is only learnable if it appears identically every time. This is why the
tool does not let the model phrase defects freely: the model returns a
`defects` list drawn from a fixed four-value enum, and the script appends the
exact same wording each time. Four consistent phrases outperform twenty
expressive ones.

For Krea 2, phrase them as natural language — `"a slightly blurry photo of
[trigger] ..."` — not as `lowres, jpeg artifacts, blurry`.

## Dataset shape

- **20–30 images** is the working sweet spot for a single character.
- Mix framings deliberately: extreme close-up, head-and-shoulders, waist-up, full
  body. A set that is all headshots produces a LoRA that falls apart the moment
  you prompt a full-body shot.
- Vary angle, expression, and background. Vary lighting too — and then don't
  caption it, so the model averages it out into "lighting is free".
- ai-toolkit never upscales. It downscales and buckets by aspect ratio, so
  varying aspect ratios are fine, but anything below your training resolution is
  permanently soft. 1024px shortest side is the sensible floor.
- Larger recipes (hundreds of images plus regularisation sets) exist for
  production-grade models. Overkill for a first character LoRA.

## Training settings

Community consensus for Krea 2 character LoRAs in ai-toolkit:

- Train on **Krea 2 RAW**, run the result on **Turbo**.
- **LoRA**, linear rank 32 / alpha 32.
- Learning rate `1e-4`, AdamW.
- Roughly 1000–2000 steps for ~25 images; save every 250 and pick a checkpoint by
  eye. Character LoRAs overfit late — the last checkpoint is often not the best.
- LoKr is the more parameter-efficient alternative, and mostly shows up for style
  work or tight VRAM budgets. No evidence it captions or trains characters better
  than plain LoRA here. Default to LoRA.

## ai-toolkit dataset contract

- Images and captions share a basename: `char_001.png` + `char_001.txt`.
- Only `jpg`, `jpeg`, `png` are supported.
- The literal string `[trigger]` in a caption is substituted with the config's
  `trigger_word` at load time. Keep `[trigger]` in the files and set the word in
  your config — that way one dataset serves several trigger words.

## Sources

- [Krea 2 technical report](https://www.krea.ai/blog/krea-2-technical-report) — architecture, Qwen3-VL text encoder
- [Krea 2 LoRA training](https://www.krea.ai/blog/krea-2-lora-training) — official captioning guidance
- [ostris/ai-toolkit README](https://github.com/ostris/ai-toolkit/blob/main/README.md) — dataset format, `[trigger]`
- [promptdexter KREA2 LoRA guide](https://promptdexter.com/blog/krea2-lora-training-guide) — caption length, trigger placement
- [Krea 2 on a 12GB GPU (Civitai)](https://civitai.com/articles/32566/how-to-train-a-krea-2-lora-on-a-12gb-gpu)
- [JahJedi/krea2-character-lora-recipe](https://huggingface.co/JahJedi/krea2-character-lora-recipe) — describe-only-what-is-visible, measured hyperparameters
