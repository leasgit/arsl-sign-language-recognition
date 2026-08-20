# Arabic Sign Language (ArSL) Letter Recognition
### AI for Lebanon — Education & Accessibility

---

## 1. Project Title & Abstract

**Title:** Arabic Sign Language Letter Recognition: A CNN-Based Accessibility Tool for Deaf and Hard-of-Hearing Learners in Lebanon

Deaf and hard-of-hearing individuals in Lebanon and the wider Arabic-speaking world face limited access to digital tools for learning Arabic Sign Language (ArSL). This project trains a convolutional neural network (CNN) to classify hand-sign images into 32 Arabic alphabet letters, using the publicly available ArSL2018 dataset (54,049 images, 40 signers). The model achieves 96.78% test accuracy after training with class-weighted loss and data augmentation to address class imbalance, with every class individually achieving over 0.92 precision and recall. The model was further deployed in a live webcam demo using MediaPipe hand detection, correctly identifying all 32 letters (100% top-1) under controlled lighting conditions, though 9 letters required posture adjustment and 4 showed persistently variable confidence. Such findings both validate the model's real-world applicability and show a domain gap between studio-quality training data and live deployment. This work demonstrates the feasibility of a lightweight, low-cost recognition system that could universalize accessible learning apps for ArSL students in Lebanon and beyond.

---

## 2. Introduction & Problem Statement

The problem: Deaf and hard-of-hearing individuals in Lebanon have limited access to tools for learning/practicing Arabic Sign Language, compared to resources available for other sign languages (e.g., ASL).

Its significance/who benefits: 
-	Deaf and hard-of-hearing individuals and their families
-	Educators and schools serving deaf students in Lebanon
-	Broader Arabic-speaking deaf community (dataset isn't Lebanon-specific, but the accessibility problem is regionally shared)
  
Core goal of the project: Build and evaluate a CNN that can automatically recognize ArSL alphabet hand-signs from images, as a technical foundation for an accessible learning or communication tool.

---

## 3. Methodology (Approach / Reproduction Details)

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
- Custom CNN: 3 convolutional blocks (32 -> 64 -> 128 filters), each with BatchNorm + MaxPooling
- Fully connected head: Dense(256) -> Dropout(0.4) -> Dense(32, softmax)
- ~2.2M parameters
- Optimizer: Adam (lr=1e-3), loss: sparse categorical cross-entropy
- Early stopping (patience=4) + learning rate reduction on plateau

**Why this approach:**
Dataset size is sufficient for training from scratch since images are small/simple (64×64 grayscale). Moreover, a lightweight model keeps training/deployment cheap, which is relevant for a real-world low-resource accessibility tool.

**Extension: Live webcam letter-spelling demo**
As an extension beyond the classification task, the trained model was deployed in a real-time webcam application. MediaPipe's `HandLandmarker` (Google's current hand-tracking model) detects and localizes the user's hand in each video frame; the detected region is cropped, converted to grayscale, resized to 64×64, and fed into the trained CNN exactly as during training. Predicted letters can be manually confirmed (via keypress SPACE) to spell out full words one letter at a time.

---

## 4. Implementation Details & Results

**Training setup:**
- Framework: TensorFlow/Keras 2.21
- Hardware: trained on CPU (Windows)
- Batch size: 64, ran the full 15 epochs (early stopping patience of 4 was not triggered and validation accuracy kept improving)
- Training time: ~42 minutes total (~160-280s/epoch)

**Results:**
- Final test accuracy: **96.78%**
- Final test loss: **0.1403**
- <img width="1316" height="419" alt="image" src="https://github.com/user-attachments/assets/97175a28-3358-46db-8fe3-2e1427a609f3" />

- <img width="1350" height="1237" alt="image" src="https://github.com/user-attachments/assets/2ff26575-a103-441f-9d45-34386d016bfe" />

- Per-class performance: every class achieved precision and recall above 0.92. Strongest classes: `ain`, `yaa`, `meem`, `la` (all ≥0.99 precision). Relatively weaker (though still strong) classes: `ta` (0.924 precision), `zay` (0.923 precision), `gaaf` (0.927 precision), `fa` (0.933 precision). macro and weighted averages both landed at 0.968.

**Sample predictions:**
- <img width="1322" height="1366" alt="image" src="https://github.com/user-attachments/assets/4dc45db6-a53d-4ceb-a945-3967f7c8431c" />
- Of 9 random test samples visualized, 7 were correctly classified. The 2 errors were `haa`→predicted `khaa` and `jeem`→predicted `dal` , both are letters with some visual similarity in hand shape/angle. Notably, neither pair shows up as a major systematic confusion cluster in the full confusion matrix, suggesting these were isolated per-image mistakes (e.g. due to hand angle or motion blur in that specific photo) rather than a structural weakness in the model.

**Live webcam demo evaluation:**

Beyond the offline test set, the model was evaluated live via the MediaPipe-based webcam extension, testing all 32 letters under controlled conditions (bright, even lighting; hand held at arm's length from the camera - conditions found to be necessary for reliable results). All 32/32 letters (100%) were correctly identified as the model's top-1 prediction, though reliability and confidence varied by letter:

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

While the model always still landed on the correct top-1 prediction for these four, the confidence swings indicate the live classification is noticeably less stable for these letters.

---

## 5. Discussion & Analysis

The confusion matrix is strongly diagonal with minimal systematic confusion between letters, indicating the class-weighting strategy successfully addressed the mild class imbalance without introducing new biases. The few individual errors observed (e.g., haa/khaa, jeem/dal) involve visually similar hand shapes which may be the source of error rather than a flaw in the model.

Live webcam testing validated the model beyond the studio-style dataset: all 32 letters were eventually recognized correctly (100% top-1) under bright, even lighting and consistent camera distance at arm's length. However, 9 of 32 letters required posture adjustment before stabilizing, and 4 (taa, thaa, dhad, gaaf) showed persistent confidence fluctuation even after finding the right posture.

Cross-referencing the two evaluations strengthens the analysis. gaaf and fa were weak in both the static test set (0.927 and 0.933 precision, the two lowest of all classes) and live testing, which is evidence that these specific hand-shapes are genuinely harder for the model to distinguish, likely due to visual similarity with neighboring letters. dhad is an instructive counter-example: strong on the static test set (0.976 precision) but the most erratic letter live (54-96% confidence swings), suggesting this instability is caused by a hand-shape that's physically harder for a human to hold consistently in front of a camera, rather than a model weakness.

Limitations: the test split shares the same 40 signers and studio backgrounds as training, so live performance reflects a genuine train/deployment domain gap. The task is limited to static alphabet recognition, not continuous/dynamic signing, and 64×64 resolution may limit fine-grained detail. Live performance is conditions-dependent — reliable results required bright, even lighting and arm's-length distance from the camera.

Future work: cross-dataset and signer-independent evaluation, expanding to words/phrases, collecting Lebanon-specific ArSL data, and testing robustness across a wider range of real-world lighting and distance conditions.

---

## 6. Reflection on Learnings

The most rewarding part of this project was getting the live webcam demo working end-to-end. Watching the model correctly recognize hand-signs in real time, after offline evaluation, made the project feel like a real, usable tool rather than just a set of accuracy numbers.

The most challenging part was debugging the webcam pipeline, since problems there weren't visible in the code itself. They only showed up as wrong predictions with no error messages. I worked through this systematically: printing the model's full top-5 confidence ranking (not just its top guess) and saving the exact cropped image the model was actually seeing let me diagnose several distinct issues one at a time. Some issues I encountered include: a mirrored camera feed that fed the model wrong-orientation hands, a non-square crop that distorted the hand shape on resize, landmark-tracking drift that occasionally produced a bounding box covering my whole upper body, and even a small typo that zeroed out a safety threshold (I embarrassingly spent more time on this one than I'd like to admit). 

Technically, I learned how to build a full tf.data pipeline with augmentation, how to diagnose and correct for class imbalance using weighted loss, and how to evaluate a multi-class classifier properly. I also learned that offline test accuracy and real-world performance are different things that need to be measured separately, since a model can excel on one and be shakier on the other for reasons the test set alone can't reveal. That gap between benchmark performance and real deployment conditions is an important part of building usable accessibility technology.
