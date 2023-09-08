from PIL import Image


class ImageCache:
    def __init__(self):
        self.cache: dict[str, Image.Image] = {}

    def load_image(self, path: str) -> Image.Image:
        image = self.cache.get(path)
        if image is None:
            print(f"[CACHE] {path} not yet cached. Caching now...")
            image = self.cache[path] = Image.open(f"images\\{path}")
        return image
