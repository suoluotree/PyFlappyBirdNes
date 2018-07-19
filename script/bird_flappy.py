# !/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append("../lib/")
import pygame
import flappy_bird_utils
import time
import random
from itertools import cycle
import nn_es

FPS = 23 #控制帧速度, 30fps
SCREENWIDTH  = 288
SCREENHEIGHT = 512

pygame.init()
FPSCLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Flappy Bird')


# 字体大小
TEXTSIZE = 40
TEXTINTERVAL = 2
CORLOR_WHITE = (255, 255, 255)

IMAGES, HITMASKS = flappy_bird_utils.load()
PIPEGAPSIZE = 100 # gap between upper and lower part of pipe
BASEY = SCREENHEIGHT * 0.79

PLAYER_WIDTH = IMAGES['player'][0].get_width()
print "player width: %s" % PLAYER_WIDTH
PLAYER_HEIGHT = IMAGES['player'][0].get_height()
print "player height: %s" % PLAYER_HEIGHT
PIPE_WIDTH = IMAGES['pipe'][0].get_width()
print "pipe width: %s" % PIPE_WIDTH
PIPE_HEIGHT = IMAGES['pipe'][0].get_height()
print "pipe height: %s" % PIPE_HEIGHT
BACKGROUND_WIDTH = IMAGES['background'].get_width()
BACKGROUND_HEIGHT = IMAGES['background'].get_height()

BIRD_INDEX_GEN = cycle([0, 1, 2, 1])

def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    #print rect1.width, rect1.height
    #print rect2.width, rect2.height
    rect = rect1.clip(rect2)
    #print rect.width, rect.height

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    #print "x1, y1: ", x1, y1
    #print "x2, y2: ", x2, y2
    for x in range(rect.width):
        for y in range(rect.height):
            #print "x, y: ", x, y
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False

class Bird():
  def __init__(self):
    self.x = int(SCREENWIDTH * 0.16)
    self.y = int((SCREENHEIGHT - PLAYER_HEIGHT) / 2)
    self.width = PLAYER_WIDTH
    self.height = PLAYER_HEIGHT

    self.alive = True
    self.gravity = 0
    self.velocity = 0.3
    self.jump = -6
    self.index = 0

  def flap(self):
    print "bird %s flap" % self.index
    self.gravity = self.jump

  def update(self, direct=0, velocity=0):
    print "bird %s before update: gravity-%s, y-%s, v-%s" % (self.index, self.gravity, self.y, velocity)
    self.gravity += self.velocity
    self.y += self.gravity
    print "bird %s after update: gravity-%s, y-%s" % (self.index, self.gravity, self.y)
    return

  def isDead(self, height, upperPipes, lowerPipes):
    if ((self.y + self.height) >= height) or (self.y <= 0):
      return True

    bird_rect = pygame.Rect(self.x, self.y, self.width, self.height)
    for uPipe, lPipe in zip(upperPipes, lowerPipes):
      uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], PIPE_WIDTH, PIPE_HEIGHT)
      lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], PIPE_WIDTH, PIPE_HEIGHT)
      pHitMask = HITMASKS['player'][0]
      uHitmask = HITMASKS['pipe'][0]
      lHitmask = HITMASKS['pipe'][1]

      uCollide = pixelCollision(bird_rect, uPipeRect, pHitMask, uHitmask)
      lCollide = pixelCollision(bird_rect, lPipeRect, pHitMask, lHitmask)

      if uCollide or lCollide:
        return True

    return False

class Game():
  def __init__(self):
    self.width = SCREENWIDTH
    self.height = SCREENHEIGHT

    self.upperPipes = []
    self.lowerPipes = []
    self.pipesInit()
    self.birds = []
    self.alive_bird = 0

    #self.Neuvol = nn_es.Neuroevolution([2, [16, 8, 4], 3], 50)
    self.Neuvol = nn_es.Neuroevolution([3, [4], 1], 50)
    self.generation = 0
    self.loopIter = 0
    self.interval = 0
    self.spawnInterval = 90

    self.score = 0
    self.max_score = 0

    self.pipe_velx = -4
    self.gen = []
    self.bird_img_index = 0
    return

  def pipesInit(self):
    newPipe1 = self.getRandomPipe()
    newPipe2 = self.getRandomPipe()
    self.upperPipes = [
        {'x': SCREENWIDTH, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + (0.66 * SCREENWIDTH), 'y': newPipe2[0]['y']},
    ]
    self.lowerPipes = [
        {'x': SCREENWIDTH, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + (0.66 * SCREENWIDTH), 'y': newPipe2[1]['y']},
    ]

  def gameOver(self):
    for bird in self.birds:
      if bird.alive == True:
        return False
    return True

  def start(self):
    self.interval = 0
    self.score = 0
    self.birds = []
    self.gen = self.Neuvol.nextGeneration()
    for i in range(len(self.gen)):
      bird = Bird()
      bird.index = i
      self.birds.append(bird)
    self.generation += 1
    print "=====generation %s======" % self.generation
    self.alive_bird = len(self.birds)
    self.pipesInit()
    return

  def update(self):
    next_holl = 0
    for pipe in self.lowerPipes:
      if (pipe['x'] + PIPE_WIDTH) > self.birds[0].x:
        next_holl = float(pipe['y']) / float(self.height)
        break

    self.pipeUpdate()

    for i in range(len(self.birds)):
      bird = self.birds[i]
      if bird.alive != True:
        continue
      print "bird position: ", bird.x
      print "pipe position: ", pipe['x'] + PIPE_WIDTH
      inputs = [float(bird.x) / float(pipe['x'] + PIPE_WIDTH), float(bird.y) / float(self.height), next_holl]
      #inputs = [bird.y / self.height, next_holl]
      print "network input is: ", inputs
      res = self.gen[i].compute(inputs)
      if res[0] > 0.5:
        bird.flap()
      print "bird i-%s, x-%s, y-%s, res-%s" % (bird.index, bird.x, bird.y, res[0])
      bird.update()
      print "bird i-%s, x-%s, y-%s, res-%s" % (bird.index, bird.x, bird.y, res[0])
      if bird.isDead(self.height, self.upperPipes, self.lowerPipes):
        bird.alive = False
        self.alive_bird -= 1
        print "dead bird %s: score-%s" % (i, self.score)
        self.Neuvol.networkScore(self.gen[i], self.score)
        if self.gameOver():
          self.start()

    self.interval += 1
    if self.interval == self.spawnInterval:
      self.interval = 0

    self.score += 1
    if self.score > self.max_score:
      self.max_score = self.score

    return

  def display(self):
    pygame.event.pump()
    # 背景渲染
    SCREEN.blit(IMAGES['background'], (0,0))

    # 管子渲染
    for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
      SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
      SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

    # 小鸟渲染
    if (self.loopIter + 1) % 3 == 0:
      self.bird_img_index = next(BIRD_INDEX_GEN)
    for bird in self.birds:
      if bird.alive != True:
        continue
      SCREEN.blit(IMAGES['player'][self.bird_img_index], (bird.x, bird.y))

    display_text = ["Score: %s" % self.score,
                    "Max score: %s" % self.max_score,
                    "Generations: %s" % self.generation,
                    "Alive birds: %s" % self.alive_bird]

    for i in range(len(display_text)):
      self.message_display(display_text[i], i)
    pygame.display.update()
    FPSCLOCK.tick(FPS)
    self.loopIter += 1
    if self.loopIter >= 10000000:
      self.loopIter = 0
    return

  def getRandomPipe(self):
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapYs = [20, 40, 60, 80, 100, 120, 140]
    index = random.randint(0, len(gapYs)-1)
    gapY = gapYs[index]

    gapY += int(BASEY * 0.2)
    pipeX = SCREENWIDTH + 0.66 * SCREENWIDTH

    return [
        {'x': pipeX, 'y': gapY - PIPE_HEIGHT},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE},  # lower pipe
    ]

  def pipeUpdate(self):
    for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
      uPipe['x'] += self.pipe_velx
      lPipe['x'] += self.pipe_velx

    if 0 < self.upperPipes[0]['x'] < 5:
      newPipe = self.getRandomPipe()
      self.upperPipes.append(newPipe[0])
      self.lowerPipes.append(newPipe[1])

    if self.upperPipes[0]['x'] < -PIPE_WIDTH:
      self.upperPipes.pop(0)
      self.lowerPipes.pop(0)
    return

  def message_display(self, text, index):
    large_text = pygame.font.Font(None, TEXTSIZE)
    text_surface = large_text.render(text, True, CORLOR_WHITE)
    pos_y = (index + 1) * TEXTINTERVAL + index * TEXTSIZE
    SCREEN.blit(text_surface, (TEXTINTERVAL, pos_y))
    return
    

def main():
  game = Game()
  game.start()
  while True:
    game.update()
    game.display()
  return

if __name__ == "__main__":
  main()
