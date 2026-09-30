# 🔌 How to Extend and Add New Models

This guide shows how to plug new Detection, Preprocessing, or Embedding models into the system without breaking existing functionality, thanks to the **Hierarchical Service Pattern** and **Factory Pattern**.

---

## 🎯 Adding a New Face Detector (e.g., SCRFD or RetinaFace)

To add a new detector backend (e.g., `SCRFDDetectionService`):

### Step 1: Subclass `BaseFaceDetectionService`
Create `src/services/detection/scrfd_service.py`:

```python
from pathlib import Path
from typing import List, Union
import numpy as np

from src.services.base import BaseFaceDetectionService
from src.services.codec import ImageCodecService
from src.schemas.response_schemas import FaceDetectionDTO, BoundingBoxDTO, KeypointDTO

class SCRFDDetectionService(BaseFaceDetectionService):
    def __init__(self, model_path: str = "models/scrfd.onnx", min_confidence: float = 0.5):
        self._model_path = Path(model_path)
        self.min_confidence = min_confidence
        # Load your SCRFD ONNX / PyTorch session here...

    @property
    def model_name(self) -> str:
        return "SCRFD 10G KPS"

    def detect(self, image_input: Union[bytes, str, Path, np.ndarray]) -> List[FaceDetectionDTO]:
        img_bgr = ImageCodecService.decode(image_input)
        
        # 1. Run inference...
        # 2. Extract bounding boxes & keypoints...
        
        return [
            FaceDetectionDTO(
                bbox=BoundingBoxDTO(origin_x=100, origin_y=120, width=200, height=200),
                confidence=0.98,
                keypoints=[KeypointDTO(name="left_eye", x=130, y=160), ...]
            )
        ]
```

### Step 2: Register in `DetectionServiceFactory`
In `src/services/detection/factory.py`:

```python
from src.services.detection.scrfd_service import SCRFDDetectionService

DetectionServiceFactory.register("scrfd", SCRFDDetectionService)
```

### Step 3: Switch via Config
Set in `src/config.py` or terminal:
```bash
export DETECTION_BACKBONE="scrfd"
```

---

## 🧠 Adding a New Recognition Embedding Model (e.g., AdaFace or FaceNet)

### Step 1: Subclass `BaseFaceEmbeddingService`
Create `src/services/embedding/adaface_service.py`:

```python
from pathlib import Path
from typing import Union
import numpy as np

from src.services.base import BaseFaceEmbeddingService

class AdaFaceEmbeddingService(BaseFaceEmbeddingService):
    def __init__(self, model_path: str = "models/adaface_ir50.onnx"):
        self._model_path = Path(model_path)
        # Load AdaFace ONNX Session...

    @property
    def model_name(self) -> str:
        return "AdaFace (IR-50)"

    @property
    def embedding_dim(self) -> int:
        return 512

    def extract(self, tensor: np.ndarray, normalize: bool = True) -> np.ndarray:
        # Run inference -> return 512-D float32 array
        feat = self.session.run(...)[0][0]
        if normalize:
            feat = feat / np.linalg.norm(feat)
        return feat

    def extract_batch(self, batch_tensor: np.ndarray, normalize: bool = True) -> np.ndarray:
        feats = self.session.run(...)[0]
        if normalize:
            feats = feats / np.linalg.norm(feats, axis=1, keepdims=True)
        return feats
```

### Step 2: Register in `EmbeddingServiceFactory`
In `src/services/embedding/factory.py`:

```python
from src.services.embedding.adaface_service import AdaFaceEmbeddingService

EmbeddingServiceFactory.register("adaface", AdaFaceEmbeddingService)
```

### Step 3: Switch via Config
```bash
export EMBEDDING_BACKBONE="adaface"
```

---

## 📐 Adding a New Preprocessing Strategy

### Step 1: Subclass `BaseFacePreprocessingService`
Create your custom preprocessor in `src/services/preprocessing/` and implement:
- `align_and_crop(image_bgr, detection) -> np.ndarray`
- `normalize_tensor(face_bgr) -> np.ndarray`
- `target_size` property

### Step 2: Register in `PreprocessingServiceFactory`
```python
PreprocessingServiceFactory.register("my_custom_align", MyCustomPreprocessingService)
```
