import math

def zero(x):
  return 0.0;

def const(c):
  return lambda x: c

def identity(x):
  return x

# 3*x*x - 2*x*x*x, x, 0.5 * (sin((x - 0.5)*3.14) + 1)
def blend(x):
  return 0.5 + 0.5 * math.sin((x - 0.5) * math.pi)

def step(x):
  if x < 0.5: return 0.0
  else: return 1.0

def stepper(r):
  def st(x):
    if x < r: return 0.0
    else: return 1.0
  return st

def accelerator(s):
  return lambda x: math.pow(x, s)

def deaccelerator(s = 2):
  return lambda x: 1.0 - math.pow(1.0 - x, s)

def rev_para(x):
  return 1 - (1 - x)**2

#def wave(x):
#  return 0.5 + 0.5 * math.sin((x - 0.25) * 2 * math.pi)

def forth_back(f):
  def fn(x):
    if x < 0.5: return f(2.0*x)
    else: return f(2.0*(1.0-x))
  return fn

def rep(n, f):
  def fn(x):
    if n > 0:
      return f(math.fmod(x, 1.0 / n) * n)
    return x
  return fn


# Don't use shifter
def shifter(r, f):
  return lambda x: f(math.fmod(x + r, 1.0))
#  def fn(x):
#    v = x - r
#    while (v > 1.0): v -= 1.0
#    while (v < 0.0): v += 1.0
#    return f(v)
#  return fn

def inverter(f):
  return lambda x: 1.0-f(x)

def plfun(nodes, values):
  def fn(x):
    begin = nodes[0]
    end = nodes[-1]
    node = begin * (1.0 - x) + end * x
    for i in range(len(nodes) - 1):
      if nodes[i] <= node <= nodes[i + 1]:
        d = (nodes[i+1] - nodes[i])
        if d > 0:
          r = float(node - nodes[i]) / d
          return values[i] * (1.0 - r) + values[i + 1] * r
        else:
          return values[i + 1]
    return 0.
  return fn

def fcomp(a, b):
  return lambda x: a(b(x))

def fmult(a, b):
  return lambda x: a(x) * b(x)

def fadd(a, b):
  return lambda x: a(x) + b(x)

def cmult(c, f):
  return lambda x: c * f(x)

def linear_combiner(a, b):
  return lambda x: a * (1. - x) + b * x
