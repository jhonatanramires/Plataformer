import pygame
import random

class Camera:
    def __init__(self, screen_width, screen_height, map_props):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scroll = [0, 0]
        self.target = None
        self.screen_shake = 0
        
        # Store map properties
        self.map_width = map_props["screenSize"][0]
        self.map_height = map_props["screenSize"][1]
        self.tile_width = map_props["tileW"]
        self.tile_height = map_props["tileH"]
        
        # Camera configuration
        self.lerp_speed = 0.1
        self.offset = [0, 0]
        
        # Calculate true bounds considering screen size
        self.bounds = {
            'left': -self.tile_width,  # Allow slight overflow on left
            'right': self.map_width - self.screen_width + self.tile_width,
            'top': -self.tile_height,  # Allow slight overflow on top
            'bottom': self.map_height - self.screen_height + self.tile_height
        }
        
    def set_target(self, target):
        self.target = target
        
    def apply_screen_shake(self, intensity):
        self.screen_shake = intensity
        
    def update(self):
        if not self.target:
            return
        
        # Calculate desired camera position (centered on target)
        target_x = self.target.rect.centerx - self.screen_width // 1
        target_y = self.target.rect.centery - self.screen_height // 1.4
        
        # Apply bounds
        target_x = max(self.bounds['left'], min(self.bounds['right'], target_x))
        target_y = max(self.bounds['top'], min(self.bounds['bottom'], target_y))
        
        # Smooth camera movement
        self.scroll[0] += (target_x - self.scroll[0]) * self.lerp_speed
        self.scroll[1] += (target_y - self.scroll[1]) * self.lerp_speed
        
        # Screen shake effect
        if self.screen_shake > 0:
            self.offset[0] = random.randint(-self.screen_shake, self.screen_shake)
            self.offset[1] = random.randint(-self.screen_shake, self.screen_shake)
            self.screen_shake = max(0, self.screen_shake - 1)
        else:
            self.offset = [0, 0]
    
    def get_offset(self):
        return (round(self.scroll[0] + self.offset[0]), 
                round(self.scroll[1] + self.offset[1]))
                
    def apply(self, rect):
        offset_x, offset_y = self.get_offset()
        return pygame.Rect(rect.x - offset_x, 
                         rect.y - offset_y, 
                         rect.width, 
                         rect.height)

    def apply_rect(self, rect):
        """Apply camera offset to any rect and return the adjusted position"""
        offset_x, offset_y = self.get_offset()
        return (rect.x - offset_x, rect.y - offset_y)