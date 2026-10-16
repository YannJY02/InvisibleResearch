# Feature engineering explainer

A Chinese interactive teaching figure built with Anatomy. This owner contains
synthetic examples, not an empirical study or a paper analysis.

## Concept and parts plan

Figure tier: a four-lane mechanical slide-rule bench. Its carriages show the
filled area, rescaled area, categorical switches, and area per room. Each
position is computed from the same pure model as the numerical readout.
All training statistics remain fixed when a new sample changes.

The drawing uses rectangular machined parts, with no pipes, round bodies,
WebGL, or exploded pose. Structural parts planned before geometry:

- Base: four rubber feet, four foot mounting pads, one bed, one top deck,
  one engraved nameplate, two edge guards (13).
- Four mechanisms: four cassette beds, eight guide rails, eight end stops,
  four ruler strips, four fixed reference inserts (28).
- Moving parts: three numerical carriages with three grips and six shoes;
  three category switches with three grips and three shoes (21).
- Six category stop pads and one missing-value flag mount (7).

The final drawing has 71 structural solids (three rather than four reference
inserts, and two shoes per category switch), plus engravings, screws, ruler
marks, and the missing flag. The drawing is an explanatory instrument, not a claim
that feature engineering literally operates mechanically.

## Run

Requires Node.js 20.10+ and the installed Anatomy skill. The build resolves it
from `ANATOMY_HOME`, defaulting to `~/.agents/skills/anatomy`.

```sh
node research/feature-engineering-explainer/build.mjs
node research/feature-engineering-explainer/build.mjs --light
node --test research/feature-engineering-explainer/model.test.mjs
node research/feature-engineering-explainer/verify-browser.mjs
```

Open `artifacts/interactive/index.html` or `index-light.html` in a browser.
Both are self-contained, work offline, and include their JavaScript and SVG.
All generated pages and screenshots belong to `artifacts/interactive/`.
Browser verification also requires Chrome/Chromium; Anatomy supports
`CHROME_PATH` when it is not in a standard installation location.

## Verification

Checked on 2026-10-16: eight pure-model tests; desktop and 390 px phone
rendering; all feature outputs for missing, minimum and maximum inputs;
keyboard range/checkbox/step controls; native region and room selectors in
the in-app browser; idle tour; offscreen pause; reduced motion; dark/light
themes; zero floating line ends at resting and extreme positions. Inspected
screenshots and a six-frame motion sheet, including close-ups of the
mechanisms. Browser consoles were clean. No WebGL or pipe/round-body audit
is applicable to this slab-only figure. Document governance also passed.

## Teaching boundary

The five apartments are deliberately synthetic. Their training areas are
40, 60, 80, 100, 120 square metres. Median imputation and min-max scaling
use only this training set. Category order is explicit. No predictive model
is trained and no accuracy improvement is claimed. The final vector is an
illustration of combining features, not a recommended production pipeline:
other numerical columns may also need scaling for a scale-sensitive model.
New ratios need a substantive rationale and validation on held-out data.

Primary references, checked 2026-10-16:

- [scikit-learn: preprocessing](https://scikit-learn.org/stable/modules/preprocessing.html)
- [scikit-learn: imputation](https://scikit-learn.org/stable/modules/impute.html)
- [scikit-learn: data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage)

Artwork uses the [Anatomy kit](https://github.com/wheresryan22/anatomy), MIT.
