import io
import imageio
import requests


class ImageBuffer:
    def __init__(self, capacity=5):
        self.capacity = capacity
        self.queue = []

    def append(self, image):
        if len(self.queue) >= self.capacity:
            self.queue.pop(0)
        self.queue.append(image)


class Camera:
    def __init__(self, address, auth=(), video_length=10):
        self.buffer = ImageBuffer(video_length)
        self.address = address
        self.auth = auth
        for _ in range(video_length):
            self.shot_to_buffer()

    def _take_shot(self):
        r = requests.get(self.address, auth=self.auth)
        return imageio.imread(io.BytesIO(r.content))

    def shot_to_buffer(self):
        img = self._take_shot()
        self.buffer.append(img)

    def movie(self):
        movie_f = '/tmp/video.mp4'
        writer = imageio.get_writer(movie_f, fps=5)
        for im in self.buffer.queue:
            writer.append_data(im)
        writer.close()
        with open(movie_f, 'rb') as f:
            movie = io.BytesIO(f.read())
        return movie
