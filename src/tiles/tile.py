import pygame

class Entity(pygame.sprite.Sprite):
  def __init__(self, game, surf, groups, pos, scale=1):
      super().__init__(groups)
      self.pos = pos
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

  def draw(self, screen):
    if self.image:
      screen.blit(self.image, self.pos)      
  
  def render(self, surf, offset=(0, 0)):
    surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        

class Tile(Entity):
    def __init__(self, game, surf, groups, pos="Na", screenProps="Na", topleft="Na", radius="Na", color="Na", scale=1):
        super().__init__(game, surf, groups, scale)
        if (pos != "Na") and (screenProps != "Na") and (topleft != "Na"):
            self.set_collider(pos, screenProps, topleft)
        if (radius != "Na") and (color != "Na"):
            self.set_debug(radius, color)

    def round(self, x):
        return int(self.base * round(float(x)/self.base))

    def debug(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        #pygame.draw.circle(screen, self.color, (self.rect.x, self.rect.y), self.radius)

    def update(self, tilemap, movement=(0, 0)):
        # Reiniciar colisiones
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        # Calcular el movimiento total para este frame
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        # Actualizar posición X y comprobar colisiones horizontales
        self.pos[0] += frame_movement[0]
        self.rect.x = self.pos[0]
        
        # Obtener tiles cercanas para colisiones
        nearby_tiles = tilemap.sprites()
        
        # Colisiones horizontales
        for tile in nearby_tiles:
            if tile != self and tile.rect.colliderect(self.rect):
                if frame_movement[0] > 0:  # Moviendo a la derecha
                    self.rect.right = tile.rect.left
                    self.collisions['right'] = True
                elif frame_movement[0] < 0:  # Moviendo a la izquierda
                    self.rect.left = tile.rect.right
                    self.collisions['left'] = True
                self.pos[0] = self.rect.x
                
        # Actualizar posición Y y comprobar colisiones verticales
        self.pos[1] += frame_movement[1]
        self.rect.y = self.pos[1]
        
        # Colisiones verticales
        for tile in nearby_tiles:
            if tile != self and tile.rect.colliderect(self.rect):
                if frame_movement[1] > 0:  # Cayendo
                    self.rect.bottom = tile.rect.top
                    self.collisions['down'] = True
                elif frame_movement[1] < 0:  # Saltando
                    self.rect.top = tile.rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = self.rect.y
        
        # Actualizar dirección del sprite
        if movement[0] > 0:
            self.flip = False
        elif movement[0] < 0:
            self.flip = True
            
        # Guardar último movimiento
        self.last_movement = movement
        
        # Aplicar gravedad
        if not self.collisions['down']:
            self.velocity[1] = min(5, self.velocity[1] + 0.1)
        else:
            self.velocity[1] = 0
            
        # Si hay colisión arriba, detener velocidad vertical
        if self.collisions['up']:
            self.velocity[1] = 0
            
        # Actualizar animación
        if hasattr(self, 'animation'):
            self.animation.update()

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)