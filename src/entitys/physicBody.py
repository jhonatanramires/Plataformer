import pygame
import math
import random
from scripts.particle import Particle

class PhysicsBody:
    """Base class for handling physics calculations"""
    def __init__(self):
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.friction = 0.85
        self.gravity = 0.4
        self.terminal_velocity = 8
        self.grounded = False
        self.mass = 1.0

    def apply_force(self, force):
        """Apply a force vector to the body"""
        self.acceleration += force / self.mass

    def update_physics(self):
        """Update physics calculations"""
        # Apply acceleration to velocity
        self.velocity += self.acceleration
        
        # Apply terminal velocity
        self.velocity.y = min(self.velocity.y, self.terminal_velocity)
        
        # Apply friction when grounded
        if self.grounded:
            self.velocity.x *= self.friction
        
        # Reset acceleration
        self.acceleration *= 0

class Entity(pygame.sprite.Sprite):
    def __init__(self, game, surf, groups, pos, scale=1):
        super().__init__(groups)
        self.physics = PhysicsBody()
        self.pos = pygame.math.Vector2(pos)
        self.game = game
        self.scale = scale
        self.visible = True
        
        if surf:
            try:
                width = int(surf.get_width() / scale)
                height = int(surf.get_height() / scale)
                self.image = pygame.transform.scale(surf, (width, height))
            except (AttributeError, pygame.error) as e:
                print(f"Error scaling image: {e}")
                self.image = None
        else:
            self.image = None

    def set_collider(self, pos, screenProps, topleft):
        self.screenProps = screenProps
        self.pos = pygame.math.Vector2(pos)
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        if topleft:
            self.rect = self.image.get_rect(topleft=pos)
        else:
            self.rect = self.image.get_rect(topleft=(
                pos[0] - self.screenProps["tileW"],
                pos[1] - self.screenProps["tileH"]
            ))
    def set_action(self, action):
      if action != self.action:
          self.action = action
          self.animation = self.game.assets[self.type + '/' + self.action].copy()
    def set_actions(self,e_type):
      self.action = ''
      self.anim_offset = (-3, -3)
      self.type = e_type
      self.flip = False
      self.set_action('idle')
      self.last_movement = [0, 0]

class Tile(Entity):
    def __init__(self, game, surf, groups, pos="Na", screenProps="Na", topleft="Na", radius="Na", color="Na", scale=1):
        super().__init__(game, surf, groups, pos if pos != "Na" else (0, 0), scale)
        if (pos != "Na") and (screenProps != "Na") and (topleft != "Na"):
            self.set_collider(pos, screenProps, topleft)
        if (radius != "Na") and (color != "Na"):
            pass
            #self.set_debug(radius, color)
        
        # Physics properties
        self.coyote_time = 0
        self.COYOTE_FRAMES = 6
        self.buffer_jump = False
        self.BUFFER_FRAMES = 6
        self.buffer_timer = 0

    def update(self, tilemap, movement=(0, 0)):
        # Reset collisions
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        # Update physics
        self.physics.update_physics()
        
        # Add movement to velocity
        self.physics.velocity.x += movement[0]
        
        # Update position with velocity
        move_vector = self.physics.velocity + pygame.math.Vector2(movement)
        
        # Handle X movement and collisions
        self.pos.x += move_vector.x
        self.rect.x = int(self.pos.x)
        self._handle_horizontal_collisions(tilemap)
        
        # Handle Y movement and collisions
        self.pos.y += move_vector.y
        self.rect.y = int(self.pos.y)
        self._handle_vertical_collisions(tilemap)
        
        # Update grounded state
        self.physics.grounded = self.collisions['down']
        
        # Apply gravity if not grounded
        if not self.physics.grounded:
            self.physics.apply_force(pygame.math.Vector2(0, self.physics.gravity))
            self.coyote_time = max(0, self.coyote_time - 1)
        else:
            self.coyote_time = self.COYOTE_FRAMES
        
        # Update buffer timer
        if self.buffer_jump:
            self.buffer_timer = max(0, self.buffer_timer - 1)
            if self.buffer_timer == 0:
                self.buffer_jump = False

    def _handle_horizontal_collisions(self, tilemap):
        for tile in tilemap.sprites():
            if tile != self and tile.rect.colliderect(self.rect):
                if self.physics.velocity.x > 0:
                    self.rect.right = tile.rect.left
                    self.collisions['right'] = True
                elif self.physics.velocity.x < 0:
                    self.rect.left = tile.rect.right
                    self.collisions['left'] = True
                self.pos.x = self.rect.x
                self.physics.velocity.x = 0

    def _handle_vertical_collisions(self, tilemap):
        for tile in tilemap.sprites():
            if tile != self and tile.rect.colliderect(self.rect):
                if self.physics.velocity.y > 0:
                    self.rect.bottom = tile.rect.top
                    self.collisions['down'] = True
                elif self.physics.velocity.y < 0:
                    self.rect.top = tile.rect.bottom
                    self.collisions['up'] = True
                self.pos.y = self.rect.y
                self.physics.velocity.y = 0

class Player(Tile):
    def __init__(self, game, surf, groups, pos="Na", screenProps="Na", topleft="Na", radius="Na", color="Na", scale=1):
        super().__init__(game, surf, groups, pos, screenProps, topleft, radius, color, scale)
        self.set_actions("player")
        
        # Movement constants
        self.MOVE_SPEED = 0.2
        self.JUMP_FORCE = -8.0
        self.WALL_JUMP_FORCE = pygame.math.Vector2(-12.5, -8.5)
        self.DASH_SPEED = 8.0
        self.AIR_CONTROL = 0.7
        
        # State variables
        self.jumps_left = 2
        self.wall_sliding = True
        self.dash_time = 0
        self.DASH_DURATION = 60
        self.dash_cooldown = 0
        self.DASH_COOLDOWN = 30
        self.facing_right = True

    def update(self, tilemap):
        # Get movement input
        movement = pygame.math.Vector2(0, 0)
        if self.game.movement[0]:  # Left
            movement.x = -1
            self.facing_right = False
        if self.game.movement[1]:  # Right
            movement.x = 1
            self.facing_right = True

        # Apply air control
        if not self.physics.grounded:
            movement.x *= self.AIR_CONTROL

        # Scale movement by speed
        movement.x *= self.MOVE_SPEED

        # Handle wall sliding
        self.wall_sliding = self._check_wall_slide()
        if self.wall_sliding:
            self.physics.velocity.y = min(self.physics.velocity.y, 0.5)
            self.set_action('wall_slide')

        # Update physics and position
        super().update(tilemap, movement)

        # Update animation states
        self._update_animation_state(movement)

        # Update dash state
        self._update_dash_state()

        # Reset jumps when grounded
        if self.physics.grounded:
            self.jumps_left = 1

    def jump(self):
        can_jump = (self.physics.grounded or self.coyote_time > 0 or self.jumps_left > 0)
        
        if self.wall_sliding:
            if (self.facing_right and self.game.movement[1]) or (not self.facing_right and self.game.movement[0]):
                self.physics.velocity = self.WALL_JUMP_FORCE
                if self.facing_right:
                    self.physics.velocity.x *= -1
                self.jumps_left = max(0, self.jumps_left - 1)
                return True
        elif can_jump:
            self.physics.velocity.y = self.JUMP_FORCE
            self.jumps_left -= 1
            self.physics.grounded = False
            return True
        else:
            # Buffer jump
            self.buffer_jump = True
            self.buffer_timer = self.BUFFER_FRAMES
        return False

    def dash(self):
        if self.dash_cooldown <= 0 and self.dash_time <= 0:
            self.game.sfx['dash'].play()
            self.dash_time = self.DASH_DURATION
            self.dash_cooldown = self.DASH_COOLDOWN
            dash_direction = 1 if self.facing_right else -1
            self.physics.velocity.x = self.DASH_SPEED * dash_direction

    def _check_wall_slide(self):
        return (self.collisions['right'] or self.collisions['left']) and not self.physics.grounded

    def _update_animation_state(self, movement):
        if not self.wall_sliding:
            if not self.physics.grounded:
                self.set_action('jump')
            elif abs(movement.x) > 0:
                self.set_action('run')
            else:
                self.set_action('idle')

    def _update_dash_state(self):
        if self.dash_time > 0:
            self.dash_time -= 1
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
  