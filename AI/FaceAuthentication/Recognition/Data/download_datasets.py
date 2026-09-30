"""
Automated downloader utility to fetch lightweight sample datasets for:
- Detection (single face, multi-face)
- Recognition (sample gallery identities)
- Anti_Spoofing (real faces, 2D print & screen replay spoof attacks)
"""

import os
import urllib.request
from pathlib import Path
from tqdm import tqdm

DATA_DIR = Path(__file__).resolve().parent

DETECTION_DIR = DATA_DIR / "Detection"
RECOGNITION_DIR = DATA_DIR / "Recognition"
ANTISPOOFING_DIR = DATA_DIR / "Anti_Spoofing"

# Sample lightweight benchmark images (~800 KB total)
SAMPLE_DATASETS = [
    # 1. Detection Samples
    {
        "url": "https://raw.githubusercontent.com/opencv/opencv/5.x/samples/data/lena.jpg",
        "target": DETECTION_DIR / "single_face" / "single_face_1.jpg",
        "description": "Detection Single Face (Lena portrait)",
    },
    {
        "url": "https://raw.githubusercontent.com/ageitgey/face_recognition/master/examples/two_people.jpg",
        "target": DETECTION_DIR / "multi_face" / "multi_face_1.jpg",
        "description": "Detection Multi Face (Two people benchmark)",
    },
    # 2. Anti-Spoofing Samples (from minivision-ai/Silent-Face-Anti-Spoofing)
    {
        "url": "https://raw.githubusercontent.com/minivision-ai/Silent-Face-Anti-Spoofing/master/images/sample/image_T1.jpg",
        "target": ANTISPOOFING_DIR / "real" / "real_1.jpg",
        "description": "Anti-Spoofing Genuine Face (Live sample)",
    },
    {
        "url": "https://raw.githubusercontent.com/minivision-ai/Silent-Face-Anti-Spoofing/master/images/sample/image_F1.jpg",
        "target": ANTISPOOFING_DIR / "spoof" / "spoof_replay_1.jpg",
        "description": "Anti-Spoofing Attack (Screen Replay sample 1)",
    },
    {
        "url": "https://raw.githubusercontent.com/minivision-ai/Silent-Face-Anti-Spoofing/master/images/sample/image_F2.jpg",
        "target": ANTISPOOFING_DIR / "spoof" / "spoof_replay_2.jpg",
        "description": "Anti-Spoofing Attack (Screen Replay sample 2)",
    },
]


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_file(url: str, target_path: Path, desc: str = ""):
    target_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with DownloadProgressBar(unit="B", unit_scale=True, miniters=1, desc=desc or target_path.name) as t:
        with urllib.request.urlopen(req) as resp, open(target_path, "wb") as f:
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                f.write(chunk)
                t.update(len(chunk))


def ensure_placeholders():
    """Ensures .gitkeep placeholders exist in all dataset split directories."""
    directories = [
        DETECTION_DIR,
        DETECTION_DIR / "single_face",
        DETECTION_DIR / "multi_face",
        RECOGNITION_DIR,
        RECOGNITION_DIR / "duke",
        RECOGNITION_DIR / "kyle",
        RECOGNITION_DIR / "leon",
        ANTISPOOFING_DIR,
        ANTISPOOFING_DIR / "real",
        ANTISPOOFING_DIR / "spoof",
    ]
    for d in directories:
        d.mkdir(parents=True, exist_ok=True)
        gitkeep = d / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()


def ensure_datasets():
    """Checks and downloads sample datasets if missing."""
    ensure_placeholders()

    print("Checking dataset splits...")
    for item in SAMPLE_DATASETS:
        target = item["target"]
        if not target.exists():
            print(f"Downloading {item['description']} -> {target.name}...")
            try:
                download_file(item["url"], target, desc=target.name)
                print(f"  {target.name} downloaded successfully.")
            except Exception as e:
                print(f"  [Warning] Failed to download {item['url']}: {e}")
        else:
            print(f"   {item['description']} exists: {target.name}")

    print("\nDataset split status:")
    print(f"  Detection:      {len(list(DETECTION_DIR.glob('*/*.jpg')))} images")
    print(f"  Recognition:    {len(list(RECOGNITION_DIR.glob('*/*.jpg')))} images")
    print(f"  Anti_Spoofing:  {len(list(ANTISPOOFING_DIR.glob('*/*.jpg')))} images")


if __name__ == "__main__":
    ensure_datasets()
