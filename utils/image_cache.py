import cv2
import numpy as np
import pickle
from .logger import logger
import os


class ImageCache:
    def __init__(self):
        self.cache: dict[str, np.ndarray] = {}

    def load_image(self, path: str) -> np.ndarray:
        image = self.cache.get(path)
        if image is None:
            try:
                logger.debug(f"[CACHE] Caching {path}...")
                image = self.cache[path] = cv2.imread(path)
                if image is None:
                    logger.debug(f"[CACHE] Failed to load {path}.")
            except Exception as e:
                logger.debug(f"[CACHE] Error loading {path}: {e}")
        return image

    def save_cache(self, path: str):
        try:
            with open(path, "wb") as f:
                pickle.dump(self.cache, f)
                logger.debug(f"[CACHE] Saved cache to {path}.")
        except Exception as e:
            logger.debug(f"[CACHE] Error saving cache: {e}")

    def load_cache(self, path: str):
        try:
            with open(path, "rb") as f:
                self.cache = pickle.load(f)
                logger.debug(f"[CACHE] Loaded cache from {path}.")
        except Exception as e:
            logger.debug(f"[CACHE] Error loading cache: {e}")

    def initialize_cache(self, directory: str, recursive=True):
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.endswith(".png"):
                    self.load_image(file_path)
