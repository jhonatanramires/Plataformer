import pygame
from pytmx.util_pygame import load_pygame
from entitys.tileGroup import TileGroup

class Setup():
  def __init__(self):
    pygame.init()
    self.set_display()
    self.set_sound()
    self.set_cons("../data/maps/level.tmx")
    self.setupTiles()
    self.clock = pygame.time.Clock()

  def setupTiles(self):
    # MAP
    self.tileMaps = {}
    for layerName in self.tmx_data.layernames:
      layer = self.tmx_data.get_layer_by_name(layerName)
      if layer in self.tmx_data.visible_layers:
        self.tileMaps[layerName] = TileGroup(game=self,layer=layer,color=layer.properties['color'],screenProps=self.screenProps,topleft=layer.properties['topleft'],type=layer.properties['type'])
        self.tileMaps[layerName].setupTiles()

  def set_display(self):
    pygame.display.set_caption('ninja game')
    self.screen = pygame.display.set_mode((640, 480))
    self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
    self.display_2 = pygame.Surface((320, 240))

  def set_sound(self):
    self.sfx = {
      'jump': pygame.mixer.Sound('../data/sfx/jump.wav'),
      'dash': pygame.mixer.Sound('../data/sfx/dash.wav'),
      'hit': pygame.mixer.Sound('../data/sfx/hit.wav'),
      'shoot': pygame.mixer.Sound('../data/sfx/shoot.wav'),
      'ambience': pygame.mixer.Sound('../data/sfx/ambience.wav'),
    }
    
    self.sfx['ambience'].set_volume(0.2)
    self.sfx['shoot'].set_volume(0.4)
    self.sfx['hit'].set_volume(0.8)
    self.sfx['dash'].set_volume(0.3)
    self.sfx['jump'].set_volume(0.7)

  def set_cons(self,level):
    self.tmx_data = load_pygame(level)
    self.screenProps = {
        "tileW": self.tmx_data.tilewidth,
        "tileH": self.tmx_data.tileheight,
        "nRows" : self.tmx_data.width,
        "hCols" : self.tmx_data.height,
        "screenSize" : (self.tmx_data.tilewidth * self.tmx_data.width,self.tmx_data.tileheight * self.tmx_data.height)
    }
    self.my_font = pygame.font.SysFont('Bahnschrift', self.screenProps["tileH"])