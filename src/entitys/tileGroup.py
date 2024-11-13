import pygame

class Entity(pygame.sprite.Sprite):
  def __init__(self,surf,groups,scale=1):
    super().__init__(groups)
    self.scale = scale
    self.visible = True
    try:
      self.image = pygame.transform.scale(surf, (surf.get_width()/scale,surf.get_height()/scale))
    except:
      self.image = None

  def set_collider(self,pos,screenProps,topleft):
    self.screenProps = screenProps
    if topleft:
      self.rect = self.image.get_rect(topleft=pos)
    else:
      self.rect = self.image.get_rect(topleft=([pos[0] - self.screenProps["tileW"], pos[1] - self.screenProps["tileH"]]))

  def set_debug(self,radius,color):
    self.radius = radius 
    self.color = color

class Tile(Entity):
  def __init__(self,surf,groups,pos="Na",screenProps="Na",topleft="Na",radius="Na",color="Na",scale=1):
    super().__init__(surf,groups,scale)
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
  def __init__(self,tile_name,game,tmx_data,screenProps,topleft,type,color="Na",scale=1):
    super().__init__()
    self.color = color
    self.tile_name = tile_name
    self.tmx_data = tmx_data
    self.scale = scale
    self.game = game
    self.type = type
    self.screenProps = screenProps
    self.topleft = topleft

  def setupTiles(self):
    # recorrer cada una de las capas
    for layer in self.tmx_data.visible_layers:
      if hasattr(layer,'data'): # solo las tiles no los objetos
        if layer.name == self.tile_name:
          print("🚀 ~ tile_name -> setupTiles():", self.tile_name)
          for x,y,surf in layer.tiles():
            pos = (x * self.screenProps["tileW"],y * self.screenProps["tileH"])
            if self.type == "Tile":
              Tile(pos= pos,color=self.color,radius=int(6 * self.screenProps["tileW"] / 16),screenProps=self.screenProps,surf=surf,groups=self,topleft=self.topleft,scale=self.scale)
            else:
              Tile(pos= pos,surf=surf,color=self.color,radius=int(6 * self.screenProps["tileW"] / 16),screenProps=self.screenProps,groups=self,topleft=self.topleft,scale=self.scale)
          for obj in self.tmx_data.objects:
            if obj.image:
              Tile(pos=(obj.x,obj.y), surf=obj.image, screenProps=self.screenProps,groups=self.sprite_group,topleft=self.topleft,scale=self.scale)

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

