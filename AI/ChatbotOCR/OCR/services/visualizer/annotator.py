"""Visual annotation service for drawing OCR bounding boxes and text labels."""

from typing import List, Any, Optional
import cv2
import numpy as np


class OCRVisualizerService:
    """Draws detected polygons, bounding boxes, and recognized text labels onto images."""

    @classmethod
    def draw_annotations(
        cls,
        image: np.ndarray,
        ocr_items: List[Any],
        draw_polygon: bool = True,
        draw_text: bool = True,
        draw_confidence: bool = True,
        color_rgb: tuple = (0, 180, 255),  # Yellow-orange in RGB -> (255, 180, 0) BGR
    ) -> np.ndarray:
        """Renders bounding polygons and recognized text tags onto an image copy.

        Args:
            image: Original BGR image as numpy array.
            ocr_items: List of objects or dicts containing 'polygon' or 'box_2d', 'text', 'confidence'.
            draw_polygon: Whether to draw bounding polygon outlines.
            draw_text: Whether to draw text labels.
            draw_confidence: Whether to include confidence score in text label.
            color_rgb: Primary color tuple for bounding boxes.

        Returns:
            np.ndarray: Annotated BGR image.
        """
        if image is None or image.size == 0:
            return image

        annotated = image.copy()
        bgr_color = (color_rgb[2], color_rgb[1], color_rgb[0])  # Convert to BGR
        h_img, w_img = annotated.shape[:2]

        for item in ocr_items:
            # Extract fields
            text = getattr(item, "text", None) if hasattr(item, "text") else item.get("text", "")
            confidence = getattr(item, "confidence", 1.0) if hasattr(item, "confidence") else item.get("confidence", 1.0)
            polygon = getattr(item, "polygon", None) if hasattr(item, "polygon") else item.get("polygon", None)
            box_2d = getattr(item, "box_2d", None) if hasattr(item, "box_2d") else item.get("box_2d", None)

            # Draw polygon or box
            if draw_polygon and polygon and len(polygon) >= 3:
                pts = np.array(polygon, np.int32).reshape((-1, 1, 2))
                cv2.polylines(annotated, [pts], isClosed=True, color=bgr_color, thickness=2)
            elif box_2d and len(box_2d) == 4:
                xmin, ymin, xmax, ymax = box_2d
                cv2.rectangle(annotated, (xmin, ymin), (xmax, ymax), bgr_color, 2)

            # Draw text label banner
            if draw_text and text:
                label = f"{text} ({confidence:.2f})" if draw_confidence else text
                
                # Determine anchor point for text label
                if polygon and len(polygon) > 0:
                    anchor_x = int(polygon[0][0])
                    anchor_y = int(polygon[0][1])
                elif box_2d and len(box_2d) == 4:
                    anchor_x, anchor_y = int(box_2d[0]), int(box_2d[1])
                else:
                    continue

                font_scale = max(0.4, min(0.7, w_img / 1200.0))
                thickness = 1
                (text_w, text_h), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
                )

                # Clamp banner coordinates
                bg_y1 = max(0, anchor_y - text_h - 6)
                bg_y2 = max(text_h + 6, anchor_y)
                bg_x1 = max(0, anchor_x)
                bg_x2 = min(w_img, anchor_x + text_w + 6)

                # Draw label background tag
                cv2.rectangle(
                    annotated,
                    (bg_x1, bg_y1),
                    (bg_x2, bg_y2),
                    bgr_color,
                    cv2.FILLED,
                )

                # Draw black text over colored tag
                cv2.putText(
                    annotated,
                    label,
                    (bg_x1 + 3, bg_y2 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale,
                    (0, 0, 0),
                    thickness,
                    lineType=cv2.LINE_AA,
                )

        return annotated
