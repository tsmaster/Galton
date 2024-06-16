import math

from physics import TIME_STEP

class Ball:
    def __init__(self, radius, x, y):
        self.radius = radius
        self.pos = (x,y)
        self.prev_pos = (x, y)

    def apply_force(self, dt, fx, fy):
        dvx = fx * dt
        dvy = fy * dt

        dx = self.pos[0] - self.prev_pos[0] + fx * TIME_STEP * TIME_STEP
        dy = self.pos[1] - self.prev_pos[1] + fy * TIME_STEP * TIME_STEP

        self.prev_pos = self.pos
        self.pos = (self.pos[0] + dx,
                    self.pos[1] + dy)

    def calc_velocity(self): # returns in units/second
        dx = self.pos[0] - self.prev_pos[0]
        dy = self.pos[1] - self.prev_pos[1]

        vx = dx / TIME_STEP
        vy = dy / TIME_STEP

        return (vx, vy)

    def calc_speed(self): # returns in units/second
        vx, vy = self.calc_velocity()
        return math.sqrt(vx * vx + vy * vy)

    def constrain_at_radius(self, r, pos):
        old_vel = self.calc_velocity()
        old_speed = math.sqrt(old_vel[0]*old_vel[0] + old_vel[1]*old_vel[1]) # units/second
        
        cx, cy = pos
        dx = self.pos[0] - cx
        dy = self.pos[1] - cy

        a = math.atan2(dy, dx)

        new_x = cx + math.cos(a) * r
        new_y = cy + math.sin(a) * r

        self.pos = (new_x, new_y)

        out_vx = old_speed * math.cos(a) # pixels per second
        out_dx = out_vx * TIME_STEP
        out_vy = old_speed * math.sin(a) # pixels per second
        out_dy = out_vy * TIME_STEP
        
        self.prev_pos = ((new_x - out_dx),
                         (new_y - out_dy))
        
