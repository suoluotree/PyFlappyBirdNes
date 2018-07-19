# !/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import random
import math
import copy

def randomClamped():
  return random.random() * 2 - 1;

"""
神经元定义
"""
class Neuron():
  def __init__(self):
    self.value = 0
    self.weights = []
    return

  def populate(self, weight_num):
    for i in range(weight_num):
      self.weights.append(randomClamped())
    return


"""
网络层定义
"""
class Layer():
  def __init__(self, index):
    self.id = index
    self.neurons = []
    return

  def populate(self, neuron_num, input_num):
    for i in range(neuron_num):
      neuron = Neuron()
      neuron.populate(input_num)
      self.neurons.append(neuron)
    return

"""
网络定义
"""
class Network():
  def __init__(self):
    self.layers = []

  def activation(self, sum):
    ap = (-sum) / 1.0
    return 1.0 / (1.0 + math.exp(ap))

  def perceptronGeneration(self, inputs, hiddens, outputs):
    index = 0
    previousNeurons = 0
    layer = Layer(index)
    layer.populate(inputs, previousNeurons)
    self.layers.append(layer)
    index += 1
    previousNeurons = inputs
    for i in range(len(hiddens)):
      layer = Layer(index)
      layer.populate(hiddens[i], previousNeurons)
      previousNeurons = hiddens[i]
      self.layers.append(layer)
      index += 1
    layer = Layer(index)
    layer.populate(outputs, previousNeurons)
    self.layers.append(layer)

    return

  def readSave(self):
    datas = {"neurons": [], "weights": []}
    for i in range(len(self.layers)):
      datas["neurons"].append(len(self.layers[i].neurons))
      for j in range(len(self.layers[i].neurons)):
        for weight in self.layers[i].neurons[j].weights:
          datas["weights"].append(weight)
    return datas

  def save(self, save_data):
    previousNeurons = 0
    index = 0
    index_weights = 0
    self.layers = []
    for i in range(len(save_data["neurons"])):
      layer = Layer(index)
      layer.populate(save_data["neurons"][i], previousNeurons)
      for j in range(len(layer.neurons)):
        for k in range(len(layer.neurons[j].weights)):
          layer.neurons[j].weights[k] = save_data["weights"][index_weights]
          index_weights += 1
      previousNeurons = save_data["neurons"][i]
      index += 2
      self.layers.append(layer)

  def compute(self, inputs):
    for i in range(len(inputs)):
      if self.layers[0] and self.layers[0].neurons[i]:
        self.layers[0].neurons[i].value = inputs[i]

    pre_layer = self.layers[0]
    layer_num = len(self.layers)
    for i in range(1, layer_num):
      for j in range(len(self.layers[i].neurons)):
        sum = 0
        for k in range(len(pre_layer.neurons)):
          sum += pre_layer.neurons[k].value * self.layers[i].neurons[j].weights[k]
        self.layers[i].neurons[j].value = self.activation(sum)
      pre_layer = self.layers[i]

    out = []
    last_layer = self.layers[layer_num - 1]
    for i in range(len(last_layer.neurons)):
      out.append(last_layer.neurons[i].value)
    return out

class Genome():
  def __init__(self, score, network):
    self.score = score
    self.network = network

class Generation():
  def __init__(self, sort=-1, population=50):
    self.genomes = []
    self.scoreSort = sort
    # 下一代变异的概率
    self.mutationRate = 0.1
    # 变异后网络weight的范围
    self.mutationRange = 0.5
    # 种群数量，多少个小鸟
    self.population = population
    # 下一代中有多少比例的最好的网络结构会被保留
    self.elitism = 0.2
    # 新的随机生成的网络结构占下一代的比例
    self.randomBehaviour = 0.2
    # 基因交叉后生成的孩子个数
    self.nbChild = 1

  def addGenome(self, genome):
    genome_len = len(self.genomes)
    insert_pos = -1
    self.genomes.append(Genome(0, []))
    for i in range(genome_len):
      # 降序插入
      if self.scoreSort == -1:
        if genome.score > self.genomes[i].score:
          insert_pos = i
          break
      # 升序插入
      else:
        if genome.score < self.genomes[i].score:
          insert_pos = i
          break

    if insert_pos >= 0:
      move_pos = (genome_len - 1)
      while move_pos >= insert_pos:
        self.genomes[move_pos + 1] = self.genomes[move_pos]
        move_pos -= 1
      self.genomes[insert_pos] = genome
    else:
      self.genomes[genome_len] = genome

    #print "after insert: insert pos %s" % insert_pos
    score_list = []
    for item in self.genomes:
      #print item.network
      score_list.append(str(item.score))

    #print ", ".join(score_list)

  def breed(self, g1, g2, child_num):
    datas = []
    mutationRange = self.mutationRange
    for i in range(child_num):
      data = copy.deepcopy(g1)
      for i in range(len(g2.network["weights"])):
        if random.random() <= 0.5:
          data.network["weights"][i] = g2.network["weights"][i]

      for i in range(len(data.network["weights"])):
        if random.random() < self.mutationRate:
          data.network["weights"][i] += random.random() * mutationRange * 2 - mutationRange

      datas.append(data)
    return datas

  def generateNextGeneration(self, network_struct):
    nexts = []
    elitism_num = round(self.elitism * self.population)
    #print "======before new generation======"
    for i in range(int(elitism_num)):
      #print "%s: " % i, self.genomes[i].network
      if len(nexts) < self.population:
        nexts.append(copy.deepcopy(self.genomes[i].network))
        #print "append: %s-" % i, nexts[-1]

    random_num = round(self.randomBehaviour * self.population)
    for i in range(int(random_num)):
      network = Network()
      network.perceptronGeneration(network_struct[0],
                                   network_struct[1],
                                   network_struct[2])
      save_data = network.readSave()
      for j in range(len(save_data["weights"])):
        save_data["weights"][j] = randomClamped()
      if len(nexts) < self.population:
        nexts.append(save_data)
        #print "random", nexts[-1]

    max = 0
    child_num = 1
    if self.nbChild > 0:
      child_num = self.nbChild
    while True:
      for i in range(max):
        childs = self.breed(self.genomes[i], self.genomes[max], child_num)
        for child in childs:
          if len(nexts) < self.population:
            nexts.append(child.network)
            #print "breed", nexts[-1]
          else:
            return nexts
      max += 1
      if max >= (len(self.genomes) - 1):
        max = 0

class Generations():
  def __init__(self, population=50):
    self.generations = []
    self.population = population

  def firstGeneration(self, inputs, hiddens, outputs):
    out = []
    for i in range(self.population):
      nn = Network()
      nn.perceptronGeneration(inputs, hiddens, outputs)
      out.append(nn.readSave())
    self.generations.append(Generation(-1))
    return out

  def nextGeneration(self, network_struct):
    if len(self.generations) == 0:
      return None

    gen_len = len(self.generations)
    gen = self.generations[gen_len - 1].generateNextGeneration(network_struct)
    self.generations.append(Generation(-1))
    return gen

  def addGenome(self, genome):
    if len(self.generations) == 0:
      return None

    return self.generations[len(self.generations) - 1].addGenome(genome)

class Neuroevolution():
  def __init__(self, network, population):
    # 网络结构，代表input个数，hidden结构，output个数
    self.network = network
    # 是否保留最后一次的网络结构
    self.historic = 0
    # 是否只保存网络的weight信息
    self.lowHistoric = False
    # 根据网络输出结果排序，-1为降序，1为升序
    self.scoreSort = -1
    self.generations = Generations(population)

  def restart(self):
    self.generations = Generations()

  def nextGeneration(self):
    networks = []
    if len(self.generations.generations) == 0:
      networks = self.generations.firstGeneration(self.network[0], self.network[1], self.network[2])
    else:
      #print "entry generation new networks"
      networks = self.generations.nextGeneration(self.network)
      #print "end generation new networks"

    #for item in networks:
      #print item
    nns = []
    for i in range(len(networks)):
      nn = Network()
      nn.save(networks[i])
      nns.append(nn)

    return nns

  def networkScore(self, network, score):
    self.generations.addGenome(Genome(score, network.readSave()))
