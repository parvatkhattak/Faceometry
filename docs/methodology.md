# Faceometry Methodology

## Scientific Positioning

Faceometry is a **facial geometry analysis tool**. It analyzes mathematical proportions, symmetry, and geometric ratios of facial structure.

**Faceometry does NOT:**
- Claim to objectively measure beauty or attractiveness
- Assert that the Golden Ratio determines beauty
- Claim that its scoring weights are scientifically optimal

**Faceometry DOES:**
- Measure facial proportions using computer vision
- Calculate bilateral symmetry from landmark positions
- Measure proximity of selected ratios to φ (the Golden Ratio)
- Analyze facial thirds (vertical proportions)
- Analyze facial fifths (horizontal proportions)
- Combine these into a transparent "Facial Harmony Score"

---

## Measurements

### Coordinate Normalization

All measurements are normalized by a stable reference dimension (face height):

$$d_{normalized} = \frac{d}{D_{reference}}$$

This makes measurements independent of image resolution and face size.

### Symmetry

For each bilateral landmark pair:
1. Estimate the facial midline from nose bridge and chin landmarks
2. Reflect left-side landmarks across the midline
3. Calculate normalized Euclidean error: $E_i = \sqrt{(x_i - x_i')^2 + (y_i - y_i')^2}$
4. Aggregate errors into a symmetry score

### Golden Ratio

$$\phi = \frac{1+\sqrt{5}}{2} \approx 1.618$$

For each configured ratio:
- Deviation: $D_i = \frac{|R_i - \phi|}{\phi}$
- Score: $S_i = \max(0, 100 \cdot (1 - D_i))$

Only explicitly configured ratios are compared to φ.

### Facial Thirds

Vertical divisions: hairline → eyebrows → nose base → chin

### Facial Fifths

Horizontal divisions: face edge → eye → inter-eye → eye → face edge

---

## Scoring

$$S_{harmony} = \sum_i w_i \cdot S_i$$

Default weights (experimental):
| Component | Weight |
|-----------|--------|
| Symmetry | 35% |
| Proportion | 25% |
| Golden Ratio | 20% |
| Facial Thirds | 10% |
| Facial Fifths | 10% |

These weights are configurable and are not claimed to be scientifically optimal.
