# HTM
Originally made by M.S.KIM, forked by Cailen R. <br> 
original theory from [numenta](https://numenta.com/neuroscience-research/research-publications/papers/)
Hierachical Temporal Memory System

---
# What's different: 
This fork is dedicated to building a working implementation of HTM to be used in real time anomaly streams that can run in python 3.6. Currently Numeta has no plan to port forward their benchmark and library to python 3 so alternative solutions were needed. Ideally once complete it will be able to be used as a drop in replacement of the numeta HTM model for other projects.

---
## 1. HTM?

> HTM 은 대뇌 신피질 (neocortex) 의 구조를 벤치마킹한 신경망이다. 신피질 전역에서 기둥형태의 뉴런집합체인  micro column 구조가 발견된다.
이 구조는 어느곳에서나 같은 구조를 띄고 있으며 어디에 위치하는가에 관계없이 실제로 같은 작업을 수행한다. 
다른 동물들은 감각기관으로부터 받는 정보 대부분을 변연계에서 처리하는 것과 달리 인간은 신피질이 이 작업을 많은 부분 이어받았다.
일반화, 추상화, 추론 등 고등지능은 이 신피질의 계층구조에서 학습되는 듯하다.
HTM 은 이 신피질의 micro column 을 모방한 생체 신경망이다.

> HTM is a neural network that benchmarks the structure of the neocortex. A columnar neuron aggregate, micro column structure, is found throughout the neocortex. This structure has the same structure everywhere, and it actually does the same thing regardless of where it is located. Unlike other animals that process most of the information they receive from sensory organs in the limbic system, the human cortex has taken up this task in many ways. Higher intelligence, such as generalization, abstraction, and reasoning, seems to be learned in this hierarchy of neocortex. HTM is a vital neural network that mimics the microcolumns of the cortex.


## 2. 특징

1. 비지도 학습에 해당.
2. 주로 시계열 데이터를 학습하고 처리.
3. deep learning 과 다르게 live streaming 데이터를 학습하는데 특화되어있음.
4. 구조가 복잡한 대신 학습은 단순한 hebbian learning 으로 학습.
5. noise tolerance 가 뛰어남.


1. Applicable to non-paper learning.
2. Mainly learns and processes time series data.
3. Unlike deep learning, it specializes in learning live streaming data.
4. Structures are complex, but learning is done with simple hebbian learning.
5. Excellent noise tolerance.

## 3. 구조

실제로는 6층의 구조로 되어있지만 1층만 구현해도 sequence data 를 학습할 수 있다고 함.
- 하나의 계층에 많은 micro column 으로 구성되어 있음.
- 실제로는 2차원으로 퍼져있지만 1차원으로 구현해도 됨.
- 하나의 column 안에는 여러개의 cell 이 1열로 기둥형태로 구성되어짐.
- 하나의 cell 은 2종류의 수상돌기가 있음.
- 하나는 입력 데이터와 연결되는 proximal segment
- 다른 하나는 같은 계층내 다른 cell 들과 연결되는 distal segment
- proximal segment 는 column 내 cell 들과 모두 공유되므로 이 수상돌기는 column 의 속성으로 간주한다.
- 이 수상돌기에는 입력 데이터와 직접 연결되는 synapse 들을 갖고 있다.
- distal segment 는 각 cell 마다 여러개 갖고 있고 각 segment 마다 여러개의 synapse 를 갖고 있다. 
- "column - cell - segment - synapse"

In fact, it has a six-layer structure, but it can learn sequence data even if only one layer is implemented.
- It consists of many micro columns in one layer.
- It actually spreads in two dimensions, but it can also be implemented in one dimension.
- In a column, several cells are arranged in columns in one column.
- One cell has two kinds of dendrite. One is the proximal segment associated with the input data The other is the distal segment that connects with other cells in the same layer
- Since the proximal segment is shared with all the cells in the column, this dendrite is considered as a property of the column. - These dendrites have synapses directly linked to the input data.
- The distal segment has several cells per cell, and each segment has multiple synapses.
- "column - cell - segment - synapse"

크게 2 가지 모듈
1. Spatial Pooler (공간 풀러)
2. Temporal Memory (시간 풀러)

공간 풀러의 메커니즘은 입력 층 -> 신경망(2차원 혹은 1차원 column 벡터) 으로 데이터가 주입될 때
정적 표상을 만드는 역할을 한다.
proximal segment 과 관련이 있다.

1. Spatial Pooler 
2. Temporal Memory
The mechanism of the spatial puller is that when data is injected into the input layer -> neural network (two-dimensional or one-dimensional column vector) 
It serves to create static representations. It is related to the proximal segment.

공간 풀러에서는 데이터를 받아서 그것을 특수한 정적 표상을 만들어낸다.
이를 희소분포표상 (SDR) 이라 함.
SDR 은 입력 데이터에 대해 극소수(=~2%)의 column 만 활성화 시킨것을 의미함.
모든 column 에 대해 소수의 column 을 선택하는 방법은 천문학적으로 많아질 수 있으므로,
수많은 정적 패턴을 인지할 수 있다.
이외의 SDR 의 여러 특징들은 [여기](https://nbviewer.jupyter.org/github/Chocoberry12/HTM/blob/master/SP3.ipynb)서 볼 수 있다.


---
Some other resources to help understand HTM. [summary article] (https://medium.com/@rockingrichie1994/understanding-hierarchal-temporal-memory-f6a1be38e07e), or [here] (https://www.analyticsvidhya.com/blog/2018/05/alternative-deep-learning-hierarchical-temporal-memory-htm-unsupervised-learning/),  or from Numeta themselves [here] (https://numenta.org/htm-school/)


The spatial pooler takes the data and generates a special static representation of it.
This is called rare distribution representation (SDR).
SDR means that only very few columns (= ~ 2%) are activated for the input data.
The choice of a few columns for every column can be astronomical, Numerous static patterns can be recognized.
Other features of SDR can be found [here] (https://nbviewer.jupyter.org/github/Chocoberry12/HTM/blob/master/SP3.ipynb).

