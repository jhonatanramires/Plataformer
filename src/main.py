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
          self.mapTile.move(-12,0)
        if event.key == pygame.K_RIGHT:
          self.mapTile.move(12,0)
        if event.key == pygame.K_UP:
          self.mapTile.move(0,-12)
        if event.key == pygame.K_DOWN:
          self.mapTile.move(0,12) 
          
    self.render()

  def render(self):
    #self.screen.blit(self.background, (0, 0))
    self.screen.fill((0, 0, 0, 0))
    self.mapTile.render(self.screen)
    #self.mapTile.debug(self.screen)
    pygame.display.update()

    self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    while True:
      game.update()