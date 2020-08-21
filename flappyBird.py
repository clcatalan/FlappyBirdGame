import pygame
import neat
import time
import os
import random

WIN_WIDTH = 500
WIN_HEIGHT = 800

#scale image to 2x size
BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))), 
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))), 
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))



class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25 #how much the bird tilts when it moves up or down
    ROT_VEL = 20 #how much rotation in each frame
    ANIMATION_TIME = 5 #how long each bird animation is shown

    def __init__(self,x,y):
        self.x = x #initial positions
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5 #negative because coordinates (0,0) is the top left, so when it jumps, it's supposed to decrease the position w/ respect to y-axis
        self.tick_count = 0 #keeps track of when we last jumped
        self.height = self.y

    def move(self):
        self.tick_count += 1
        #displacement | so in first jump d = -10.5 + 1.5
        d = self.vel*self.tick_count + 1.5*self.tick_count**2

        #implement "terminal velocity"

        #if we're moving down too fast, just maintain constant displacement of 16
        if d >= 16:
            d = 16
        #if moving too fast upward, and reaches the limit, just move up a little bit more upward constantly
        if d < 0:
            d -=2

        self.y = self.y + d

        #tilting upwards
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        #tilting downwards
        else:
            if self.tilt >  -90: 
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 2 #to keep track of how many ticks we've shown a current image for

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4+1:
            self.img = self.IMGS[0]
            self.img_count = 0

        #when it falls down, bird should just stay the same and not flap its wings
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2 #chose ANIMATION_TIME*2 so it wont look like it skipped a frame

        #rotate image around its center
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)    #blit = draw the image | what this line does is rotate the image

    #gets collision
    def getMask(self):
        return pygame.mask.from_surface(self.img)


def drawWindow(win, bird):
    win.blit(BG_IMG, (0,0))
    bird.draw(win) #draw the bird
    pygame.display.update()

#main game loop
def main():
    bird = Bird(200,200)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        #bird.move()
        drawWindow(win, bird)
    
    pygame.quit()
    quit()

main()




