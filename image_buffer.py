import io
import imageio


def compress_jpeg(image):
    i = io.BytesIO()
    imageio.imwrite(i, image, format='JPG', quality=50, optimize=True)
    i.seek(0)
    return imageio.imread(i)


class ImageBuffer:
    def __init__(self, capacity=5):
        self.capacity = capacity
        self.queue = []

    def append(self, image):
        if len(self.queue) >= self.capacity:
            self.queue.pop(0)
        compressed = compress_jpeg(image)
        self.queue.append(compressed)

    def gif(self):
        gif = io.BytesIO()
        imageio.mimwrite(gif, self.queue, format="GIF", duration=0.5)
        gif.seek(0)
        return gif
