#!/usr/bin/env python

import random
import itertools

def generate_random_grid(cols=6, rows=6, minValue=1, maxValue=100):
    """Generates a random two-dimensional hex array."""
    
    grid = [[format(random.randint(minValue, maxValue), 'X') for x in xrange(cols)] for y in xrange(rows)]
    
    return grid


def __get_adjacent_tiles(grid=None, pos=(0, 0), moveset="udlr"):
    """Returns a list of adjacent tile tuples of a given position in a grid."""
    
    if grid is None:
        raise ValueError

    rows = len(grid)
    cols = len(grid[0])

    nextTiles = []

    # right
    if 'r' in moveset and pos[0] < cols - 1:
        nextTiles.append((pos[0] + 1, pos[1]))

    # left
    if 'l' in moveset and pos[0] > 0:
        nextTiles.append((pos[0] -1, pos[1]))

    # down
    if 'd' in moveset and pos[1] < rows - 1:
        nextTiles.append((pos[0], pos[1] + 1))

    # up
    if 'u' in moveset and pos[1] > 0:
        nextTiles.append((pos[0], pos[1] - 1))

    return nextTiles


def hex_to_int_grid(hex_grid=None):
    """Converts a given two-dimensional hex array to a two-dimensional integer array."""
    
    # Convert hex grid values into integer values for easier processing later
    if hex_grid is None or not isinstance(hex_grid, list):
        raise ValueError

    rows = len(hex_grid)
    cols = len(hex_grid[0])

    int_grid = [row[:] for row in hex_grid]
    for x in xrange(rows):
        for y in xrange(cols):
            val = hex_grid[x][y]
            if (isinstance(val, str) or isinstance(val, unicode)):
                try:
                    int_grid[x][y] = int(val, 16)
                except TypeError:
                    raise
            else:
                try:
                    int_grid[x][y] = int(val)
                except ValueError:
                    raise

    return int_grid


def get_least_cost_path(grid=None, origin=(0, 0), destination=None, moveset="udlr"):
    """Returns a tuple consisting of a list of tiles that are part of the least cost
    path and the list of directions from the source to the target tile."""
     
    # This uses Dijkstra's algorithm to find the shortest paths between nodes in a graph.
    if grid is None:
        raise ValueError

    startPos = origin
    rows = len(grid)
    cols = len(grid[0])

    if destination is None:
        destination = (cols - 1, rows - 1)
    endPos = destination

    # Generate list of 'unvisited' tiles and assign tentative least cost value for each tile
    Q = {z: float("inf") for z in itertools.product([x for x in xrange(cols)], [y for y in xrange(rows)])}
    
    # Lists of tentative least cost value for each tile and the previous tiles
    costs = {q: float("inf") for q in Q}
    prev_tiles = {q: None for q in Q}

    # Mark source tile as the current tile
    costs[startPos] = Q[startPos] = grid[startPos[0]][startPos[1]]

    while Q:
        # Find the tile with the least cost value and remove it from the
        # list of 'unvisited' tiles
        u = min(Q, key=Q.get)
        del Q[u]

        # Get list of possible adjacent tiles to move next 
        nextTiles = __get_adjacent_tiles(grid, u, moveset)
        
        
        # Determine the least cost value for each adjacent tile
        # and update it's tentative least cost value
        for v in nextTiles:
            path_cost = costs[u] + grid[v[1]][v[0]]
            if path_cost < costs[v]:
                costs[v] = Q[v] = path_cost
                prev_tiles[v] = u

    directions = []
    path = [endPos]

    # Trace our way back from the target tile to the source
    # using the least cost path determined earlier
    while prev_tiles[endPos]:
        path.insert(0, prev_tiles[endPos])
        x = endPos[0] - prev_tiles[endPos][0]
        y = endPos[1] - prev_tiles[endPos][1]

        if x > 0 and y == 0:
            directions.insert(0, 'r')
        elif x < 0 and y == 0:
            directions.insert(0, 'l')
        elif y > 0 and x == 0:
            directions.insert(0, 'd')
        elif y < 0 and x == 0:
            directions.insert(0, 'u')
        else:
            raise ValueError()

        endPos = prev_tiles[endPos]

    return path, directions
