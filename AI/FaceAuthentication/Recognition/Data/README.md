# 📂 Project Datasets Organization

This directory organizes facial image datasets into three modular functional splits:

```text
Data/
├── Detection/             # Face Detection evaluation samples
│   ├── single_face/       # Single-face portrait images
│   └── multi_face/        # Multi-person / group photos
├── Recognition/           # Face Recognition & Authentication gallery identities
│   ├── duke/              # Identity 'duke' photos
│   ├── kyle/              # Identity 'kyle' photos
│   └── leon/              # Identity 'leon' photos
├── Anti_Spoofing/         # Face Anti-Spoofing (FAS) & Liveness evaluation samples
│   ├── real/              # Genuine live human face captures
│   └── spoof/             # Presentation attacks (2D print, digital screen replay)
└── download_datasets.py   # Utility script to automatically fetch sample datasets
```

---

## 🔒 Git Policy: Lightweight Placeholders

To keep the git repository lightweight, raw dataset images (`*.jpg`, `*.jpeg`, `*.png`) are ignored by Git. Only folder placeholders (`.gitkeep`) and documentation are tracked in the repository.

### Fetching Sample Images
To download the sample benchmark images (~800 KB total), run:

```bash
python Data/download_datasets.py
```
