from types import LambdaType
import numpy as np

class System:
    state: np.ndarray = None
    
    V: LambdaType = None

    def __init__(self, V_x: str, V_y: str) -> None:
        
        def vectorField(X: np.ndarray):
            x, y = X[:,0], X[:,1] # passing in x, y
            try:
                return np.stack([eval(V_x), eval(V_y)], axis=1)
            except Exception:
                return np.zeros(X.shape)
        self.V = vectorField

    def get_state(self) -> np.ndarray:
        return self.state

    def set_state(self, state) -> None:
        self.state = state

    def get_derivative(self):
        return self.V(self.state)