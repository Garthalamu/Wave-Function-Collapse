import numpy as np

class VoronoiGenerator:
    def __init__(self, size: int, clusters: int, iterations: int=0, seed: int=None):
        assert size > 0, "Size must be positive."
        assert clusters > 0, "Number of clusters must be more than 1."
        assert iterations >= 0, "Iterations must be non-negative."

        self.size = size
        self.clusters = clusters
        self.iterations = iterations
        self.seed = seed
        self.rnd = np.random.default_rng(seed)
        
        self.grid = np.zeros((size, size), dtype=int)

    def generate(self) -> np.ndarray:
        print(f"[Voronoi] ({self.size} size, {self.clusters} clusters, {self.iterations} iterations")
        self._initialize_seeds()
        self._calculate_clusters()
        for _ in range(self.iterations):
            self._recalculate_seeds()
            self._calculate_clusters()

        return self.grid

    def _initialize_seeds(self):
        self.seeds = self.rnd.integers(0, self.size, (self.clusters, 2))

    def _calculate_clusters(self):
        x, y, z = np.meshgrid(np.arange(self.size), np.arange(self.size), np.arange(self.clusters))
        sx, sy = self.seeds[:, 0], self.seeds[:, 1]
        
        distances = np.sqrt((x - sx[z])**2 + (y - sy[z])**2)
        self.grid = np.argmin(distances, axis=2)

    def _recalculate_seeds(self):
        new_seeds = []
        for i in range(self.clusters):
            positions = np.argwhere(self.grid == i)
            if len(positions) == 0:
                new_seeds.append(self.seeds[i])
                continue
            centroid = positions.mean(axis=0).astype(int)
            new_seeds.append([centroid[1], centroid[0]])
        self.seeds = np.array(new_seeds)