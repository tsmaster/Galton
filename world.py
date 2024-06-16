import ball
import bumper

class World():
    def __init__(self):
        self.bumpers = []
        self.balls = []

        self.ball_radius = 32
        self.bumper_radius = 48

        self.gravity_x = 0
        self.gravity_y = 100

    def add_ball(self, x, y):
        self.balls.append(ball.Ball(self.ball_radius, x, y))

    def add_bumper(self, x, y, pitch):
        self.bumpers.append(bumper.Bumper(self.bumper_radius, x, y, pitch))

    def cull(self, width, height):
        new_balls = []
        for b in self.balls:
            bx, by = b.pos
            if bx >= 0 and bx <= width and by < height:
                new_balls.append(b)
        self.balls = new_balls
