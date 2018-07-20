# PyFlappyBirdNes
python版基于神经进化算法的flappybird

# 参考代码如下
https://github.com/xviniette/FlappyLearning 基于js版本的神经进化策略，收敛速度相当快，最快的一次在第12代基本成为不死鸟<br>
https://github.com/yenchenlin/DeepLearningFlappyBird python实现的DQN，但是在我本地训练两天，还没有达到稳定的状态，鸟仍然会随机死亡

# 运行方式
cd scripts && python bird_flappy.py

# 依赖的工具和包
python2.7<br>
pygame: 动画渲染

# 说明
## 20180719：
1、目前这个版本的鸟仍然会在某种状态下死亡，经过观察怀疑是状态没有捕获完全导致，仍然需要进一步迭代<br>
2、由于pygame运用不是很熟练，所以pipe之间不是等间距，这样反倒无意之间增加了游戏的难度
