# random_dungeon_generator
Random dungeon generators implemented in various languages

**snakegen**  
snakegen.py uses a `blind man` type algorithm which 'walks' from one node to the next in randomly selected cardinal directions and will traverse back through the existing nodes when it walks itsleft into a loop that prevents it from generating more rooms/nodes. You can safely change min/maxInflation, numNodes, and maxMapWith/Height. Requires PyGame to see visual results.
