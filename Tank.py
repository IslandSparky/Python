''' Tanks - beta version by Darwin I and Darwin II
    ver 0.1 intitial beta test the committ '''

import pygame, sys, time, random,math
from pygame.locals import *

pygame.init()


WHITE =  (255,255,255)
YELLOW = (255,255,0)
LIGHTYELLOW = (128,128,0)
RED = (255, 0 ,0)
LIGHTRED = (128,0,0)
BLUE = (0, 0, 255)
LIGHTBLUE = (0, 0, 128)
GREEN = (0,255,0)
LIGHTGREEN = (0, 128, 0)
BACKGROUND = (0,0,0)

WINDOWWIDTH = 1250
WINDOWHEIGHT = 750

NUMBERMINES = 5     # NUMBER OF MINES TO SPRINKLE AROUND
NUMBERROBOTS = 10     # NUMBER OF ROBOT TANKS TO SPRINKLE AROUND
BULLETSPEED = 10     # SPEED OF THE BULLET IN PIXELS PER UPDATE

windowSurface = pygame.display.set_mode([WINDOWWIDTH, WINDOWHEIGHT])
pygame.display.set_caption('Tanks')

#-------------------- Tank Class ver 0.2------------------------------------------
class Tank(object):
# Tank class to define a battle tank. Turret direction indicates move and shoot
# direction for now:

    tanks = []  # list of all tank objects

    def move_all():
    # Tank class method to move all the active tanks
        for tank in Tank.tanks:
            tank.move()

        return # return from Tank.move_all

    def  __init__(self,center=(500,500),color=YELLOW,size=25,direction = 90,
                  lives=5,ammo=25,speed=0):

    # This is the initializer called each time you create a new tank.
    # The size is specified as a single variable because the tank is drawn
    # in a square.
        self.color = color
        self.size = size
        self.direction = direction # direction the tank (and gun) is pointed
        self.lives = lives  # number of lives we have
        self.ammo = ammo    # number of rounds we can fire in each life

        self.speed = speed
        self.home = center  # remember center as the home base

        # add this tank to the list of tanks
        Tank.tanks.append(self)


        # dx and dy are the distance accumulators for the distance not moved
        # by the integer pixel count
        self.dx = 0.
        self.dy = 0.

        # build a rectangle for this tank and save as an attribute
        # center was given rather than topleft, so adjust for half the size
        self.rect = pygame.Rect(center[0]-int(size/2),
                                center[1]-int(size/2),size,size)
        

        # now draw the tank
        self.draw()

        return # return from Tank.__init__

    def draw(self):
    # Tank method to draw the tank. Does not update the display.
        pygame.draw.rect(windowSurface,BACKGROUND,self.rect,0) # erase old
        pygame.draw.rect(windowSurface,self.color,self.rect,1) # tank outline
        pygame.draw.circle(windowSurface,self.color,self.rect.center,
                           int(self.size/3),2) # draw turret

        # draw the gun. Starts in center but must compute the endpoint

        gunlength = self.size/2-1
        dx = math.cos(self.direction/57.4) * gunlength  # x increment
        dy = -math.sin(self.direction/57.4) * gunlength  # y increment
        gunend = (self.rect.center[0]+dx, self.rect.center[1]+dy)
        pygame.draw.line(windowSurface,self.color,self.rect.center,
                         gunend,2)
       

        return # return from Tank.draw

    def move(self):
    # move method for the Tank Class, returns True if stuck against something
        stuck = False   # default to not stuck against something
        if self.lives <= 0: # do nothing if you are already dead
            return stuck  # return not stuck
    # Tank method to move the tank in the direction indicated by gun
        pygame.draw.rect(windowSurface,BACKGROUND,self.rect,0) # erase old

        olddx = self.dx
        olddy = self.dy

        self.dx = self.dx + math.cos(self.direction/57.4) * self.speed # x increment
        self.dy = self.dy - math.sin(self.direction/57.4) * self.speed # y increment

        self.rect.center = (self.rect.center[0]+int(self.dx),
                            self.rect.center[1]+int(self.dy))

        # if we hit a wall or a barrier, reverse out the move

        if ( (check_wall(self.rect) != None) |
              check_barrier(self.rect) ):
            stuck = True
            self.rect.center = (self.rect.center[0]-int(self.dx),
                                self.rect.center[1]-int(self.dy))
            self.dx = olddx
            self.dy = olddy
        else:
            self.dx -= int(self.dx) 
            self.dy -= int(self.dy)

        # check to see if we hit a mine and, if so, die
        if Mine.check_all(self.rect): # if True, hit live mine
            explode(self.rect.center,self.color,
                    radius=self.rect.size[0])
            self.draw() # leave the dead tank here
            if (self.lives >0):
                self.lives -= 1 # kill him
                if (self.lives >0): # leave him here if dead
                    self.rect.center = self.home # send him home
                    self.speed = 0  # at zero speed
                    self.direction = 90 # pointing up
                    update_scores(Tank.tanks[0],Tank.tanks[1]) # show updated scoreboard
 
        self.draw()

        return stuck # return from move, with stuck True or False

    def speed_up(self):
    # Tank method to increase the speed. Can't go more than MAXSPEED

        MAXSPEED = 3

        
        if self.speed < MAXSPEED:
            self.speed += 1

        return  # return from Tank.speed_up

    def brake(self):
    # Tank method to slow down

        
        if self.speed > 0:
            self.speed -= 1

        return # return from Tank.brake

    def turn(self,turn_angle):
    # Tank method to turn the turret and direction by angle_change
    # angle_change in degrees- plus is counter_clockwise

        self.direction += turn_angle
        if self.direction < 0:
            self.direction += 360
        elif self.direction > 360:
            self.direction -= 360

    def shoot(self,max_range=int(WINDOWWIDTH/BULLETSPEED)):
    # Tank method to fire the main gun. All tank movement stops while the bullet
    # is in flight. If a tank is hit, the handle to that tank is returned.
    # otherwise None is returned

        if self.lives <= 0: # do nothing if you are already dead
            return None

    
        color = self.color  # bullet color same as tank
        bullet_speed = BULLETSPEED
        bullet_wait = .005   # time between bullet updates
        track_max = 10      # maximum length of track to keep
        track = []
        rect = pygame.Rect(self.rect.center[0],self.rect.center[1],2,2) # define bullet
        pygame.draw.rect(windowSurface,color,rect,0) # initial draw
        dx = 0
        dy = 0
        direction = self.direction
        if self.ammo >0:
            self.ammo -= 1  # subtract this round from the ammo on board
        else:
            return  # out of bullets

        for i in range(0,int(max_range) ):
        
            dx = dx + math.cos(direction/57.4) * bullet_speed # x increment
            dy = dy - math.sin(direction/57.4) * bullet_speed # y increment

            rect.center = (rect.center[0]+int(dx),
                                rect.center[1]+int(dy))
            dx -= int(dx) 
            dy -= int(dy)
            pygame.draw.rect(windowSurface,color,rect,0) # draw bullet
            pygame.display.update()

            # save the current center in track memory
            center_now = rect.center  # remember where we are
            track.append(center_now)

            # if track length is maxed out, start blanking old track
            if(len(track) > track_max):
                rect.center = track[0] # blank out the oldest track
                pygame.draw.rect(windowSurface,BACKGROUND,rect,0)
                pygame.display.update()
                del track[0] # delete the oldest track position
                rect.center = center_now  # restore current position

            # see if we hit a wall and, if so, bounce off
            wall = check_wall(rect)
            if ( (wall == 'RIGHT') | (wall == 'LEFT') ):
                wall_hit = True
                direction=180-direction
            elif( (wall == 'TOP') | (wall == 'BOTTOM') ):
                wall_hit = True
                direction=360 - direction

            # see if we hit a tank, and if so, explode and return the tank
            # object, don't start test until bullet is on the way
            if i > 3: # let bullet leave the shooter or else kill yourself
                for tank in Tank.tanks:
                    if rect.colliderect(tank): # see if we hit a tank
                        # tank hit, blow him up, kill him and start new life
                        explode(tank.rect.center,tank.color,
                                radius=tank.rect.size[0])
                        if (tank.lives >0):
                            tank.lives -= 1 # kill him
                            if (tank.lives >0): # leave him here if dead
                                tank.rect.center = tank.home # send him home
                                tank.speed = 0  # at zero speed
                                tank.direction = 90 # pointing up
                                tank.draw()
                
                        # clean track
                        clean_track(rect,track)
                        return tank

            # see if we hit a barrier. If so, explode and return no tank hit
            for barrier in Barrier.barriers:
                if rect.colliderect(barrier):
                    explode(rect.center,color,radius=20)
                    clean_track(rect,track)
                    return None
            # wait a bit so we can follow the bullet
            time.sleep(bullet_wait)

        # loop ended at end of range with no hit or break out on a barrier
        # wipe out remaining track
        clean_track(rect,track)

        # no tank hit, return None
        return None

#-----------------End of Tank Class----------------------------------------

#---------------------Robot Tank Class ver 0.2--------------------------------------
# Inherited class of Tank for robot tanks
class Robot_Tank(Tank):

    def  __init__(self,center=(500,500),color=GREEN,size=25,
                  lives=1,ammo=10,speed=1,max_range=WINDOWWIDTH/10):

    # This is the initializer called each time you create a new robot tank.
    # The size is specified as a single variable because the tank is drawn
    # in a square.
        self.color = color
        self.size = size
        self.direction = random.randrange(0,359) # direction the tank (and gun) is pointed
        self.lives = lives  # number of lives we have
        self.ammo = ammo    # number of rounds we can fire in each life
        self.speed = speed
        self.max_range = max_range

        self.target = None  # initially not locked, otherwise hold target tank
    
        self.home = center  # remember center as the home base

        # add this tank to the list of tanks
        Tank.tanks.append(self)


        # dx and dy are the distance accumulators for the distance not moved
        # by the integer pixel count
        self.dx = 0.
        self.dy = 0.

        # build a rectangle for this tank and save as an attribute
        # center was given rather than topleft, so adjust for half the size
        self.rect = pygame.Rect(center[0]-int(size/2),
                                center[1]-int(size/2),size,size)
        

        # now draw the tank
        self.draw()

        return # return from Robot_Tank.__init__

    def move(self):
    # Overload the tank move class so we can check for special actions for the
    # robot.  It calls the Tank class move and shoot methods to do the actual
    # work.



        # if not locked on target, choose a live one at random
        while self.target == None:
            index = random.randrange(0,len(Tank.tanks))  # only lock on to first two tanks
            if  ((Tank.tanks[index] != self) &
               (Tank.tanks[index].lives >0)):   # see if this tank is still alive
                    self.target = Tank.tanks[index] # live duck, latch on


        #*************
        # compute the angle to the target        
        #*************
       

        x = self.rect.center[0]
        y = self.rect.center[1]
        targetx = self.target.rect.center[0]
        targety = self.target.rect.center[1]

        # find the x and y distance to the target

        xtotarget = targetx - x
        ytotarget = -(targety - y)

      
        # compute direction to target
        if (xtotarget == 0) :  # avoid infinite atan function
            xtotarget = 1  # avoid a divide by zero
        self.direction = 57.4 * math.atan(ytotarget/xtotarget)
        if xtotarget < 0:
            self.direction = self.direction + 180

        # distance to target
        distancetotarget = math.sqrt(xtotarget**2+ ytotarget**2)

        # if target in range of our short gun, shoot and unlock from him
        if abs(distancetotarget) < self.max_range:
            self.shoot(max_range = self.max_range)
            self.target = None

        

        # Move, if we hit something, spin around in a random direction
        # and unlock from any targets.
        stuck = Tank.move(self)
        if stuck == True:  # True means we are stuck against something
            self.direction = random.randrange(0, 359) # spin to random direction
            self.target = None  # unlock from any targets




        return # return from Robot_Tank.move


#----------------   End of Robot_Tank class -------------------------------
    

#------------------- Barrier Class ver 0.1 ------------------------------------

class Barrier(object):

    barriers = []   # hold the list of barriers

    def __init__(self,left=300,top=300,size=(30,70),color=WHITE):
    # initializer for barrier, called when one is created
        self.color = color # save color as attribute
    
        # Add to list of barriers
        Barrier.barriers.append(self)


        # build a rectangle for this barrier and save as attribute
        self.rect = pygame.Rect(left,top,size[0],size[1])

        # now draw the barrier
        self.draw()

        return # return from Barrier.__init__

    def draw(self):
    # Barrier method to draw the barrier. Does not update the display.

        pygame.draw.rect(windowSurface,self.color,self.rect,1) # Barrier outline

        return # return from Barrier.draw

#------------------- Mine Class ver 0.1 ---------------------------------------

class Mine(object):

    mines = []   # hold the list of mines
    last_shown = time.time()  # when mines were last shown

    def show_all():
    #Called at the Mine class level to show all the mines
        for i in range( 0,len(Mine.mines) ):
            Mine.draw(Mine.mines[i])
        return # return from Mine.show_all

    def hide_all():
    # Called at the Mine class level to hide all the mines
        for i in range( 0,len(Mine.mines) ):
            Mine.hide(Mine.mines[i])

        Mine.last_shown = time.time()
        return # return from Mine.hide_all
    
    def flash_all(period = 10, flashtime = 1):
    # Called at the Mine Class level to give a glimpse of the mine locations
    # once in a while.  It's up to you to remember where you saw them.

        deltatime = time.time()-Mine.last_shown

        if deltatime >= period:
            Mine.show_all()  # make them all visible
            time.sleep(flashtime) # wait for the flash time
            Mine.hide_all() # hide them again
            Mine.last_shown = time.time() # reset time for next flash

        return  # return from Mine.flash_all
        
    def check_all(rect):
    # Called aat the mine class level to see if the specified rectangle
    # collides with a mine.  If so, return true and disarm the mine (assume it
    # explodes).  Otherwise, return false

        for i in range( 0,len(Mine.mines) ):
            if ( (rect.colliderect(Mine.mines[i].rect) > 0) &
                 (Mine.mines[i].armed == True) ): # hit a live mine
                    Mine.mines[i].armed = False # disarm, assume it explodes
                    return True # return that you hit a mine

        # no hits found, return False
        return False  # end of Mine.check_all
                
            

    def __init__(self,center=(300,300),size= 10,color=BLUE):
    # initializer for mine, called when one is created
        self.color = color # save color as attribute
        self.armed = True # arm the mine
    
        # Add to list of barriers
        Mine.mines.append(self)


        # build a rectangle for this mine and save as attribute
        self.rect = pygame.Rect(center[0]-int(size/2),center[1]-int(size/2),
                                size,size)

        return # return from Barrier.__init__

    def draw(self):
    # Mine method to draw the mine. Does update the display

        pygame.draw.rect(windowSurface,self.color,self.rect,0) # draw mine
        pygame.display.update()   # update display

        return # return from Mine.draw

    def hide(self):
    # Mine method to hide the mine.Does update the display
        pygame.draw.rect(windowSurface,BACKGROUND,self.rect,0) # hide mine
        pygame.display.update()   # update display    



#---------------- General purpose functions not part of a class ver 0.1 ---------
    
def check_wall(rect):
# General purpose function to test if an  hit a wall.
# Call with a rectangle object
# Returns None if no wall struck, otherwise 'TOP','BOTTOM','RIGHT','LEFT'
    if (rect.right >= WINDOWWIDTH):
        return 'RIGHT'
    elif (rect.left <= 0):
        return 'LEFT'
    elif (rect.top <= 0):
        return 'TOP'
    elif (rect.bottom >= WINDOWHEIGHT):
        return 'BOTTOM'
    else:
        return None

def check_barrier(rect):
# General purpose function to test if an  hit a barrier.
# Call with a rectangle object
# Returns None if no wall struck, otherwise True

    # Run through the list of barriers to see if we hit one
    for barrier in Barrier.barriers:
        if rect.colliderect(barrier.rect):
            return True

    return False
    
def explode(center,color=YELLOW,radius=50):
# General purpose function to create an explosion of a given radius and color
# at a location specified by a (x,y) center location tuple

    for i in range(10,radius,5):
        pygame.draw.circle(windowSurface,color,center,
                           i,2)
        pygame.display.update()
    

    return # return from explode

def clean_track(rect,track):
# General purpose function to clean up the track left by a bullet (or any other
# rectangle object).  Arguments are the rectangle leaving the track and the
# list of previous track centers.

    for i in range(0,len(track)):

        rect.center = track[0] # get oldest center
        pygame.draw.rect(windowSurface,BACKGROUND,
                         rect,0)
        pygame.display.update()
        del track[0] # delete the oldest track position

    return # end of clean track

def write_text(text='TEXT TEST',topleft=(200,200),font_size=50,color=YELLOW):
# General purpose function to write text on the screen
    myfont = pygame.font.SysFont(0,font_size)#setting for the font size
    label = myfont.render(text, 1,color)#("text",alias flag, color
    textrec = label.get_rect()  # get a rectangle to put it in
    textrec.left = topleft[0]  # set the position
    textrec.top = topleft[1]

    windowSurface.blit(label,textrec)#put the text rec onto the surface
    pygame.display.update()

    return  # end of write text

def update_scores(tank1,tank2):
# Special purpose routine to write the tank scores in blocks in preassigned
# locations
    box_x_size = 140
    box_y_size =45

    tank1_lives_topleft = (WINDOWWIDTH-150,25)
    tank1_ammo_topleft = (WINDOWWIDTH-150,50)

    tank2_lives_topleft = (25,25)
    tank2_ammo_topleft = (25,50)

    # create rectangle to use to blank the score boxes
    rect = pygame.Rect(0,0,box_x_size,box_y_size)

    # place over tank1 scores and blank them
    rect.topleft = tank1_lives_topleft
    pygame.draw.rect(windowSurface,BACKGROUND,rect,0) # erase old tank1 score

    # place over tank2 scores and blank them
    rect.topleft = tank2_lives_topleft
    pygame.draw.rect(windowSurface,BACKGROUND,rect,0) # erase old tank2 score    

    
    write_text(text='Tank2 lives left '+str(tank2.lives),topleft=tank2_lives_topleft,
               font_size=25,color=RED)
    write_text(text='Tank2 ammo '+str(tank2.ammo),topleft=tank2_ammo_topleft,
               font_size=25,color=RED)

    write_text(text='Tank1 lives left '+str(tank1.lives),
               topleft= tank1_lives_topleft,              
               font_size=25,color=YELLOW)
    write_text(text='Tank1 ammo '+str(tank1.ammo),
               topleft=tank1_ammo_topleft,              
               font_size=25,color=YELLOW)

    pygame.display.update()


    return # return from update scores
 

#---------------End of general purpose functions --------------------            

#----------------Main portion of the program ver 0.2 --------------------
# Initialize things before the loop

pygame.key.set_repeat(500,50) # 500 msec 'til repeat then 20 times a second

# Create the tanks
tank1_home = ( WINDOWWIDTH-100,int(WINDOWHEIGHT/2))
tank1 = Tank(direction=90,speed=0,color=YELLOW,
             center=tank1_home,lives=5,ammo=60 )

tank2_home = (100,int(WINDOWHEIGHT/2))
tank2 = Tank(direction=90,speed=0,color=RED,
             center =tank2_home,lives=5,ammo=60)

# Create the barriers, starting with the home barriers
Barrier(left=tank1_home[0]-25,top=tank1_home[1]-50,size=(10,100),color=WHITE)
Barrier(left=tank2_home[0]+25,top=tank1_home[1]-50,size=(10,100),color=WHITE)

Barrier(left=500,top=250,size=(20,75),color=WHITE)  # create a barrier for test

# Create the rest of the barriers, either in known places or random locations

# Create some robot hunter killer tanks for interest
if NUMBERROBOTS > 0:
    for i in range(0,NUMBERROBOTS):
        Robot_Tank( center=( random.randrange(200,WINDOWWIDTH-200),
                      random.randrange(50,WINDOWHEIGHT-50) ),
                      color=GREEN )    
# Create the mines and show them for a few seconds, then hide
if NUMBERMINES > 0:
    for i in range(0,NUMBERMINES):
        Mine( center=( random.randrange(200,WINDOWWIDTH-200),
                      random.randrange(50,WINDOWHEIGHT-50) ),
                      size=10,color=BLUE )

Mine.flash_all(period=0,flashtime=5) # give folks a peek to start with

#  Main game loop, runs until window x'd out or someone wins
update_scores(tank1,tank2)   # put up initial scores

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    
        if event.type is KEYDOWN:

            key = pygame.key.name(event.key)

            if(key == 'right'):
                tank1.turn(turn_angle = -2)
            elif(key == 'down'): # shift down one gear
                tank1.brake()
            elif(key == 'left'):
                tank1.turn(turn_angle = +2)
            elif(key == 'up'):  # shift up one gear
                tank1.speed_up()
            elif(key == 'end'): # shoot key - change as desired
                tank1.shoot()
                update_scores(tank1,tank2)


          #************** put in logic for second tank keys *****************          

    # check for end of game
    if (tank1.lives < 1) | (tank2.lives < 1): # see if either one is dead
        # check for tank 1 win
        if (tank2.lives < 1):
            write_text(text= 'YELLOW TANK WINS',
                       topleft=(250,250),font_size=90,color=YELLOW)
        elif (tank1.lives < 1):
            write_text(text= 'RED TANK WINS',
                       topleft=(250,250),font_size=90,color=RED)

        
        time.sleep(5) # display winning message for 5 seconds
        pygame.quit()
        sys.exit()
        
    # do the routine update things each time through the main loop   
    Mine.flash_all(period=15,flashtime=1) # maybe give a peek at mines   
    Tank.move_all()
    pygame.display.update()
    time.sleep(.05)


sys.exit() # shouldn't ever get here.  Exit is in main loop.
        

