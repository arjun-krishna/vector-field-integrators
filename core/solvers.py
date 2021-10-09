import numpy as np

class ExplicitEulerSolver(object):
  """A general Explicit Euler method solver."""
  def __init__(self):
    """Initilializes the solver."""
    pass
  
  def step(self, system, dt):
    X = system.get_state()
    h = np.broadcast_to(dt.reshape(-1, 1), X.shape)
    X_new = X + h*system.get_derivative()
    system.set_state(X_new)

class MidpointSolver(object):
  """A general Midpoint method solver."""
  def __init__(self):
    """Initilializes the solver."""
    pass
  
  def step(self, system, dt):
    X = system.get_state()
    h = np.broadcast_to(dt.reshape(-1, 1), X.shape)
    X_mid = X + 0.5*h*system.get_derivative()
    system.set_state(X_mid)
    X_new = X + h*system.get_derivative()
    system.set_state(X_new)  

class RK4Solver(object):
  def __init__(self):
    pass
  
  def step(self, system, dt):
    X = system.get_state()
    h = np.broadcast_to(dt.reshape(-1, 1), X.shape)
    K_1 = h * system.get_derivative()
    system.set_state(X + 0.5 * K_1)
    K_2 = h * system.get_derivative()
    system.set_state(X + 0.5 * K_2)
    K_3 = h * system.get_derivative()
    system.set_state(X + K_3)
    K_4 = h * system.get_derivative()
    X_new = X + (K_1 + 2 * K_2 + 2 * K_3 + K_4) / 6
    system.set_state(X_new)