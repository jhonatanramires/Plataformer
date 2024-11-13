from tiles.tile import Tile
import pygame
import random
import math

class Player(Tile):
    def __init__(self, game, surf, groups, pos="Na", screenProps="Na", topleft="Na", radius="Na", color="Na", scale=1):
        super().__init__(game, surf, groups, scale)
        if (pos != "Na") and (screenProps != "Na") and (topleft != "Na"):
            self.set_collider(pos, screenProps, topleft)
        if (radius != "Na") and (color != "Na"):
            self.set_debug(radius, color)
        
        # Player specific attributes
        self.set_actions("player")
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0
        self.velocity = [0, 0]
        
        # Movement constants
        self.MOVEMENT_SPEED = 2.0
        self.MAX_FALL_SPEED = 5
        self.GRAVITY = 0.1

    def update(self, tilemap):
        # Get movement from game state
        movement = [0, 0]
        if self.game.movement[0]:  # Left
            movement[0] = -1
        if self.game.movement[1]:  # Right
            movement[0] = 1

        # Update air time
        self.air_time += 1
        
        # Handle death condition
        if self.air_time > 120:
            if not self.game.dead:
                self.game.screenshake = max(16, self.game.screenshake)
            self.game.dead += 1

        # Handle basic movement
        if movement[0] != 0:
            self.velocity[0] = movement[0] * self.MOVEMENT_SPEED
            # Update flip direction
            self.flip = movement[0] < 0
        else:
            # Decelerate when no movement input
            if self.velocity[0] > 0:
                self.velocity[0] = max(0, self.velocity[0] - 0.1)
            else:
                self.velocity[0] = min(0, self.velocity[0] + 0.1)
        
        # Handle dash
        if abs(self.dashing) > 50:
            dash_direction = abs(self.dashing) / self.dashing
            self.velocity[0] = dash_direction * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            self.create_dash_particles(1)
        
        # Apply gravity
        if not self.collisions['down']:
            self.velocity[1] = min(self.MAX_FALL_SPEED, self.velocity[1] + self.GRAVITY)
        else:
            self.velocity[1] = 0
            self.air_time = 0
            self.jumps = 1

        # Calculate final movement
        frame_movement = (self.velocity[0], self.velocity[1])
        
        # Update position and collisions
        super().update(tilemap, movement=frame_movement)
        
        # Handle wall sliding
        self.handle_wall_slide()
        
        # Update animation states
        self.update_animation_state(movement)
        
        # Update dash state
        self.update_dash_state()

    def handle_wall_slide(self):
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            self.flip = not self.collisions['right']
            self.set_action('wall_slide')

    def update_animation_state(self, movement):
        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')

    def update_dash_state(self):
        if abs(self.dashing) in {60, 50}:
            self.create_dash_particles(20)
            
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)

    def create_dash_particles(self, count):
        for i in range(count):
            angle = random.random() * math.pi * 2
            speed = random.random() * 0.5 + 0.5
            pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            self.game.particles.append(
                Particle(self.game, 'particle', self.rect.center, 
                        velocity=pvelocity, frame=random.randint(0, 7))
            )

    def jump(self):
        if self.wall_slide:
            if self.flip and self.game.movement[0]:  # Left
                self.velocity[0] = 12.5
                self.velocity[1] = -8.5
                self.air_time = 10
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.game.movement[1]:  # Right
                self.velocity[0] = -12.5
                self.velocity[1] = -8.5
                self.air_time = 10
                self.jumps = max(0, self.jumps - 1)
                return True
        elif self.jumps:
            self.velocity[1] = -6
            self.jumps -= 1
            self.air_time = 5
            return True
        return False

    def dash(self):
        if not self.dashing:
            self.game.sfx['dash'].play()
            self.dashing = -60 if self.flip else 60

    def draw(self, screen):
        if abs(self.dashing) <= 50:
            super().draw(screen)