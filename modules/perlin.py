import numpy as np
from .generatorbase import GeneratorBase

class PerlinNoiseGenerator(GeneratorBase):
    def __init__(self, size: int, scale: float=0.2, octaves: int=1, seed: int=None):
        assert size > 0, "Size must be positive."
        assert scale > 0, "Scale must be positive."

        self.size = size
        self.scale = scale
        self.octaves = octaves
        self.seed = seed
        self.rnd = np.random.default_rng(seed)

        self.heightmap = np.zeros((size, size), dtype=float)
        
    def generate(self) -> np.ndarray:
        print(f"[PerlinNoise] ({self.size} size, {self.scale} scale, {self.octaves} octaves)")
        self._create_vector_field()
        self._calculate_heightmap()
        
        self._normalize_heightmap()
        return self.heightmap
    
    def _create_vector_field(self):
        directions = self.rnd.uniform(0, 2 * np.pi, (self.size+1, self.size+1))
        self.vector_field = np.dstack((np.sin(directions), np.cos(directions)))
        
    def _noise(self, x, y) -> float:
        # TODO: Change to use vectorization for performance
        xf = x * self.scale
        yf = y * self.scale
        
        x0 = int(xf) % self.size
        y0 = int(yf) % self.size
        x1 = x0 + 1 % self.size
        y1 = y0 + 1 % self.size
        
        dx = xf - x0
        dy = yf - y0
        dot00 = self._dot_grid_gradient(x0, y0, dx, dy)
        dot10 = self._dot_grid_gradient(x1, y0, dx - 1, dy)
        dot01 = self._dot_grid_gradient(x0, y1, dx, dy - 1)
        dot11 = self._dot_grid_gradient(x1, y1, dx - 1, dy - 1)
        
        u = self._fade(dx)
        v = self._fade(dy)
        nx0 = self._lerp(dot00, dot10, u)
        nx1 = self._lerp(dot01, dot11, u)
        value = self._lerp(nx0, nx1, v)
        return value
                
    def _calculate_heightmap(self):
        frequency = 1
        amplitude = 1
        max_amplitude = 0
        
        for _ in range(self.octaves):
            for y in range(self.size):
                for x in range(self.size):
                    self.heightmap[y, x] += self._noise(x * frequency, y * frequency) * amplitude
            
            max_amplitude += amplitude
            amplitude /= 2
            frequency *= 2
        
        self.heightmap /= max_amplitude
    
    def _dot_grid_gradient(self, ix, iy, dx, dy):
        gradient = self.vector_field[iy % self.size, ix % self.size]
        return (dx * gradient[1] + dy * gradient[0])
    
    def _lerp(self, a0, a1, w):
        return (1.0 - w) * a0 + w * a1
    
    def _fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def _normalize_heightmap(self):
        min_val = np.min(self.heightmap)
        max_val = np.max(self.heightmap)
        self.heightmap = (self.heightmap - min_val) / (max_val - min_val)