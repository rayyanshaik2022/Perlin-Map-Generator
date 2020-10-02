import pygame
from settings import *
import numpy as np
from noise import *
from bridson import poisson_disc_samples as pds
import time
import random
import pygame.gfxdraw
from poisson_disc_samples import poisson_disc_samples
from multiprocessing import Pool

class Environment:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
        self.cloud_seed = np.random.randint(1,500)
        self.cloud_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.cloud_layer.fill((255,255,255,0))
        self.cloud_row_add = 0 

        #self.black = pygame.Surface((WIDTH, HEIGHT), pygame.HWSURFACE)
        #self.black.fill((255,255,255))
        
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.grid = []
        self.cloud_grid = []
        self.tree_map = []
    def new(self):

        start = time.time()

        self.background_surface = pygame.Surface((HEIGHT, WIDTH))
        
        self.grid = np.zeros(shape=(HEIGHT, WIDTH))
        self.cloud_grid = np.zeros(shape=(HEIGHT, WIDTH))
        self.grid = self.perlin(self.grid)
        self.cloud_grid = self.cloud_perlin(self.cloud_grid, self.cloud_seed)

        seed = np.random.randint(0,500)
        
        self.new_trees = self.trees2(self.grid)
        self.background_surface = self.full_draw(self.grid, self.background_surface)

        self.cloud_layer = pygame.Surface((HEIGHT, WIDTH), pygame.SRCALPHA)
        self.cloud_layer.fill((255,255,255,0))

        stop = time.time()
        print("Time to generate: ", str( round(stop - start, 2) ), "seconds")
        


    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000 # Controls update speed (FPS per second)
            self.events()
            self.draw()
        
            

    def close(self):
        pygame.quit()
        quit()

    def events(self):
        # catch all events here
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()

    def draw(self):

        self.screen.blit(self.background_surface, (0,0))

        self.cloud_layer.fill((255,255,255,0))
        self.cloud_layer.set_alpha(0)

        self.cloud_layer = self.cloud_update(self.cloud_grid, self.cloud_layer)

        self.screen.blit(self.cloud_layer, (0,0))    

        pygame.display.flip()

        

    def perlin(self, grid, seed=np.random.randint(SEED_MIN, SEED_MAX)):
        
        pygame.display.set_caption(TITLE + " | SEED: " + str(seed))

        for i in range(len(grid)):
            for c in range(len(grid[i])):

                grid[i][c] = pnoise2(c/SCALE, i/SCALE, octaves=8, persistence=0.5, lacunarity=2.0, base=seed)
        
        return grid

    def cloud_perlin(self, grid, seed):

        pygame.display.set_caption(TITLE + " | SEED: " + str(seed))

        for i in range(len(grid)):
            for c in range(len(grid[i])):

                grid[i][c] = pnoise2(c/SCALE, i/SCALE, octaves=4, persistence=0.5, lacunarity=2.0, base=seed)
        
        return grid

    def trees(self, grid, r=10):

        tree_list = pds(width=WIDTH, height=HEIGHT, r=r, k=30)
        tree_list = np.array(tree_list)
        tree_list = np.around(tree_list, 0)   
        return tree_list

    def cloud_update(self, grid, surf):

        rolled = np.roll(grid, -1, 1)
        surf.fill((255,255,255,0))
        
        for y, row in enumerate(rolled):
            for x, item in enumerate(row):

                if item == row[-1]:
                    rolled[y][x] = pnoise2((x+self.cloud_row_add)/SCALE, y/SCALE, octaves=4, persistence=0.5, lacunarity=2.0, base=self.cloud_seed)

                cell = rolled[y][x]

                if cell > 0.2:
                    color = (170, 170, 170, 100)
                    surf.set_at((x, y), color)
        self.cloud_row_add += 1
        self.cloud_grid = rolled
        return surf


    def trees2(self, grid):
        
        min_rad = 8
        max_rad = 10
        z = np.interp(grid, (np.amin(grid), np.amax(grid)), (min_rad, max_rad))
        
        return poisson_disc_samples(width=HEIGHT, height=WIDTH, r_max=max_rad, r_min=min_rad, k=3, r_array=z)

    def full_draw(self, grid, surf):

        for y, row in enumerate(grid):
            for x, item in enumerate(row):

                tree_c = 0
                cell = grid[y][x]

                color = ()
                if cell > 0:
                    color = COLORS['beach']
                if cell > 0.005:
                    color = COLORS['dirt']
                if cell > 0.01:
                    color = COLORS['shore-grass']
                if cell > 0.02:
                    color = COLORS['grass2']
                    tree_c = 0.9
                if cell > 0.04:
                    color = COLORS['grass3']
                if cell > 0.08:
                    color = COLORS['grass4']
                if cell > 0.15:
                    color = COLORS['grass5']
                if cell > 0.25:
                    color = COLORS['mountain-base']
                if cell > 0.26:
                    color = COLORS['mountain2']
                if cell > 0.3:
                    color = COLORS['mountain3']
                if cell > 0.32:
                    color = COLORS['mountain4']
                if cell > 0.4:
                    color = COLORS['peak1']
                if cell <= 0:
                    color = COLORS['shallow-water']
                    tree_c = 0
                if cell < -0.03:
                    color = COLORS['ocean']
                    tree_c = 0.9
                if cell < -0.09:
                    color = COLORS['deep-ocean']
                    tree_c = 0.9
                
                surf.set_at((x, y), color)

        for tx, ty in self.new_trees:
            tx, ty = int(tx), int(ty)
            cell = self.grid[ty][tx]
            tree_spawnrate = 0
            if cell > 0.01:
                tree_spawnrate = 0.2
            if cell > 0.02:
                tree_spawnrate = 0.4
            if cell > 0.04:
                tree_spawnrate = 0.6
            if cell > 0.08:
                tree_spawnrate = 0.7
            if cell > 0.15:
                tree_spawnrate = 0.1
            if cell > 0.25:
                tree_spawnrate = 0
            if cell <= 0:
                tree_spawnrate = 0
            
            if random.random() < tree_spawnrate:
                pygame.draw.rect(surf, COLORS['tree-bark'], (tx + random.randint(-1,0), ty, 1, 5), 2)
                pygame.gfxdraw.filled_circle(surf, tx, ty, 2, COLORS['tree'])
                pygame.gfxdraw.aacircle(surf, tx, ty, 2, COLORS['tree'])

        return surf
# create the game object

if __name__ == '__main__':
    g = Environment()
    g.new()
    g.run()
