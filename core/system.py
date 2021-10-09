from types import LambdaType
import numpy as np

class System:
    state: np.ndarray = None
    
    V: LambdaType = None

    def __init__(self, V_x: str, V_y: str) -> None:
        
        def vectorField(X: np.ndarray):
            x, y = X[:,0], X[:,1] # passing in x, y
            try:
                if 'x' not in V_x and 'y' not in V_x:
                    X = np.broadcast_to(eval(V_x), x.shape)
                else:
                    X = eval(V_x)
                if 'x' not in V_y and 'y' not in V_y:
                    Y = np.broadcast_to(eval(V_y), y.shape)
                else:
                    Y = eval(V_y)
                return np.stack([X, Y], axis=1)
            except Exception:
                return np.zeros(X.shape)
        self.V = vectorField

    def get_state(self) -> np.ndarray:
        return self.state

    def set_state(self, state) -> None:
        self.state = state

    def get_derivative(self):
        return self.V(self.state)