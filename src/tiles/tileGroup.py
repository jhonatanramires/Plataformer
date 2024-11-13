import pygame
import math 
import random
from tiles.tile import Tile, Entity
from entitys.player import Player

class TileGroup(pygame.sprite.Group):
  def __init__(self,game,layer,screenProps,topleft,type,color="Na",scale=1):
    super().__init__()
    self.game = game
    self.layer = layer
    self.screenProps = screenProps
    self.topleft = topleft
    self.type = type
    self.color = color
    self.scale = scale
    self.NEIGHBOR_OFFSETS = [
      (-1, -1), (-1, 0), (-1, 1),  # arriba izquierda, arriba, arriba derecha
      (0, -1),  ( 0, 0), (0,  1),    # izquierda, derecha
      (1, -1),  ( 1, 0), (1,  1)     # abajo izquierda, abajo, abajo derecha
    ]

  def setupTiles(self):
    if hasattr(self.layer,'data'):
      print("🚀 ~ tile_name -> setupTiles():", self.layer.name)
      for x,y,surf in self.layer.tiles():
        pos = (x * self.screenProps["tileW"],y * self.screenProps["tileH"])
        if self.type == "map":
          Tile(game=self.game,pos=pos,color=self.color,radius=int(6 * self.screenProps["tileW"] / 16),screenProps=self.screenProps,surf=surf,groups=self,topleft=self.topleft,scale=self.scale)
        if self.type == "no":
          Entity(game=self.game,surf=surf,groups=self,pos=pos)
        if self.type == "player":
          self.game.player = Player(game=self.game,pos=pos,color=self.color,radius=int(6 * self.screenProps["tileW"] / 16),screenProps=self.screenProps,surf=surf,groups=self,topleft=self.topleft,scale=self.scale)
          self.game.camera.set_target(self.game.player)
        else:
          Tile(game=self.game,pos=pos,surf=surf,color=self.color,radius=int(6 * self.screenProps["tileW"] / 16),screenProps=self.screenProps,groups=self,topleft=self.topleft,scale=self.scale)

  def render(self,screen):
    for sprite in self.sprites():
      if sprite.visible:
        sprite.draw(screen)

  def debug(self,screen):
    for sprite in self.sprites():
      if sprite.visible:
        sprite.debug(screen)