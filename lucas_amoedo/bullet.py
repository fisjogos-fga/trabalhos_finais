class Bullet:
    def __init__(self, body, shape, tick):
        self.body = body
        self.shape = shape
        self.tick = tick
        self.body.reference = self
