import pygame
import neat
import time
import os
import random

pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

GEN = 1

#scale image to 2x size
BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))), 
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))), 
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))

STAT_FONT = pygame.font.SysFont('comicsans', 50)




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


class Pipe:
    GAP = 200 #space b/w pipe ends
    VEL = 15

    def __init__(self,x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) #some pipes facing downward
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.setHeight()

    def setHeight(self):
        self.height = random.randrange(40, 450) #placement of top of pipe
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        birdMask = bird.getMask()
        topMask = pygame.mask.from_surface(self.PIPE_TOP)
        bottomMask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        topOffset = (self.x - bird.x, self.top - round(bird.y))
        bottomOffset = (self.x - bird.x, self.bottom - round(bird.y))

        #check if masks collide via pts of collision
        bPoint = birdMask.overlap(bottomMask, bottomOffset)
        tPoint = birdMask.overlap(topMask, topOffset)

        if tPoint or bPoint: #if any of these pts exist, it means there's a collision
            return True
        
        return False

class Base:
    VEL = 15
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        #horizontal parallax for base
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
        

def drawWindow(win, birds, pipes, base, score, gen):
    win.blit(BG_IMG, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render('Score: '+str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render('Gen: '+str(gen), 1, (255,255,255))
    win.blit(text, (10, 10))

    base.draw(win)
    for bird in birds:
        bird.draw(win) #draw the bird
    pygame.display.update()

#main game loop
def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    birds = []

    #setup a bird and neural network for each genome
    for _, g in genomes:
        #setup neural network
        net = neat.nn.FeedForwardNetwork.create(g, config)
        #append to neural net list
        nets.append(net)
        #append bird to bird list
        birds.append(Bird(230, 350))
        #all fitness of birds are initially to 0, then add to ge list
        g.fitness = 0
        ge.append(g)



    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    run = True
    score = 0
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        
        #take into account when there are 2 pipes on the screen
        pipeIdx = 0
        if len(birds) > 0:
            #if there's more than 1 pipe, just get any bird's x position, and if it has passed the first pipe in the screen, change the pipe we're looking at to the next one
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipeIdx = 1
        else: #if no birds, quit running the game
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            #add small fitness to ecnourage the bird to move forward ant not just go up or down all the way
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipeIdx].height), abs(bird.y - pipes[pipeIdx].bottom)))

            if output[0] > 0.5:
                bird.jump()

        addPipe = False
        
        rem =[]
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

            
                if not pipe.passed and pipe.x < bird.x: 
                    pipe.passed = True
                    addPipe = True
            if pipe.x + pipe.PIPE_TOP.get_width() < 0: #if pipe is outside of screen
                rem.append(pipe)
            pipe.move()
        
        if addPipe:
            score += 1
            for g in ge:
                g.fitness += 3
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0: #if hits the base (height of base) or hits the roof
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        drawWindow(win, birds, pipes, base, score, GEN)
    
    


#setup NEAT
def run(configPath):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, configPath)

    #generate population
    p = neat.Population(config)

    #set output
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    #fitness functiion
    winner = p.run(main,50) #50 generations

if __name__ == '__main__':
    localDir = os.path.dirname(__file__)
    configPath = os.path.join(localDir, 'config-feedforward.txt')
    run(configPath)




