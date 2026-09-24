# 📈 Face Recognition Accuracy & Improvement Roadmap

This document analyzes the root causes behind accuracy limitations in baseline face verification pipelines and provides a structured roadmap ordered by difficulty level.

---

## 🔍 Why Baseline Accuracy Fluctuates

1. **6-Landmark BlazeFace vs 5-Point Umeyama Alignment**:
   - ArcFace was pretrained on faces aligned using 5 exact points: Left/Right Eye Centers, Nose Tip, and Left/Right Mouth Corners.
   - BlazeFace estimates mouth as a single center point. This creates spatial tilt/shear on angled faces, dropping cosine similarity by $0.15 - 0.25$.
2. **20MP Image Coordinate Jitter**:
   - $5184 \times 3888$ raw images projected through a $128 \times 128$ internal detector grid suffer from $40 - 50\text{px}$ coordinate quantization jitter.
3. **MobileFaceNet vs ResNet-50 Capacity**:
   - `w600k_mbf.onnx` is MobileFaceNet ($1.2\text{M}$ parameters, $13\text{MB}$). While fast, its representation capacity under shadows and angles is lower than ResNet-50 ($43.6\text{M}$ parameters).

---

## 🛠️ Solutions Ordered by Difficulty Level

| Level | Difficulty | Solution | Expected Impact | Implementation Effort |
| :---: | :---: | :--- | :---: | :---: |
| **1** | 🟢 **Low** | **Test-Time Augmentation (TTA)**: Flip feature fusion ($\mathbf{e}_{\text{orig}} + \mathbf{e}_{\text{flip}}$) | $+2 - 3\%$ intra-sim | 30 mins |
| **1** | 🟢 **Low** | **Multi-Photo Enrollment Centroid**: Register users with 3–5 photos to average out shadow outliers | $+15 - 20\%$ intra-sim | 1 hour |
| **1** | 🟢 **Low** | **Image Pre-scaling**: Downsample $20\text{MP}$ inputs to $1280\text{px}$ before detection to eliminate coordinate jitter | $5\times$ faster detection | 30 mins |
| **2** | 🟡 **Medium** | **High-Precision 5-Point Alignment (MediaPipe FaceMesh)**: Extract exact outer eye and mouth corners | $+5 - 8\%$ accuracy | 3 hours |
| **2** | 🟡 **Medium** | **Face Quality Assessment (FQA)**: Filter out blurry (Laplacian variance $< 50$) or extreme-pose frames ($> 35^\circ$) | Removes bad frames | 2 hours |
| **3** | 🟠 **High** | **Upgrade Backbone to ResNet-50 (`w600k_r50.onnx`)**: $43.6\text{M}$ parameter model | $+10 - 15\%$ robustness | 1 hour |
| **3** | 🟠 **High** | **AdaFace Loss / CurricularFace**: Quality-adaptive angular margin for hard in-the-wild faces | $+1.5 - 3.0\%$ on hard faces | 1 day |
| **3** | 🟠 **High** | **Vector DB Indexing (FAISS)**: Sub-millisecond 1:N gallery matching | Scale to millions | 4 hours |
| **4** | 🔴 **Very High** | **Anti-Spoofing & Liveness Check (FAS)**: MiniFASNet / Silent liveness detection against 2D print & screen attacks | Essential for security | 2–3 days |
| **4** | 🔴 **Very High** | **Domain-Specific Fine-Tuning**: Fine-tune ArcFace on target device camera optics with data augmentation | Sensor calibration | 1–2 weeks |
