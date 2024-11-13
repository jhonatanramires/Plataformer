import pygame
import sys
from pygame.locals import *
from scripts.setup import Setup
import random   

class Game(Setup):
  def __init__(self):
    super().__init__()
    self.background = None

  def update(self):
    #dt = self.clock.tick(60) / 1000.0
    self.tileMaps["Player"].update(self.tileMaps["Map"])
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()
      if event.type == pygame.KEYUP:
        if event.key == pygame.K_LEFT:
            self.movement[0] = False
        if event.key == pygame.K_RIGHT:
            self.movement[1] = False
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            self.movement[0] = True
        if event.key == pygame.K_RIGHT:
            self.movement[1] = True
        if event.key == pygame.K_UP:
            if self.player.jump():
                self.sfx['jump'].play()
        if event.key == pygame.K_x:
            self.player.dash()          
    self.render()

  def render(self):
    # Clear displays
    self.display.fill((0, 0, 0, 0))
    self.display_2.blit(self.assets['background'], (0, 0))
    
    # Update camera
    self.camera.update()
    if self.screenshake:
        self.camera.apply_screen_shake(self.screenshake)
        self.screenshake = 0
    
    # Get camera offset
    camera_offset = self.camera.get_offset()
    
    # Render clouds with camera offset
    self.clouds.update()
    self.clouds.render(self.display_2, offset=camera_offset)
    
    # Combine displays
    self.display_2.blit(self.display, (0, 0))
    
    # Scale to screen
    self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), (0, 0))
    
    # Render tiles with camera offset
    for tileName in self.tileMaps.keys():
        for sprite in self.tileMaps[tileName].sprites():
            if sprite.visible:
                # Apply camera offset to sprite position
                try:
                  draw_rect = self.camera.apply(sprite.rect)
                  self.screen.blit(sprite.image, draw_rect)
                except:
                  self.screen.blit(sprite.image, ((sprite.pos[0] + camera_offset[0]),(sprite.pos[1] + camera_offset[1])))
    
    pygame.display.update()
    self.clock.tick(60)

  def run(self):
    pygame.mixer.music.load('../data/music.wav')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    
    self.sfx['ambience'].play(-1)

    while True:
      game.update()

if __name__ == "__main__":
    game = Game()
    game.run()