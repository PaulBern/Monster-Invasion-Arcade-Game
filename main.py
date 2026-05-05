
###############################################################################
# Monster Invasion Arcade
# -----------------------
# Copyright (c) 2026 Paul Georg Berning
# berning@elsetech.de
# www.elsetech.de
#
# This software is released under the MIT License.
# See the LICENSE file in the project root for full license information.
#
# Developed in Cologne, Germany.
###############################################################################


#########################################################################################################################################
#   __   __  _______  __    _  _______  _______  _______  ______      ___   __    _  __   __  _______  _______  ___   _______  __    _  #
#  |  |_|  ||       ||  |  | ||       ||       ||       ||    _ |    |   | |  |  | ||  | |  ||   _   ||       ||   | |       ||  |  | | #
#  |       ||   _   ||   |_| ||  _____||_     _||    ___||   | ||    |   | |   |_| ||  |_|  ||  |_|  ||  _____||   | |   _   ||   |_| | #
#  |       ||  | |  ||       || |_____   |   |  |   |___ |   |_||_   |   | |       ||       ||       || |_____ |   | |  | |  ||       | #
#  |       ||  |_|  ||  _    ||_____  |  |   |  |    ___||    __  |  |   | |  _    ||       ||       ||_____  ||   | |  |_|  ||  _    | #
#  | ||_|| ||       || | |   | _____| |  |   |  |   |___ |   |  | |  |   | | | |   | |     | |   _   | _____| ||   | |       || | |   | #
#  |_|   |_||_______||_|  |__||_______|  |___|  |_______||___|  |_|  |___| |_|  |__|  |___|  |__| |__||_______||___| |_______||_|  |__| #
#                                                                                                                                       #
#                                                                                                                                       #
#                                                             survive the monsters!                                                     #
#                                                                   ~   ~   ~                                                           #
#                                                                                                                                       #
#                                         M   O   N   S   T   E   R       I   N   V   A   S   I   O   N                                 #
#                                                                                                                                       #
#                                                    by Paul Georg Berning - Cologne Germany                                            #
#                                                                                                                                       #
#                                                                    2026                                                               #
#########################################################################################################################################


#imports:
import pygame
import math
import random
import numpy as np


#Helper Function: We need to tint the monser image in different colors
def tint_image(image, color):
    #create a copy of the image
    tinted = image.copy()
    
    # create a colored surface for overlaying it
    color_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    color_surface.fill(color + (0,)) 
    # we tint the image now
    tinted.blit(color_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    return tinted

#This is a class for the weapons of the player:
class Weapon:
    def __init__(self, cooldown, bullet_speed, damage, spread, projectiles, name):
        self.cooldown = cooldown                #the time between the shots
        self.bullet_speed = bullet_speed        #the speed of the bullet 
        self.damage = damage                    #the damage of the gun
        self.spread = spread                    #we need a spread angle for a shotgun
        self.projectiles = projectiles          #the projectiles for the gun
        self.name = name                        #the name for the gun which is displayed on the lower left side of the HUD

#This class represents the items which are dropped by the enemys
class Item:
    def __init__(self, x, y, image):
        self.x = x                              #x coodinate of the item
        self.y = y                              #y coordinate of the item
        self.image = image                      #coins have an image which is stored here

    def draw(self, surface):                    #the draw function of the item
        surface.blit(self.image, (self.x, self.y))


class Coin(Item):                               #the coin item which adds points for the player when he collects it
    def __init__(self, x, y, image):
        super().__init__(x, y, image)


class Cross(Item):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y)) # draw the health image

class WeaponItem(Item):                         #weapon item (displayed as "W") for changing the players weapon
    def __init__(self, x, y, weapon, image):
        super().__init__(x, y, image)
        self.weapon = weapon  # Speichert die Waffen-Daten (Schaden, Speed, etc.)

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))# draw the weapon sprite

#This class is represents the player
class RobotPlayer:
    def __init__(self):                         #init health, points and the startposition of the playr
        self._health = 100
        self._points = 0
        self._x = 640/2
        self._y= 480/2
        self._velocity = 3
    def sub_health(self, points : int):         #subtract health function
        self._health -= points

    def add_health(self, points : int):         #add health function
        self._health += points
        
    def add_points( self, points: int):         #add points function
        self._points += points
        
    def get_x(self):                            #get the x coordinate
        return self._x
        
    def get_y(self):                            #het the y coordinate
        return self._y
        
    def set_x(self, new_x : int):               #set the x coodrinate
        self._x = new_x
        
    def set_y(self, new_y : int):               #set the y coordinate
        self._y = new_y
    
    def set_weapon(self, weapon : Weapon):      #set a weapon to the player
        self._weapon = weapon
    
    def get_weapon( self ):                     #get the current wapon of the player
        return self._weapon

    def get_velocity( self ):                   #get the velocity of the player
        return self._velocity
    
    def set_velocity(self, velocity : int ):    #set the velocity of the player
        self.velocity = velocity


#This class represents a single bullet wich is shot by a gun
class Bullet:
    def __init__(self, x, y, dx, dy, speed, damage, weapon_name=None):
        self.x = x                              #x coordinate of the bullet
        self.y = y                              #y coordinate of the bullet
        self.dx = dx                            #delta x: difference of the x coodinate per frame                         
        self.dy = dy                            #delta y: difference of the y coodinate per frame
        self.speed = speed                      #speed of the bullet
        self.damage = damage                    #the damage of the bullet
        self.weapon_name = weapon_name          #the name of the weapon which shot the bullet ("maschine gun, shotgun etc")

    def update(self):                           #updates the bullet position
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

    def draw(self, window):                     #draw the bullet
        if self.weapon_name == "rocket launcher":#we have a different visualization for rocket launcher bullets
            length = 12
            width = 6
            end_x = int(self.x + self.dx * length)
            end_y = int(self.y + self.dy * length)
            pygame.draw.line(window, (255, 100, 0), (int(self.x), int(self.y)), (end_x, end_y), width)
        else:                                     #other bullets are small yellow circles
            pygame.draw.circle(window, (255, 255, 0), (int(self.x), int(self.y)), 3)

#we define the enemies here:
class Enemy:
    def __init__(self, x, y, dx, dy, image):
        self.x = x                              #x coordinates of the enemy
        self.y = y                              #y coordinates of the enemy
        self.dx = dx                            #delta x, the x difference per frame
        self.dy = dy                            #delta y, the y difference per frame
        self.speed = 1.5                        #speed of the enemy
        self.image = image                      #every image has an seperated image with a random color
        self.health = 10                        #enemys health points
        self.hit_timer = 0                      #controls the hit process

    def update(self):                           #update function of the enemy
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

    def draw(self, surface):                    #draw function of the enemy
        if self.hit_timer > 0:                  #flashing effect: the enemy flashes when it's hit
            temp = self.image.copy()
            temp.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(temp, (self.x, self.y))
            self.hit_timer -= 1
        else:
            surface.blit(self.image, (self.x, self.y)) #normal render if not hit

#enemys will apper in different "waves"
class Wave:
    def spawn(self, enemies, player):
        pass


#enemys from the right!
class WaveFromRight(Wave):
    def __init__(self, monster_base):           #inits the wave from the right
        self.monster_base = monster_base

    def spawn(self, enemies, player):           #spawning process with random y position
        y = random.randint(0, 480)

        color = (                               #we create a random color for every enemy
            random.randint(80, 255),
            random.randint(80, 255),
            random.randint(80, 255)
        )

        colored_sprite = tint_image(self.monster_base, color)

        enemies.append(                         #appending the enemy
            Enemy(640, y, -1, 0, colored_sprite)
        )

#enemys from the left!
class WaveFromLeft(Wave):                       #same process as enemys from the right, but the enemys will come from the left in this wave
    def __init__(self, monster_base):
        self.monster_base = monster_base

    def spawn(self, enemies, player):
        y = random.randint(0, 480)
        color = (
            random.randint(80, 255),
            random.randint(80, 255),
            random.randint(80, 255)
        )
        colored_sprite = tint_image(self.monster_base, color)
        enemies.append(
            Enemy(0, y, 1, 0, colored_sprite)  # dx = 1 => from left to right
        )
        
#enemys from random directions!!
class WaveRandom(Wave):                         #same procress but the enemys are spawned at a random location
    def __init__(self, monster_base):
        self.monster_base = monster_base

    def spawn(self, enemies, player):
        x = random.randint(0, 1024)  
        y = random.randint(0, 768)  

        color = (
            random.randint(80, 255),
            random.randint(80, 255),
            random.randint(80, 255)
        )
        colored_sprite = tint_image(self.monster_base, color)

        #random direction:
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        if dx == 0 and dy == 0:
            dx = 1  #always the same direction

        enemies.append(
            Enemy(x, y, dx, dy, colored_sprite)
        )


#This class manages our different waves (left wave, right wave, random wave), it holds the logic of the waves
class WaveManager:
    def __init__(self):
        self.waves = []                         #we store the waves here   
        self.current_wave = 0   
        self.timer = 0                          #timer for the wave
        self.first_wave_done = False            
        self.difficulty = 1                     #speed at the beginningt
        self.spawn_interval = 120               #base value for the spawns

    def update(self, enemies, player, monster_base):#update function of the wave manager
        self.timer += 1                         #time passes by
        self.difficulty += 0.0005               #every frame it gets more difficult! (more monsters)

        interval = max(int(self.spawn_interval / self.difficulty), 20) 

        if not self.first_wave_done:
            if self.timer > 60:
                self.timer = 0
                wave = WaveFromRight(monster_base)
                wave.spawn(enemies, player)
            if len(enemies) > 10:
                self.first_wave_done = True
                self.timer = 0
        else:
            if self.timer > interval:
                self.timer = 0
                # zufällige Welle auswählen
                wave_class = random.choice([WaveFromRight, WaveRandom, WaveFromLeft])
                wave = wave_class(monster_base)
                # spawn mehrerer Gegner je nach difficulty
                for _ in range(int(self.difficulty)):
                    wave.spawn(enemies, player)

#This class represents the HUD wich shows the informations at the screen like players health, points, weapon and help
class HUD:
    def __init__(self, font):
        self.font = font

    def draw_health(self, surface, player):         #draw function of the health display at the upper left of the screen
        x, y = 10, 10
        width = 180
        height = 18

        # background (gray)
        pygame.draw.rect(surface, (80, 80, 80), (x, y, width, height))

        # fill (red)
        health_ratio = max(player._health / 100, 0)
        pygame.draw.rect(surface, (200, 0, 0), (x, y, width * health_ratio, height))

        # border
        pygame.draw.rect(surface, (255, 255, 255), (x, y, width, height), 2)

        # label
        text = self.font.render("HEALTH", True, (255, 255, 255))
        surface.blit(text, (x, y + 18))

    def draw_points(self, surface, player, width):  #draw function of the users points 
        text = self.font.render(f"POINTS: {player._points}", True, (255, 255, 255))
        surface.blit(text, (width - text.get_width() - 10, 10))

    def draw_weapon(self, surface, player, height): #draw the weapons name 
        weapon_name = player.get_weapon().name.upper()
        text = self.font.render(f"WEAPON: {weapon_name}", True, (255, 255, 255))
        surface.blit(text, (10, height - 25))

    def draw(self, surface, player, width, height): #the global HUD draw function wich calls all the elements draw functions (health, points, )
        self.draw_health(surface, player)
        self.draw_points(surface, player, width)
        self.draw_weapon(surface, player, height)


#the main game class- this is where the magic happends
class Game:
    def __init__(self):                             #init the game: adding the weapons
        self.shotgun = Weapon(0.8, 7, 8, 11, 6, "shotgun")#please checkout the weapon class constructor to understand the different values
        self.mg = Weapon(0.1, 8, 3, 5, 1, "maschine gun")   
        self.rocket = Weapon(0.4, 15, 20, 0, 1, "rocket launcher") 

        # shoot_timer per frame:
        self.shoot_timer = 0
        self.player = RobotPlayer()             
        self.player.set_weapon(random.choice([self.shotgun, self.mg, self.rocket]))
        self.bullets = []
        # we set the windows size and the "internal" rendering size smaller than the window size for a cool retro look
        self.window_width = 1024
        self.window_height = 768
        self.viewport_width = 640
        self.viewport_height = 480
        self.enemies = []
        self.wave_manager = WaveManager()
        self.items = []

    #the game class entry point
    def execute( self ):
        pygame.init()
        #initializing the HUD
        self.font = pygame.font.SysFont("consolas", 18, bold=True)
        self.hud = HUD(self.font)
        #we set the window size here:
        window = pygame.display.set_mode((self.window_width, self.window_height))
        #and here the smaller sized "viewport" of the game - this makes a cool retro "blocky" look
        game_surface = pygame.Surface((self.viewport_width, self.viewport_height))        

        #load the sprites
        try:
            robot = pygame.image.load("robot.png")
        except FileNotFoundError:
            robot = pygame.image.load("assets/robot.png")
        robot = pygame.transform.scale(robot, (40, 40))
        try:
            monster_base = pygame.image.load("monster.png").convert_alpha()
        except FileNotFoundError:
            monster_base = pygame.image.load("assets/monster.png").convert_alpha()
        monster_base = pygame.transform.scale(monster_base, (30, 30))
        try:
            coin_img = pygame.image.load("coin.png").convert_alpha()
        except FileNotFoundError:
            coin_img = pygame.image.load("assets/coin.png").convert_alpha()

        monster_base = pygame.transform.scale(monster_base, (64, 64))
        robot = pygame.transform.scale(robot, (64, 64))

        coin_img = pygame.transform.scale(coin_img, (20, 20))

        try:
            cross_img = pygame.image.load("health.png").convert_alpha()
        except FileNotFoundError:
            cross_img = pygame.image.load("assets/health.png").convert_alpha()

        # Skaliere es auf eine passende Größe (z.B. 20x20 Pixel)
        cross_img = pygame.transform.scale(cross_img, (20, 20))

        # load weapon sprites
        try:
            img_mg = pygame.image.load("mg.png").convert_alpha()
            img_shotgun = pygame.image.load("shotgun.png").convert_alpha()
            img_rocket = pygame.image.load("rocketlauncher.png").convert_alpha()
        except FileNotFoundError:
            # Fallback for assets-folder
            img_mg = pygame.image.load("assets/mg.png").convert_alpha()
            img_shotgun = pygame.image.load("assets/shotgun.png").convert_alpha()
            img_rocket = pygame.image.load("assets/rocketlauncher.png").convert_alpha()

        # scale the sprites
        img_mg = pygame.transform.scale(img_mg, (50, 50))
        img_shotgun = pygame.transform.scale(img_shotgun, (50, 50))
        img_rocket = pygame.transform.scale(img_rocket, (50, 50))


        #init the wave manager which handles the enemys waves
        self.wave_manager.waves.append(WaveFromRight(monster_base))

        #init the booleans for controlling the player sprite
        to_right = False
        to_left = False
        to_upper = False
        to_lower = False

        #init more booleans for the help screen (h pressend) and the game_over
        h_was_pressed = False  
        show_help = False
        game_over = False
        clock = pygame.time.Clock()

        #this is the main gameloop
        while True:
            #if h is pressed we toggle the help screen
            keys = pygame.key.get_pressed()
            if keys[pygame.K_h] and not h_was_pressed:
                show_help = not show_help
            h_was_pressed = keys[pygame.K_h]

            #getting the other keys pressed for player movement
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        to_left = True
                    if event.key == pygame.K_d:
                        to_right = True
                    if event.key == pygame.K_w:
                        to_upper = True
                    if event.key == pygame.K_s:
                        to_lower = True
                    if event.key == pygame.K_ESCAPE:
                        exit()
                #setting the booleans false when key up
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        to_left = False
                    if event.key == pygame.K_d:
                        to_right = False
                    if event.key == pygame.K_w:
                        to_upper = False
                    if event.key == pygame.K_s:
                        to_lower = False
                if event.type == pygame.QUIT:
                    exit()

            #this moves the player when "wasd" is pressed
            if to_right:
                self.player.set_x( self.player.get_x() + self.player.get_velocity())
            if to_left:
                self.player.set_x( self.player.get_x() - self.player.get_velocity())
            if to_upper:
                self.player.set_y( self.player.get_y() - self.player.get_velocity())
            if to_lower:
                self.player.set_y( self.player.get_y() + self.player.get_velocity())

            #Game Over Screen:
            if game_over:
                # dark background
                overlay = pygame.Surface((self.viewport_width, self.viewport_height))
                overlay.fill((0, 0, 0))
                overlay.set_alpha(180) 
                game_surface.blit(overlay, (0, 0))
                #game over font 
                game_over_font = pygame.font.SysFont("consolas", 48, bold=True)
                #set the "GAME OVER" text
                text = game_over_font.render("GAME OVER", True, (255, 0, 0)) 
                game_surface.blit(text, (self.viewport_width//2 - text.get_width()//2,
                                        self.viewport_height//2 - text.get_height()//2 - 50))
                #"Press R to restart text"
                restart_font = pygame.font.SysFont("consolas", 24, bold=True)
                restart_text = restart_font.render("Press [r] to restart", True, (255, 255, 255))
                game_surface.blit(restart_text, (self.viewport_width//2 - restart_text.get_width()//2,
                                                self.viewport_height//2 + 10))
                #scale the text for the cool retro look
                scaled = pygame.transform.scale(game_surface, (self.window_width, self.window_height))
                window.blit(scaled, (0, 0))
                pygame.display.flip()
                
                #check if "r" is pressed for restart the game
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            # Reset alles
                            self.__init__()
                            self.execute()
                    elif event.type == pygame.QUIT:
                        exit()
                
                clock.tick(60)
                continue  #jump to the next frame



            #update the waves:
            self.wave_manager.update(self.enemies, self.player, monster_base)
            #update enemys
            for enemy in self.enemies:
                enemy.update()

            # testing player collision with enemies (player vs enemies):
            #first make the boundingbox for the player
            player_rect = pygame.Rect( 
                self.player.get_x(),
                self.player.get_y(),
                40,
                40
            )

            #loop throug enemies
            for enemy in self.enemies:
                #enemy bonuding box
                enemy_rect = pygame.Rect(enemy.x, enemy.y, 30, 30)

                #simple rect-rect collisoin detection 
                if player_rect.colliderect(enemy_rect):
                    self.player.sub_health(0.2)  #damage per frame
                if self.player._health <= 0:
                    game_over = True            #player is gameover when health <=0

            #Player / Item collision: (for collecting the items)
            for item in self.items[:]:
                #items bounding box:
                item_rect = pygame.Rect(item.x, item.y, 20, 20)

                #append points/health/weapon
                if player_rect.colliderect(item_rect):
                    if isinstance(item, Coin):
                        self.player.add_points(25)

                    if isinstance(item, Cross):
                        self.player.add_health(5)

                    elif isinstance(item, WeaponItem):
                        self.player.set_weapon(item.weapon)  
                    
                    #remove the item when it's taken
                    self.items.remove(item)
                    
            #collision test between bullets and enemys:
            for bullet in self.bullets[:]:
                for enemy in self.enemies[:]:
                    
                    dist = math.hypot(enemy.x - bullet.x, enemy.y - bullet.y)

                    if dist < 35:  # hit radius for normal bullets
                        if bullet.weapon_name == "rocket launcher":
                            # explosions for the rocket launcher
                            explosion_radius = 50
                            for e in self.enemies[:]:
                                dist_to_explosion = math.hypot(e.x - bullet.x, e.y - bullet.y)
                                if dist_to_explosion <= explosion_radius:
                                    e.health -= bullet.damage
                                    e.hit_timer = 5
                                    if e.health <= 0:
                                        self.enemies.remove(e)
                                        self.player.add_points(10)

                                        # DROP SYSTEM: The dead enemy dropps loot:
                                        roll = random.random()
                                        if roll < 0.4:
                                            self.items.append(Coin(e.x, e.y, coin_img))
                                        elif roll < 0.6:
                                            self.items.append(Cross(e.x, e.y, cross_img))
                                        elif roll < 0.7:
                                            new_weapon = random.choice([self.shotgun, self.mg, self.rocket])
                                            if new_weapon == self.mg:
                                                w_img = img_mg
                                            elif new_weapon == self.shotgun:
                                                w_img = img_shotgun
                                            else:
                                                w_img = img_rocket
                                            self.items.append(WeaponItem(enemy.x, enemy.y, new_weapon, w_img))
                            # remove bullet
                            if bullet in self.bullets:
                                self.bullets.remove(bullet)
                            break
                        else:
                            #this is the detection for maschinegun and shotgun bullets
                            enemy.health -= bullet.damage
                            enemy.hit_timer = 5
                            if bullet in self.bullets:
                                self.bullets.remove(bullet)
                            if enemy.health <= 0:
                                self.enemies.remove(enemy)
                                self.player.add_points(10)

                                # DROP SYSTEM: same as in the rocket launcher part above
                                roll = random.random()
                                if roll < 0.4:
                                    self.items.append(Coin(enemy.x, enemy.y, coin_img))
                                elif roll < 0.6:
                                    self.items.append(Cross(enemy.x, enemy.y, cross_img))
                                elif roll < 0.7:
                                    new_weapon = random.choice([self.shotgun, self.mg, self.rocket])
                                    if new_weapon == self.mg:
                                        w_img = img_mg
                                    elif new_weapon == self.shotgun:
                                        w_img = img_shotgun
                                    else:
                                        w_img = img_rocket
                                    self.items.append(WeaponItem(enemy.x, enemy.y, new_weapon, w_img))
                            break

            #fill the game surface
            game_surface.fill((15, 15, 30))
            #create the background lines
            for x in range(0, self.viewport_width, 20):
                pygame.draw.line(game_surface, (30, 30, 30), (x, 0), (x, self.viewport_height))
            for y in range(0, self.viewport_height, 20):
                pygame.draw.line(game_surface, (30, 30, 30), (0, y), (self.viewport_width, y))
            for item in self.items:
                item.draw(game_surface)

            #render the robot/ player:
            game_surface.blit(robot, (self.player.get_x(), self.player.get_y()))

            #render every enemy
            for enemy in self.enemies:
                enemy.draw(game_surface)

            #calculate the direction of the weapon: center of the robot to the mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()

            robot_center_x = self.player.get_x() + robot.get_width() / 2
            robot_center_y = self.player.get_y() + robot.get_height() / 2

            dx = mouse_x - robot_center_x
            dy = mouse_y - robot_center_y

            #calculate the distance
            distance = math.hypot(dx, dy)

            if distance != 0:
                dx /= distance
                dy /= distance

            #draw the weapon as a line with length 15px
            weapon_length = 15 
            end_x = robot_center_x + dx * weapon_length
            end_y = robot_center_y + dy * weapon_length
            pygame.draw.line( game_surface,(255, 0, 0),(robot_center_x, robot_center_y),(end_x, end_y),3 )

            #add bullets with the new direction of the weapon
            if self.shoot_timer <= 0:
                weapon = self.player.get_weapon()
                self.shoot_timer = int(weapon.cooldown * 60)

                # calculate the angle of the direction
                base_angle = math.atan2(dy, dx)

                for i in range(weapon.projectiles):
                    # the angle of the weapon spread (in rad)
                    spread_rad = math.radians(weapon.spread)
                    if weapon.projectiles > 1:
                        #spread the bullets
                        angle = base_angle - spread_rad/2 + i * (spread_rad / (weapon.projectiles - 1))
                    else:
                        angle = base_angle + random.uniform(-spread_rad/2, spread_rad/2)

                    bullet_dx = math.cos(angle)
                    bullet_dy = math.sin(angle)

                    #append the bullets to our bullets list
                    self.bullets.append(
                        Bullet(
                            robot_center_x,
                            robot_center_y,
                            bullet_dx,
                            bullet_dy,
                            weapon.bullet_speed,
                            weapon.damage,
                            weapon_name=weapon.name
                        )
                    )
            self.shoot_timer -= 1

            #update each bullet
            for bullet in self.bullets:
                bullet.update()
                bullet.draw(game_surface)

            #remove bullets outside of the viewport with list comprehension:
            self.bullets = [b for b in self.bullets if 0 <= b.x <= self.viewport_width and 0 <= b.y <= self.viewport_height ]
            self.hud.draw(game_surface, self.player, self.viewport_width, self.viewport_height)
          
            #the help text in the lower right
            hint_font = pygame.font.SysFont("consolas", 18, bold=True)
            hint_text = hint_font.render("press [h] for help", True, (200, 200, 200))
            # calculate the width of the text
            text_width = hint_text.get_width()
            game_surface.blit(hint_text, (self.viewport_width - text_width - 10, self.viewport_height - 25))
            scaled = pygame.transform.scale(game_surface, (self.window_width, self.window_height))
            window.blit(scaled, (0, 0))
            
            #rendering the "help" text when h is pressed
            if show_help:
                        game_surface.fill((20, 20, 50))  
                        help_font = pygame.font.SysFont("consolas", 24, bold=True)
                        help_texts = [
                            "HELP / CONTROLS:",
                            "WASD: move robot",
                            "Mouse: move gun",
                            "ESC: exit",
                            "",
                            "Monsters are dropping items:",
                            "Coin: +10 points",
                            "+: +10 health points",
                            "W: new weapon",
                            "",
                            "SURVIVE AS LONG AS YOU CAN",
                            "",
                            "",
                            "made with <3 by paul berning",
                            "in cologne, germany"

                        ]
                        for i, line in enumerate(help_texts):
                            text = help_font.render(line, True, (255, 255, 255))
                            game_surface.blit(text, (20, 20 + i * 30))

                        #scale it to the windows size
                        scaled = pygame.transform.scale(game_surface, (self.window_width, self.window_height))
                        window.blit(scaled, (0, 0))
                        pygame.display.flip()
                        clock.tick(60)
                        continue  


            pygame.display.flip()

            clock.tick(60)

   

#this is the main program entry point:
if __name__ == "__main__":
    game = Game()           #create the game
    game.execute()          #start the game