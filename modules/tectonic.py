from voronoi import VoronoiGenerator
import numpy as np
import math
from scipy.ndimage import gaussian_filter

class TectonicGenerator:
    def __init__(self,
                 size: int,
                 smoothing: float=0.0,
                 plates_clusters: int=5,
                 plates_iterations: int=3,
                 seed: int=None):
        self.size = size
        self.smoothing = smoothing
        self.plates_clusters = plates_clusters
        self.plates_iterations = plates_iterations
        self.seed = seed
        self.rnd = np.random.default_rng(seed)

        self.heightmap = np.zeros((size, size), dtype=float)

    def generate(self) -> np.ndarray:
        print(f"[Tectonic] ({self.size} size, {self.smoothing} smoothing)")
        self._initialize_plates()
        self._create_boundaries_mask()
        self._create_heightmap()
        self._smooth_heightmap()
        self._normalize_heightmap()

        return self.heightmap

    def _initialize_plates(self):
        self.plates = VoronoiGenerator(size=self.size,
                                       clusters=self.plates_clusters,
                                       iterations=self.plates_iterations,
                                       seed=self.seed)\
                                        .generate()
        
        directions = self.rnd.uniform(0, 1, (self.plates_clusters)) * 2 * math.pi
        x = np.cos(directions)
        y = np.sin(directions)
        self.plate_velocities = np.stack((y, x), axis=-1)
        self.plate_velocities /= np.linalg.norm(self.plate_velocities, axis=1, keepdims=True)

    def _create_boundaries_mask(self):
        x_diff = np.zeros((self.size, self.size), dtype=bool)
        y_diff = np.zeros((self.size, self.size), dtype=bool)

        x_diff[:, :-1] = self.plates[:, :-1] != self.plates[:, 1:]
        y_diff[:-1, :] = self.plates[:-1, :] != self.plates[1:, :]

        self.boundary_mask = np.logical_or(x_diff, y_diff)

    def _create_heightmap(self):
        vel_x = self.plate_velocities[self.plates, 1]
        vel_y = self.plate_velocities[self.plates, 0]

        rel_x = np.zeros((self.size, self.size), dtype=float)
        rel_y = np.zeros((self.size, self.size), dtype=float)

        rel_x[:, 1:] = vel_x[:, 1:] - vel_x[:, :-1]
        rel_y[1:, :] = vel_y[1:, :] - vel_y[:-1, :]

        self.heightmap = rel_x + rel_y

    def _smooth_heightmap(self):
        if self.smoothing > 0.0:
            self.heightmap = gaussian_filter(self.heightmap, sigma=self.smoothing)

    def _normalize_heightmap(self):
        min_height = np.min(self.heightmap)
        max_height = np.max(self.heightmap)
        self.heightmap = (self.heightmap - min_height) / (max_height - min_height)
