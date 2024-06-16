import threading
import sys
import math
import random

import pygame
import scamp

import world
import physics
import bdgmath
import collisionrec

WIDTH,HEIGHT = 1200, 1200

def makeCircleSurface(radius, colorRGB):
    diameter = int(2*radius)
    r_squared = radius*radius
    new_surface = pygame.Surface((diameter, diameter), flags = pygame.SRCALPHA)

    new_surface.fill((0, 0, 0, 0))

    for x in range(diameter):
        dx = radius - x
        dx_squared = dx * dx
        for y in range(diameter):
            dy = radius - y
            dy_squared = dy*dy
            if dx_squared + dy_squared < r_squared:
                new_surface.set_at((x, y), colorRGB)

    return new_surface

ball_img = makeCircleSurface(32, (255, 0, 0))
bumper_img = makeCircleSurface(48, (64, 96, 192))

def update(dt, w):
    collisions = []
    
    for b_idx, b in enumerate(w.balls):
        b.apply_force(dt, w.gravity_x, w.gravity_y)

        r2 = 4 * b.radius * b.radius

        for ob_idx, ob in enumerate(w.balls):
            if b_idx == ob_idx:
                continue
            dx = b.pos[0] - ob.pos[0]
            dy = b.pos[1] - ob.pos[1]
            if dx*dx + dy*dy < r2:
                # TODO better force
                b.constrain_at_radius(2*b.radius, ob.pos)
                new_col_rec = collisionrec.CollisionRecord(
                    collisionrec.INST_CLARINET,
                    60,
                    1.0)
                collisions.append(new_col_rec)

        for bump in w.bumpers:
            dx = b.pos[0] - bump.pos[0]
            dy = b.pos[1] - bump.pos[1]

            test_dist = b.radius + bump.radius * 1.1
            td2 = test_dist * test_dist
            
            if dx * dx + dy * dy < td2:
                # TODO better force, constrain
                #print("old ball pos:", b.pos)
                #print("bumper pos:", bump.pos)
                #print("dist before:", math.sqrt(dx * dx + dy * dy))
                spd = b.calc_speed()
                #print("ball bumper coll speed:", spd)
                b.constrain_at_radius(test_dist, bump.pos)

                norm_spd = bdgmath.bdg_map(spd, 0, 400, 0, 1)

                ndx = b.pos[0] - bump.pos[0]
                ndy = b.pos[1] - bump.pos[1]
                #print("new ball pos", b.pos)
                #print("new ball dist", math.sqrt(ndx * ndx + ndy * ndy))
                new_col_rec = collisionrec.CollisionRecord(
                    collisionrec.INST_PIANO,
                    bump.pitch,
                    norm_spd)
                collisions.append(new_col_rec)
    return collisions

        

def draw(screen, w):
    screen.fill((0, 0, 0))

    for b in w.bumpers:
        
        screen.blit(bumper_img, (b.pos[0]-b.radius,
                                 b.pos[1]-b.radius))
    for b in w.balls:
        screen.blit(ball_img, (b.pos[0] - b.radius,
                               b.pos[1] - b.radius))


session = scamp.session.Session().run_as_server()

piano = session.new_part("piano")
clarinet = session.new_part("clarinet")

piano.play_note(60, 0.5, 0.25)


def play_collision(colrec):
    if colrec.instrument == collisionrec.INST_CLARINET:
        clarinet.play_note(colrec.pitch, colrec.volume, 0.25)
    elif colrec.instrument == collisionrec.INST_PIANO:
        piano.play_note(colrec.pitch, colrec.volume, 0.25)


def find_empty_location(min_x, min_y, max_x, max_y,
                        dist, num_tries,
                        existing_posns):

    dist_sqr = dist * dist
    for try_num in range(num_tries):
        test_x = random.uniform(min_x, max_x)
        test_y = random.uniform(min_y, max_y)

        found_collision = False

        for px, py in existing_posns:
            dx = px - test_x
            dy = py - test_y
            if (dx * dx + dy * dy < dist_sqr):
                found_collision = True
                break

        if not found_collision:
            return (test_x, test_y)
    return None
    
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Galton Board w/ SCAMP")
    pygame_clock = pygame.time.Clock()

    w = world.World()
    SPAWN_WINDOW = 64
    BALLS_IN_FLIGHT = 3

    BUMPER_COUNT = 10

    bumper_pos_list = []

    for b_idx in range(BUMPER_COUNT):
        pos = find_empty_location(0, SPAWN_WINDOW * 2, WIDTH, HEIGHT - SPAWN_WINDOW,
                                  80, 15,
                                  bumper_pos_list)

        if pos:
            px, py = pos
            pitch = int(bdgmath.bdg_map(px, 0, WIDTH, 30, 90))
            bumper_pos_list.append(pos)
            w.add_bumper(px, py, pitch)
    
    exit_requested = False
    time_since_last_physics_tick = 0.0
    
    while not exit_requested:
        dt = pygame_clock.tick(60) / 1000
        time_since_last_physics_tick += dt
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_requested = True
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

        if len(w.balls) < BALLS_IN_FLIGHT:
            w.add_ball(random.uniform(0, WIDTH), random.uniform(-SPAWN_WINDOW, SPAWN_WINDOW))

        collisions = []
        while time_since_last_physics_tick > physics.TIME_STEP:
            colls = update(physics.TIME_STEP, w)
            collisions = collisions + colls
            time_since_last_physics_tick -= physics.TIME_STEP

        for c in collisions:
            session.fork(play_collision, (c,))
            
        w.cull(WIDTH, HEIGHT)
        draw(screen, w)
        pygame.display.flip()


    pygame.quit()


if __name__ == "__main__":
    main()
