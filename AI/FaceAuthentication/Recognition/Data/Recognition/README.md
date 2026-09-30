# 👤 Face Recognition & Identification Gallery Split

Contains identity-segregated directories for 1:1 Face Verification and 1:N Identification workflows.

## Subdirectories:
- Each subdirectory represents a unique identity subject (e.g. `duke/`, `kyle/`, `leon/`).
- Inside each subject directory, place multiple facial images of the person under varying poses, lighting, and expressions.
- The `FaceRecognitionService.enroll()` method averages embeddings from multiple images to form a robust centroid template representation.
