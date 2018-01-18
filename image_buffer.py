import io
import imageio


class ImageBuffer:
    def __init__(self, capacity=5):
        self.capacity = capacity
        self.queue = []

    def append(self, image):
        if len(self.queue) >= self.capacity:
            self.queue.pop(0)
        self.queue.append(image)

    def movie(self):
        movie_f = '/tmp/video.mp4'
        writer = imageio.get_writer(movie_f, fps=5)
        for im in self.queue:
            writer.append_data(im)
        writer.close()
        with open(movie_f, 'rb') as f:
            movie = io.BytesIO(f.read())
        return movie
