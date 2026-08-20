# Arabic Sign Language (ArSL) Letter Recognition
### AI for Lebanon — Education & Accessibility

---

## 1. Project Title & Abstract

**Title:** Arabic Sign Language Letter Recognition: A CNN-Based Accessibility Tool for Deaf and Hard-of-Hearing Learners in Lebanon

**Abstract** *(~150-200 words — write this LAST, once results are in)*
> Summarize in 4-5 sentences:
> - The problem (limited accessible tools for learning Arabic Sign Language)
> - Your approach (CNN trained on ArSL2018 dataset, 32-letter classification)
> - Your key result (test accuracy — fill in once training completes)
> - Your one-sentence takeaway/conclusion

"Deaf and hard-of-hearing individuals in Lebanon and the wider Arabic-speaking world face limited access to digital tools for learning Arabic Sign Language (ArSL). This project trains a convolutional neural network (CNN) to classify hand-sign images into 32 Arabic alphabet letters, using the publicly available ArSL2018 dataset (54,049 images, 40 signers). The model achieves **96.78%** test accuracy after training with class-weighted loss and data augmentation to address class imbalance, with every class individually achieving over 0.92 precision and recall. The model was further deployed in a live webcam demo using MediaPipe hand detection, correctly identifying all 32 letters (100% top-1) under controlled lighting conditions, though 9 letters required posture adjustment and 4 showed persistently variable confidence — findings that both validate the model's real-world applicability and surface an honest domain gap between studio-quality training data and live deployment. This work demonstrates the feasibility of a lightweight, low-cost recognition system that could underpin accessible learning apps for ArSL students in Lebanon and beyond."

---

## 2. Introduction & Problem Statement

*(~1/2 page)*

**Points to cover:**
- **The problem:** Deaf and hard-of-hearing students in Lebanon have limited access to structured tools for learning/practicing Arabic Sign Language, compared to resources available for spoken Arabic or other sign languages (e.g., ASL).
- **Why it matters / who benefits:**
  - Deaf and hard-of-hearing students and their families
  - Educators and schools serving deaf students in Lebanon
  - Broader Arabic-speaking deaf community (dataset isn't Lebanon-specific, but the accessibility problem is regionally shared)
- **Core goal of the project:** Build and evaluate a CNN that can automatically recognize ArSL alphabet hand-signs from images, as a technical foundation for an accessible learning or communication tool.
- **Scope:** This project focuses on the *static alphabet* recognition task (not continuous signing/sentences), which is a reasonable and well-scoped entry point given the timeline.

---

## 3. Methodology (Approach / Reproduction Details)

*(~3/4 page)*

**Dataset:**
- ArSL2018 dataset — 54,049 grayscale (64×64) images, 32 Arabic sign language letter classes, collected from 40 participants (Latif et al., 2019)
- Publicly available via Mendeley Data: https://data.mendeley.com/datasets/y7pckrw6z2/1
- Mild class imbalance (~1,293–2,114 images per class)

**Preprocessing:**
- Images normalized to [0,1]
- Stratified split: 70% train / 15% validation / 15% test
- Data augmentation on training set only: random horizontal flip, brightness, contrast (to improve generalization / simulate real-world variation in signing conditions)
- Class-weighted loss (`compute_class_weight`) to counter mild class imbalance

**Model architecture:**
- Custom CNN: 3 convolutional blocks (32 → 64 → 128 filters), each with BatchNorm + MaxPooling
- Fully connected head: Dense(256) → Dropout(0.4) → Dense(32, softmax)
- ~2.2M parameters
- Optimizer: Adam (lr=1e-3), loss: sparse categorical cross-entropy
- Early stopping (patience=4) + learning rate reduction on plateau

**Why this approach:**
- Explain briefly why a custom CNN (vs. transfer learning) was chosen as the baseline — e.g., dataset size is sufficient for training from scratch, images are small/simple (64×64 grayscale), and a lightweight model keeps training/deployment cheap — relevant for a real-world low-resource accessibility tool.

**Extension: Live webcam letter-spelling demo**
As an extension beyond the static classification task, the trained model was deployed in a real-time webcam application. MediaPipe's `HandLandmarker` (Google's current hand-tracking model) detects and localizes the user's hand in each video frame; the detected region is cropped, converted to grayscale, resized to 64×64, and fed into the trained CNN exactly as during training. Predicted letters can be manually confirmed (via keypress) to spell out full words one letter at a time — a simple but functional demonstration of how this model could underpin a real accessibility or learning tool, going beyond static offline evaluation.

---

## 4. Implementation Details & Results

*(~3/4 page — fill in once training finishes)*

**Training setup:**
- Framework: TensorFlow/Keras 2.21
- Hardware: trained on CPU (Windows)
- Batch size: 64, ran the full 15 epochs (early stopping patience of 4 was not triggered — validation accuracy kept improving)
- Training time: ~42 minutes total (~160-280s/epoch)

**Results:**
- Final test accuracy: **96.78%**
- Final test loss: **0.1403**
- [Insert training/validation accuracy & loss curves — screenshot from notebook]
- [Insert confusion matrix — screenshot from notebook]
- Per-class performance: every class achieved precision and recall above 0.92. Strongest classes: `ain`, `yaa`, `meem`, `la` (all ≥0.99 precision). Relatively weaker (though still strong) classes: `ta` (0.924 precision), `zay` (0.923 precision), `gaaf` (0.927 precision), `fa` (0.933 precision) — macro and weighted averages both landed at 0.968.

**Sample predictions:**
- [Insert screenshot of the correct/incorrect prediction grid from the notebook]
- Of 9 random test samples visualized, 7 were correctly classified. The 2 errors were `haa`→predicted `khaa` and `jeem`→predicted `dal` — both are letters with some visual similarity in hand shape/angle. Notably, neither pair shows up as a major systematic confusion cluster in the full confusion matrix, suggesting these were isolated per-image mistakes (e.g., due to hand angle or motion blur in that specific photo) rather than a structural weakness in the model.

**Live webcam demo evaluation:**

Beyond the offline test set, the model was evaluated live via the MediaPipe-based webcam extension, testing all 32 letters under controlled conditions (bright, even lighting; hand held at arm's length from the camera — conditions found to be necessary for reliable results). All 32/32 letters (100%) were correctly identified as the model's top-1 prediction, though reliability and confidence varied by letter:

| Reliability tier | Count | Letters |
|---|---|---|
| Immediately reliable (consistently high confidence, no adjustment needed) | 23 | aleff, bb, jeem, ha, haa, khaa, dal, thal, ra, sheen, saad, ta, dha, ain, ghain, kaaf, laam, meem, nun, ya, toot, al, la, yaa |
| Shaky at first, then stable (~98-100%) once correct hand posture was found | 5 | zay, seen, fa, ha, waw |
| Persistently variable confidence even with correct posture | 4 | taa, thaa, dhad, gaaf |

For the four persistently variable letters, confidence fluctuated noticeably across repeated attempts even once a seemingly-correct posture was found:
- `taa`: 78%, 81%, 92%, 93%
- `thaa`: 78%, 82%, 83%, 85%
- `dhad`: 54%, 64%, 75%, 84%, 96%
- `gaaf`: 51%, 68%, 68%, 69%

While the model always still landed on the correct top-1 prediction for these four, the confidence swings indicate the live classification is noticeably less stable for these letters than for the other 28.

---

## 5. Discussion & Analysis

*(~1/2 page)*

**Points to cover:**
- The 96.78% test accuracy is in line with published benchmarks on ArSL2018 — reported CNN results on this dataset in the literature typically fall in the 94-99% range on similar internal (non-signer-independent) splits, so this result is competitive with existing work.
- The confusion matrix is strongly diagonal with very little systematic confusion between specific letter pairs — a positive sign that the class-weighting strategy successfully addressed the mild class imbalance without introducing new biases.
- The handful of individual errors observed (e.g., `haa`/`khaa`, `jeem`/`dal`) involve letters with visually similar hand shapes, which is an intuitive and explainable source of error rather than a sign of a flawed model.
- **Live webcam results validate the pipeline while surfacing a real, honest domain gap.** All 32 letters were eventually recognized correctly (100% top-1), confirming that the trained model generalizes beyond the studio-style dataset when conditions are favorable (bright, even lighting; consistent hand-to-camera distance). However, live conditions clearly matter: performance was only reliable under controlled lighting and framing, and 9 of 32 letters required some trial-and-error to find a hand posture the model recognized confidently — a gap the static test accuracy alone does not reveal.
- **Cross-referencing live and offline weaknesses strengthens the analysis.** Two of the four letters that were persistently unstable live — `gaaf` (51-69% confidence) and `fa` (needed posture adjustment before stabilizing) — were *also* among the four lowest-precision classes on the static test set (`gaaf`: 0.927, `fa`: 0.933, vs. a 0.968 average). This agreement across two independent evaluations (offline test set and live webcam) is stronger evidence that these specific hand-shapes are genuinely harder for the model to distinguish — plausibly due to visual similarity with neighboring letters in ArSL — rather than an artifact of either evaluation method alone.
- **`dhad` is an instructive counter-example.** It scored strongly on the static test set (0.976 precision, among the better-performing classes) yet was the *most* erratic letter live (54-96% confidence swings). This mismatch suggests the live instability for `dhad` is not primarily a model weakness, but more likely reflects a hand-shape that is physically harder for a human signer to hold consistently in front of a camera, or one more sensitive to small variations in hand angle/framing — a distinction that would not be visible from static test-set metrics alone, and illustrates why live testing was a valuable addition to this project rather than a redundant check.
- An important caveat: this internal test split is drawn from the *same* 40 signers and consistent studio-style backgrounds as the training data. Real-world/live-camera performance is a genuine train/deployment domain gap — a new signer (the report author), unconstrained lighting, and a live camera feed the model never saw during training.
- Limitations:
  - Dataset is not Lebanon-specific and was collected in Saudi Arabia with only 40 signers — may not generalize well to different signing styles, camera setups, or lighting in a real deployment
  - Static image classification doesn't capture continuous/dynamic signing
  - Small 64×64 resolution may limit fine-grained hand detail
  - Live performance is conditions-dependent: reliable results required bright, even lighting and a consistent arm's-length distance from the camera — a real deployment would need to handle a wider range of conditions than tested here
- Future work: cross-dataset testing, signer-independent evaluation, expanding to words/phrases, collecting Lebanon-specific ArSL data, and testing live robustness across a wider range of lighting/distance/background conditions than the controlled setup used here

---

## 6. Reflection on Learnings

*(~1/4 - 1/2 page)*

**Points to cover (write this based on your actual experience):**
- What was the most rewarding part of this project?
- What was the most challenging part, and how did you address it? (e.g., environment/package setup issues, understanding class imbalance, interpreting the confusion matrix)
- What did you learn technically (e.g., building a `tf.data` pipeline, handling class imbalance, evaluating multi-class classifiers)?
- What did you learn about the problem domain / accessibility considerations?
- If you had more time, what would you do differently or explore further?

---

## Submission Checklist

- [ ] Code pushed to GitHub (public or shared repo link)
- [ ] Report finalized as PDF/Word doc, 2-4 pages
- [ ] 3-minute video recorded (plan → execution → results demo)
- [ ] All submitted via the Google Form by **August 20**
