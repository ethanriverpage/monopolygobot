import cv2
import numpy as np


class ImageCache:
    def __init__(self):
        self.cache: dict[str, np.ndarray] = {}

    def load_image(self, path: str) -> np.ndarray:
        image = self.cache.get(path)
        if image is None:
            print(f"[CACHE] {path} not yet cached. Caching now...")
            image = self.cache[path] = cv2.imread(path)
        return image
