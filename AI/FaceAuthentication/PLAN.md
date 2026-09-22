# Face Recognition for Learning Portal

## 1. Project Overview

### Objective

Develop and integrate a face recognition module into the Learning Portal to support face-based user authentication.

The main focus is **Face Recognition**, not the complete authentication system.

The system should be able to:

1. Detect a face from an image or camera frame.
2. Preprocess and align the detected face.
3. Generate a face embedding.
4. Compare the embedding with registered users.
5. Determine whether the face belongs to a registered user.
6. Return the matched user identity and similarity/confidence information.
7. Evaluate the recognition system under different conditions.

### Main Goal

Build a reliable and measurable face recognition pipeline rather than simply integrating an existing face recognition library.

---

# 2. Scope

## 2.1 In Scope

### Core

* Face detection
* Face preprocessing
* Face alignment
* Face embedding extraction
* Face registration
* Face embedding storage
* Face matching
* Similarity calculation
* Recognition threshold
* Unknown-face handling
* API integration
* Basic multi-face handling

### Evaluation

* Recognition accuracy
* FAR (False Acceptance Rate)
* FRR (False Rejection Rate)
* Precision
* Recall
* F1-score
* Recognition latency
* Robustness testing

### Advanced

* Recognition model comparison
* Threshold calibration
* Face quality assessment
* Different lighting conditions
* Different face angles
* Different distances from camera
* Glasses / appearance variation
* CPU/GPU performance comparison if applicable

---

# 3. Out of Scope

The following features should not be part of the main implementation unless there is additional time:

* Complete authentication/authorization system
* Password authentication
* JWT implementation
* User permission management
* Liveness detection
* Anti-spoofing
* Deepfake detection
* Face tracking
* Custom training of a large face recognition model
* Mobile application development
* Attendance management

These can be mentioned as possible future improvements.

---

# 4. System Architecture

The proposed pipeline is:

```text
                Learning Portal
                       |
                       v
                Face Auth API
                       |
                       v
             Face Recognition Service
                       |
        +--------------+--------------+
        |              |              |
        v              v              v
 Face Detection   Preprocessing   Face Quality
        |              |          Assessment
        +--------------+--------------+
                       |
                       v
               Face Embedding
                       |
                       v
                Face Matching
                       |
             +---------+---------+
             |                   |
             v                   v
          Matched             Unknown
             |
             v
           User ID
```

---

# 5. Face Recognition Pipeline

## Step 1 — Face Detection

Input:

```text
Image / Camera Frame
```

Output:

```text
Bounding Box
Facial Landmarks
Detection Confidence
```

Possible approaches:

* RetinaFace
* MTCNN
* YuNet
* OpenCV DNN

The detector should identify the location of the face before recognition.

---

## Step 2 — Face Preprocessing

Perform:

* Face cropping
* Resize
* Pixel normalization
* Face alignment

Example:

```text
Raw Image
    |
    v
Face Detection
    |
    v
Face Crop
    |
    v
Face Alignment
    |
    v
Normalized Face
```

The preprocessing procedure should be consistent between registration and recognition.

---

# 6. Face Embedding

The recognition model converts a face image into a numerical vector.

Example:

```text
Face Image
     |
     v
Recognition Model
     |
     v
Embedding
[0.12, -0.43, 0.81, ..., 0.17]
```

The embedding represents facial characteristics in a vector space.

Possible models:

* ArcFace
* FaceNet
* InsightFace-based models

The model should preferably be used as a pretrained model for the midterm.

---

# 7. Face Registration

When a user registers their face:

```text
User
 |
 v
Capture Face
 |
 v
Detect Face
 |
 v
Preprocess
 |
 v
Generate Embedding
 |
 v
Store Embedding
```

Example database representation:

```text
User
--------------------------------
user_id
name
face_embedding
created_at
```

If multiple enrollment images are used, consider storing multiple embeddings or an aggregated representation.

---

# 8. Face Recognition

During authentication:

```text
Input Image
     |
     v
Face Detection
     |
     v
Preprocessing
     |
     v
Embedding
     |
     v
Compare with Registered Embeddings
     |
     v
Similarity Score
     |
     +----------------------+
     |                      |
     v                      v
Above Threshold        Below Threshold
     |                      |
     v                      v
Matched User             Unknown
```

---

# 9. Similarity Calculation

Use a suitable distance or similarity metric.

For cosine similarity:

```text
                    A · B
similarity(A,B) = ---------
                   ||A|| ||B||
```

For normalized embeddings, cosine similarity can be used to measure how similar two face embeddings are.

Example:

```text
Registered embedding
        |
        | cosine similarity
        v
Input embedding
        |
        v
0.91
```

---

# 10. Threshold Calibration

Do not simply hard-code a threshold such as:

```python
if similarity > 0.8:
```

Instead, evaluate different thresholds.

Example:

```text
0.50
0.55
0.60
0.65
0.70
0.75
0.80
0.85
0.90
0.95
```

For each threshold, calculate:

* True Positive Rate
* False Positive Rate
* FAR
* FRR
* Precision
* Recall
* F1-score

Then determine an appropriate operating threshold based on validation data and the application's requirements.

---

# 11. Model Comparison

One of the strongest possible contributions is comparing different recognition models.

Possible comparison:

```text
Model A
Model B
Model C
```

Evaluate:

| Model   | Accuracy | FAR | FRR | F1 | Latency |
| ------- | -------: | --: | --: | -: | ------: |
| Model A |          |     |     |    |         |
| Model B |          |     |     |    |         |
| Model C |          |     |     |    |         |

The goal is not simply to identify a "winner", but to understand the trade-offs between recognition performance and computational cost.

---

# 12. Robustness Evaluation

Face recognition should be tested under realistic conditions.

## 12.1 Lighting

Test:

* Normal lighting
* Low lighting
* Strong lighting
* Uneven lighting

---

## 12.2 Face Angle

Test:

* Frontal face
* Slight left/right rotation
* Larger yaw angle
* Slight up/down angle

---

## 12.3 Distance

Test:

* Close to camera
* Normal distance
* Far from camera

---

## 12.4 Appearance

Test where applicable:

* Glasses
* Different facial expressions
* Different hairstyles
* Minor appearance changes

Do not intentionally alter or evaluate sensitive personal attributes as a performance criterion.

---

# 13. Face Quality Assessment

An optional advanced feature is to reject poor-quality input before recognition.

Possible quality signals:

* Face size
* Blur
* Brightness
* Detection confidence
* Face pose

Example:

```text
Camera
  |
  v
Face Detection
  |
  v
Quality Assessment
  |
  +---- Poor Quality ----> Ask user to recapture
  |
  v
Good Quality
  |
  v
Face Recognition
```

Example response:

```text
Face quality is too low.
Please move closer to the camera.
```

This can improve the practical usability of the system.

---

# 14. Multi-Face Recognition

The system should define what happens when multiple faces appear.

Example:

```text
Camera Frame
     |
     v
+----+----+----+
| Face | Face | Face |
|  A   |  B   |  C   |
+----+----+----+
   |      |      |
   v      v      v
 User A User B Unknown
```

Possible policies:

* Allow only one face during authentication.
* Reject frames containing multiple faces.
* Recognize every detected face.

For authentication, requiring exactly one face is usually simpler and easier to evaluate.

---

# 15. Performance Evaluation

Measure:

### Recognition latency

```text
Detection latency
+
Preprocessing latency
+
Embedding latency
+
Matching latency
=
Total latency
```

Example:

| Component     | Latency |
| ------------- | ------: |
| Detection     |   XX ms |
| Preprocessing |   XX ms |
| Embedding     |   XX ms |
| Matching      |   XX ms |
| Total         |   XX ms |

Also consider:

* CPU usage
* GPU usage
* RAM/VRAM usage
* Images processed per second

---

# 16. Dataset / Test Set

Create a small controlled evaluation dataset.

For each registered person, collect multiple images rather than relying on only one image.

Example:

```text
Person A
 ├── image_01
 ├── image_02
 ├── image_03
 └── image_04

Person B
 ├── image_01
 ├── image_02
 ├── image_03
 └── image_04
```

Separate data into:

```text
Enrollment Set
        |
        v
Registered Embeddings

Evaluation Set
        |
        v
Recognition Testing
```

Avoid using the exact same image for registration and testing because this can produce an overly optimistic evaluation.

---

# 17. Evaluation Protocol

Define the experiment before running it.

For example:

```text
N users
M enrollment images/user
K test images/user
```

Evaluate:

### Genuine pairs

Same person:

```text
User A ↔ User A
```

### Impostor pairs

Different people:

```text
User A ↔ User B
User A ↔ User C
```

This allows the system to measure both:

```text
Genuine similarity distribution
```

and

```text
Impostor similarity distribution
```

---

# 18. Important Metrics

## False Acceptance Rate

Percentage of impostor attempts incorrectly accepted.

```text
FAR =
False Acceptances
-----------------
Impostor Attempts
```

## False Rejection Rate

Percentage of genuine attempts incorrectly rejected.

```text
FRR =
False Rejections
----------------
Genuine Attempts
```

These metrics are particularly important for authentication-related systems.

---

# 19. Visualization

Create graphs for the final presentation.

Recommended graphs:

### 1. Genuine vs impostor similarity distribution

```text
Similarity
    ^
    |
    |      Genuine
    |     /██████\
    |    /████████\
    |             \     Impostor
    |              \██████
    +---------------------------->
```

### 2. FAR vs threshold

```text
Threshold
    |
FAR |
    |\
    | \
    |  \
    |   \
    |    \________
    +---------------->
```

### 3. FRR vs threshold

### 4. ROC curve

### 5. Model latency comparison

### 6. Recognition performance under different conditions

---

# 20. Recommended Experiments

## Experiment 1 — Baseline

Implement one recognition model.

Measure:

* Accuracy
* FAR
* FRR
* F1
* Latency

---

## Experiment 2 — Model Comparison

Compare two or more models.

Measure:

* Recognition performance
* Embedding dimension
* Inference latency
* Resource consumption

---

## Experiment 3 — Threshold Calibration

Evaluate multiple thresholds.

Find the trade-off between:

```text
Security
    ↕
False Acceptance
    ↕
False Rejection
```

---

## Experiment 4 — Robustness

Evaluate:

* Lighting
* Pose
* Distance
* Appearance variation

---

## Experiment 5 — Performance

Measure:

* Detection time
* Embedding time
* Matching time
* End-to-end latency

---

# 21. API Design

A simple API can be:

```text
POST /face/register
```

Register a user's face.

```text
POST /face/recognize
```

Recognize a face.

Example response:

```json
{
    "user_id": "123",
    "matched": true,
    "similarity": 0.91
}
```

For unknown users:

```json
{
    "user_id": null,
    "matched": false,
    "similarity": 0.52
}
```

The exact API structure should be adapted to the Learning Portal's existing backend.

---

# 22. Suggested Project Structure

```text
face-recognition/
│
├── app/
│   ├── api/
│   │   └── routes.py
│   │
│   ├── detection/
│   │   └── detector.py
│   │
│   ├── preprocessing/
│   │   └── processor.py
│   │
│   ├── recognition/
│   │   ├── model.py
│   │   ├── embedding.py
│   │   └── matcher.py
│   │
│   ├── quality/
│   │   └── quality_checker.py
│   │
│   └── config.py
│
├── experiments/
│   ├── model_comparison.py
│   ├── threshold_calibration.py
│   ├── robustness_test.py
│   └── benchmark.py
│
├── data/
│
├── results/
│
└── README.md
```

---

# 23. Recommended Technology Stack

A possible stack:

```text
Python
│
├── OpenCV
├── PyTorch
├── InsightFace / ArcFace
├── NumPy
├── FastAPI
└── PostgreSQL / existing Learning Portal database
```

The exact stack should depend on the existing Learning Portal architecture.

---

# 24. Minimum Viable Implementation

If time is limited, implement these first:

```text
[1] Face Detection
       ↓
[2] Face Preprocessing
       ↓
[3] Face Embedding
       ↓
[4] Face Registration
       ↓
[5] Face Matching
       ↓
[6] Similarity Threshold
       ↓
[7] Recognition API
```

Then evaluate:

```text
Accuracy
FAR
FRR
Latency
```

This is the minimum acceptable technical scope.

---

# 25. Features That Make the Project Stand Out

Prioritize these after the MVP:

### High Priority

1. Model comparison
2. Threshold calibration
3. FAR/FRR analysis
4. Robustness testing
5. Latency benchmarking

### Medium Priority

6. Face quality assessment
7. Multi-face handling
8. Better visualization
9. Multiple enrollment images

### Low Priority

10. Liveness detection
11. Anti-spoofing
12. Custom model training

Do not sacrifice the evaluation quality just to add more features.

---

# 26. Final Deliverables

## Software

* Face recognition service
* Registration endpoint
* Recognition endpoint
* Embedding storage
* Learning Portal integration
* Basic error handling

## Experiments

* Model comparison
* Threshold experiment
* Robustness experiment
* Performance benchmark

## Documentation

Document:

1. Problem
2. Requirements
3. Architecture
4. Face recognition pipeline
5. Model selection
6. Implementation
7. Dataset
8. Experimental methodology
9. Evaluation metrics
10. Results
11. Failure cases
12. Limitations
13. Future improvements

---

# 27. Suggested Midterm Presentation

A strong presentation flow:

```text
Problem
   ↓
Why Face Recognition?
   ↓
System Architecture
   ↓
Recognition Pipeline
   ↓
Model Selection
   ↓
Implementation
   ↓
Experiment Design
   ↓
Results
   ↓
Failure Cases
   ↓
Learning Portal Integration
   ↓
Limitations & Future Work
```

The most important part should not be the demo alone.

Show:

```text
Implementation
      +
Experimental Evidence
      +
Quantitative Results
```

---

# 28. Target Contribution Statement

The project contribution can be summarized as:

> Developed and integrated an embedding-based face recognition pipeline for a Learning Portal, covering face detection, preprocessing, embedding extraction, identity matching, and threshold-based recognition. The system is evaluated using recognition metrics, FAR/FRR analysis, robustness experiments under different environmental conditions, and inference latency benchmarking.

If model comparison and quality assessment are implemented:

> Additionally, the project investigates the trade-offs between different face recognition models and evaluates the effect of input face quality on recognition performance.

---

# 29. Recommended Priority

Use this priority order:

```text
                    ┌────────────────────┐
                    │ Face Recognition   │
                    │      MVP           │
                    └─────────┬──────────┘
                              │
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
          Detection       Embedding       Matching
               │              │              │
               └──────────────┼──────────────┘
                              ▼
                       Threshold Tuning
                              │
                              ▼
                    Quantitative Evaluation
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
        Model Comparison   Robustness       Benchmark
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                       Learning Portal
                          Integration
```

The key principle is:

**Build a small, complete recognition system first. Then spend the remaining time proving how well it works.**
