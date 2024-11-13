import pygame

class Entity(pygame.sprite.Sprite):
  def __init__(self,game,surf,groups,scale=1):
    super().__init__(groups)
    self.game = game
    self.scale = scale
    self.visible = True
    try:
      self.image = pygame.transform.scale(surf, (surf.get_width()/scale,surf.get_height()/scale))
    except:
      self.image = None

  def set_collider(self,pos,screenProps,topleft):
    self.screenProps = screenProps
    self.pos = list(pos)
    self.velocity = [0, 0]
    self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
    if topleft:
      self.rect = self.image.get_rect(topleft=pos)
    else:
      self.rect = self.image.get_rect(topleft=([pos[0] - self.screenProps["tileW"], pos[1] - self.screenProps["tileH"]]))

  def set_actions(self,e_type):
    self.action = ''
    self.anim_offset = (-3, -3)
    self.type = e_type
    self.flip = False
    self.set_action('idle')
    self.last_movement = [0, 0]
  
  def set_action(self, action):
    if action != self.action:
        self.action = action
        self.animation = self.game.assets[self.type + '/' + self.action].copy()

  def set_debug(self,radius,color):
    self.radius = radius 
    self.color = color

  def update(self, tilemap, movement=(0, 0)):
    self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
    
    frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
    
    self.pos[0] += frame_movement[0]
    entity_rect = self.rect()
    for rect in tilemap.physics_rects_around(self.pos):
        if entity_rect.colliderect(rect):
            if frame_movement[0] > 0:
                entity_rect.right = rect.left
                self.collisions['right'] = True
            if frame_movement[0] < 0:
                entity_rect.left = rect.right
                self.collisions['left'] = True
            self.pos[0] = entity_rect.x
    
    self.pos[1] += frame_movement[1]
    entity_rect = self.rect()
    for rect in tilemap.physics_rects_around(self.pos):
        if entity_rect.colliderect(rect):
            if frame_movement[1] > 0:
                entity_rect.bottom = rect.top
                self.collisions['down'] = True
            if frame_movement[1] < 0:
                entity_rect.top = rect.bottom
                self.collisions['up'] = True
            self.pos[1] = entity_rect.y
            
    if movement[0] > 0:
        self.flip = False
    if movement[0] < 0:
        self.flip = True
        
    self.last_movement = movement
    
    self.velocity[1] = min(5, self.velocity[1] + 0.1)
    
    if self.collisions['down'] or self.collisions['up']:
        self.velocity[1] = 0
        
    self.animation.update()

class Tile(Entity):
  def __init__(self,game,surf,groups,pos="Na",screenProps="Na",topleft="Na",radius="Na",color="Na",scale=1):
    super().__init__(game,surf,groups,scale)
    if (pos != "Na") and (screenProps != "Na") and (topleft != "Na"):
      self.set_collider(pos,screenProps,topleft)
    if (radius != "Na") and (color != "Na"):
      self.set_debug(radius,color)

  def round(self,x):
    return int(self.base * round(float(x)/self.base))

  def debug(self,screen):
    pygame.draw.rect(screen,self.color,self.rect)
    #pygame.draw.circle(screen,self.color,(self.rect.x,self.rect.y),self.radius)
    
  def draw(self, screen):
    if self.image:
      screen.blit(self.image, self.rect)

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
        if self.type == "player":
          print("askdfñak")
        else:
          Tile(game=self.game,pos=pos,surf=surf,color=self.color,radius=int(6 * self.screenProps["tileW"] / 16),screenProps=self.screenProps,groups=self,topleft=self.topleft,scale=self.scale)
        
  def physics_rects_around(self, pos):
    rects = []
    for tile in self.tiles_around(pos):
      x = (tile.pos[0] * self.screenProps["tileW"])
      y = (tile.pos[1] * self.screenProps["tileH"])
      rects.append(pygame.Rect(x, y, self.screenProps["tileW"], self.screenProps["tileH"]))
    return rects

  def tiles_around(self, pos):
      """
      Retorna una lista de sprites (tiles) que están alrededor de una posición dada
      Args:
          pos (tuple): Posición (x, y) en píxeles
      Returns:
          list: Lista de sprites cercanos
      """
      tiles = []
      # Convertimos la posición en píxeles a coordenadas de tile
      tile_x = int(pos[0] // self.screenProps["tileW"])
      tile_y = int(pos[1] // self.screenProps["tileH"])
      
      # Verificamos cada offset
      for offset_x, offset_y in self.NEIGHBOR_OFFSETS:
          check_x = tile_x + offset_x
          check_y = tile_y + offset_y
          
          # Buscamos sprites en esa posición
          for sprite in self.sprites():
              sprite_tile_x = int(sprite.rect.x // self.screenProps["tileW"])
              sprite_tile_y = int(sprite.rect.y // self.screenProps["tileH"])
              
              # Si encontramos un sprite en la posición buscada, lo añadimos
              if sprite_tile_x == check_x and sprite_tile_y == check_y:
                  tiles.append(sprite)
      
      return tiles

  def move(self,x,y):
    for sprite in self.sprites():
      sprite.rect.x += x
      sprite.rect.y += y 

  def render(self,screen):
    for sprite in self.sprites():
      if sprite.visible:
        sprite.draw(screen)

  def debug(self,screen):
    for sprite in self.sprites():
      if sprite.visible:
        sprite.debug(screen)


