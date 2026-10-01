"""Reading order sorting utilities for OCR bounding boxes."""

from typing import List, TypeVar, Any, Protocol


class HasBox2D(Protocol):
    box_2d: List[int]


T = TypeVar("T", bound=Any)


class ReadingOrderSorter:
    """Sorts OCR detection boxes into natural top-to-bottom, left-to-right reading order."""

    @staticmethod
    def sort(items: List[T]) -> List[T]:
        """Sorts a list of OCR items based on their 2D bounding boxes.

        Each item must have a `box_2d` attribute or dictionary key formatted as [xmin, ymin, xmax, ymax].
        """
        if not items or len(items) <= 1:
            return list(items)

        def get_box(item: Any) -> List[int]:
            if hasattr(item, "box_2d"):
                return item.box_2d
            if isinstance(item, dict) and "box_2d" in item:
                return item["box_2d"]
            raise AttributeError("Item must have 'box_2d' attribute or key.")

        # Sort primarily by ymin first
        sorted_by_y = sorted(items, key=lambda x: get_box(x)[1])

        # Cluster into lines
        lines: List[List[T]] = []
        current_line: List[T] = [sorted_by_y[0]]

        for item in sorted_by_y[1:]:
            curr_box = get_box(item)
            ref_box = get_box(current_line[-1])

            curr_ymin, curr_ymax = curr_box[1], curr_box[3]
            ref_ymin, ref_ymax = ref_box[1], ref_box[3]

            curr_h = max(curr_ymax - curr_ymin, 1)
            ref_h = max(ref_ymax - ref_ymin, 1)
            avg_h = (curr_h + ref_h) / 2.0

            curr_center_y = (curr_ymin + curr_ymax) / 2.0
            ref_center_y = (ref_ymin + ref_ymax) / 2.0

            # If vertical distance between centers is smaller than threshold fraction of line height,
            # consider them part of the same horizontal text line
            if abs(curr_center_y - ref_center_y) < avg_h * 0.6:
                current_line.append(item)
            else:
                # Sort current line left to right
                lines.append(sorted(current_line, key=lambda x: get_box(x)[0]))
                current_line = [item]

        if current_line:
            lines.append(sorted(current_line, key=lambda x: get_box(x)[0]))

        # Flatten lines
        result: List[T] = []
        for line in lines:
            result.extend(line)

        return result
