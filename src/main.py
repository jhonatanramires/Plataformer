import pygame
import sys
from pygame.locals import *
from scripts.setup import Setup  

# Albion online es un mmorpg no lineal en el que escribes tu propia historia sin limitarte a seguir un camino prefijado, explora
# ..
class Game(Setup):
  def __init__(self):
    super().__init__()
    self.background = None

  def update(self):
    #dt = self.clock.tick(60) / 1000.0
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
          self.tileMaps["Map"].move(-12,0)
        if event.key == pygame.K_RIGHT:
          self.tileMaps["Map"].move(12,0)
        if event.key == pygame.K_UP:
          self.tileMaps["Map"].move(0,-12)
        if event.key == pygame.K_DOWN:
          self.tileMaps["Map"].move(0,12) 
        if event.key == pygame.K_SPACE:
          idk = self.tileMaps["Map"].tiles_around((100,100))
          rects = self.tileMaps["Map"].physics_rects_around((100,100))
          for sprite in idk:
            sprite.visible = False 
          for rect in rects:
            pygame.draw.rect(self.screen,"blue",rect)
          
    self.render()

  def render(self):
    #self.screen.blit(self.background, (0, 0))
    self.screen.fill((0, 0, 0, 0))
    for tileName in self.tileMaps.keys():
      self.tileMaps[tileName].render(self.screen)
    pygame.draw.circle(self.screen,"red",(100,100),10)
    #self.tileMaps["Map"].debug(self.screen)
    pygame.display.update()

    self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    while True:
      game.update()