# Boruta and SHAP interactive explainer

Owner: `feature-selection-explainer`. Role: Chinese educational method demonstration,
not an empirical analysis of journal data or a Paper Analysis. The two modes use
separate teaching examples; switching modes does not train or select a model.

## Question

How do shadow-based feature selection and Shapley prediction attribution differ?

## Referenced inputs

Only the explicit synthetic measurements and model in `analysis/model.mjs`,
plus the primary and official references below. No journal datasets are loaded.

## Run

Requires Node.js 20.10 or newer; no npm dependencies or network at runtime.

```sh
node research/feature-selection-explainer/analysis/model.test.mjs
node research/feature-selection-explainer/analysis/build.mjs
node research/feature-selection-explainer/analysis/build.mjs --light
```

Open `artifacts/anatomy/index.html` (dark) or `index-light.html` (light) under
this owner. The generated pages include their CSS, SVG and JavaScript. Screenshots
and other verification outputs belong in the same ignored pipeline directory.

## Concept and parts, before geometry

A six-track mechanical comparison ruler carries six independent sliding cursors;
a seventh, illuminated cursor shows either the strongest shadow importance or
the mean marginal contribution. Cursor displacement is the numerical measurement,
not elapsed time. Boruta uses a nonnegative scale; SHAP uses a signed scale.

Figure tier: one instrument with 66 solid parts, plus engraved ticks and fasteners.
The assembly is grouped as follows (each repeated part has a distinct track ID):

- Base: four feet (1–4), bedplate (5), inset deck (6), maker plate (7).
- Structure: seven left rail strips (8–14), seven right rail strips (15–21),
  seven left stops (22–28), seven right stops (29–35).
- Mechanism: seven cursor soles (36–42), seven pointer bodies (43–49),
  seven finger grips (50–56), seven ruler strips (57–63).
- Controls: three square selector keys (64–66).

All solids are rectangular machined parts; no pipes, cables, round solids,
exploded poses or WebGL. The per-track painter order follows the physical support
stack, tracks run back to front. Moving cursors remain on the top of their rails.
The same pure model supplies the measurements, cursor targets and explanation.

## Scientific contract

Boruta mode replays 20 explicitly synthetic importance measurements. It does not
fit a random forest. Three illustrative shadow channels represent the random
benchmark; production Boruta may generate more shadow columns. Each original
feature scores a hit only when its importance exceeds the maximum shadow value.
The illustration decides at a fixed horizon using one-sided Binomial(20, .5)
tails and threshold .05 / (2 × 3). This is a labelled teaching simplification,
not a reimplementation of Boruta's sequential procedure. It keeps rejected
channels for visibility instead of removing them from later fits.

SHAP mode enumerates all six permutations and eight background rows for
`f(A,B,C) = 10 + 4A - 2B + C + λAB`. Each input independently takes −1 or +1
with equal probability. Missing features are averaged over those background rows;
they are not filled with zero. For `λ=6, x=(1,1,1)`, baseline=10,
prediction=19 and exact contributions=(7,1,1). Units are arbitrary model scores.
The background is fixed and independent, so conditional and interventional
expectations coincide in this example; they need not coincide in real data.

## Sources

- Kursa & Rudnicki (2010), [Feature Selection with the Boruta Package](https://www.jstatsoft.org/article/view/v036i11), §2.
- Lundberg & Lee (2017), [A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874), §2–4.
- SHAP maintainers, [introduction with Shapley values](https://shap.readthedocs.io/en/latest/example_notebooks/overviews/An%20introduction%20to%20explainable%20AI%20with%20Shapley%20values.html), background expectation, additivity and correlated features.
- [BorutaShap implementation](https://github.com/Ekeany/Boruta-Shap): an example of combining SHAP importance with shadow-based selection, not a synonym for SHAP.

Source checks: 2026-10-16. The drawing kit is a vendored copy of the locally
installed Anatomy `kit/iso-kit.mjs`; its MIT license is retained in
`analysis/vendor/LICENSE`.

## Verification

Verified 2026-10-16 with Node.js 25.5.0 and headless Chrome:

- The model test passes 40 sample/interaction combinations against an independent
  analytic solution, plus coalition-path sums and fixed-horizon binomial decisions.
  A separate numerical review checked all 104 UI parameter combinations.
- Browser controls: final Boruta outcomes, SHAP A/B contributions, zero interaction,
  signed extreme inputs, keyboard navigation and automatic tour passed. Offscreen
  animation stopped and resumed on return; theme switching passed. Motion frames
  were inspected; numeric results remain exact while cursor positions ease.
- Desktop and 390px phone layouts, both themes, reduced motion and 4× mechanism
  close-ups inspected. No sideways overflow or browser console errors observed.
- Anatomy line checks returned zero floating ends (672 checked endpoints) in
  both themes and the tested normal/extreme poses. The rectangular-only instrument
  has no pipe/round-part audit or WebGL layer.

Local screenshot and browser-drive evidence remains under `artifacts/anatomy/`.
