import pygame
from pytmx.util_pygame import load_pygame
from tiles.tileGroup import TileGroup
from scripts.clouds import Clouds
from scripts.utils import load_image, load_images, Animation
from scripts.camera import Camera

class Setup():
  def __init__(self):
    pygame.init()
    self.set_display()
    self.set_assets()
    self.set_sound()
    self.level = 0
    self.set_level(self.level)
    self.clock = pygame.time.Clock()
    self.movement = [False, False]
    self.screenshake = 0

  def set_tiles(self,tile_path):
    self.set_cons(tile_path)
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
    self.clouds = Clouds(self.assets['clouds'], count=16)
    self.movement = [False, False]
    self.screenProps = {
        "tileW": self.tmx_data.tilewidth,
        "tileH": self.tmx_data.tileheight,
        "nRows" : self.tmx_data.width,
        "hCols" : self.tmx_data.height,
        "screenSize" : (self.tmx_data.tilewidth * self.tmx_data.width,self.tmx_data.tileheight * self.tmx_data.height)
    }
    self.camera = Camera(
        self.display.get_width(),
        self.display.get_height(),
        self.screenProps
    )
    self.my_font = pygame.font.SysFont('Bahnschrift', self.screenProps["tileH"])

  def set_assets(self):
    self.assets = {
      'decor': load_images('tiles/decor'),
      'grass': load_images('tiles/grass'),
      'large_decor': load_images('tiles/large_decor'),
      'stone': load_images('tiles/stone'),
      'player': load_image('entities/player.png'),
      'background': load_image('background.png'),
      'clouds': load_images('clouds'),
      'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
      'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
      'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
      'player/run': Animation(load_images('entities/player/run'), img_dur=4),
      'player/jump': Animation(load_images('entities/player/jump')),
      'player/slide': Animation(load_images('entities/player/slide')),
      'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
      'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
      'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
      'gun': load_image('gun.png'),
      'projectile': load_image('projectile.png'),
      }
  def set_level(self,level):
    self.set_tiles("../data/maps/level2.tmx")
            
    #self.enemies = []
    #for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
    #    if spawner['variant'] == 0:
    #        self.player.pos = spawner['pos']
    #        self.player.air_time = 0
    #    else:
    #        self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))
        
    self.projectiles = []
    self.particles = []
    self.sparks = []
    
    self.scroll = [0, 0]
    self.render_scroll = self.scroll
    self.dead = 0
    self.transition = -30