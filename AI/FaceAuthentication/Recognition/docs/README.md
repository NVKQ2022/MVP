# 📚 Face Authentication & Recognition Documentation

Welcome to the documentation suite for the Face Detection & ArcFace Recognition Service.

---

## 📑 Documentation Index

1. **[Getting Started Guide](file:///home/quan/projects/maivenpoint/AI/FaceAuthentication/Recognition/docs/GETTING_STARTED.md)**
   - Setup, installation, model downloading, running the API server, running the demo, and CLI commands.

2. **[System Architecture & Design](file:///home/quan/projects/maivenpoint/AI/FaceAuthentication/Recognition/docs/ARCHITECTURE.md)**
   - Layered architecture, Service Class Pattern, Base interfaces, Factory Pattern, Dependency Inversion.

3. **[Pipeline Explained Step-by-Step](file:///home/quan/projects/maivenpoint/AI/FaceAuthentication/Recognition/docs/PIPELINE_EXPLAINED.md)**
   - Technical walkthrough of the 4 stages: BlazeFace Detection $\rightarrow$ 4-Point Affine Alignment $\rightarrow$ Preprocessing $\rightarrow$ ArcFace Embedding & Cosine Similarity.

4. **[REST API Reference](file:///home/quan/projects/maivenpoint/AI/FaceAuthentication/Recognition/docs/API_REFERENCE.md)**
   - Complete endpoint specifications, Base64 JSON and Multipart request payloads, response schemas, and cURL examples.

5. **[Extending & Adding New Models](file:///home/quan/projects/maivenpoint/AI/FaceAuthentication/Recognition/docs/EXTENDING_MODELS.md)**
   - Step-by-step developer tutorial on subclassing base interfaces and plugging in new detection and embedding backends via Factories.

6. **[Accuracy Analysis & Improvement Roadmap](file:///home/quan/projects/maivenpoint/AI/FaceAuthentication/Recognition/docs/IMPROVEMENTS.md)**
   - Root-cause analysis of accuracy variance and difficulty-ordered solutions for production upgrades.
