import heapq
import random
from environment import Environment, RoadBlock, SemaphoreBlock, SidewalkBlock
from globals import DIRECTION_OFFSETS, valid_coordinates
from sim.Car.CarCommon import check_valid, semaphor_options
from sim.Walker.PathFinder import PathFinder, WalkerGraphNode
from sim.Walker.WalkerCommon import get_associated_semaphores


class WalkerDijkstra(PathFinder):
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)
    def path_finder(self, cur_pos: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]:
        return self.dijkstra(cur_pos, goal)

    def get_neighbours(self, current: WalkerGraphNode) -> list[tuple[WalkerGraphNode, float]]:
        result = []
        i, j = current.pos
        matrix = self.environment.matrix
        height = len(matrix)
        width = len(matrix[0])

        if isinstance(matrix[i][j], RoadBlock):
            direction = current.cross_direction
            x =  i + direction[0]
            y = j + direction[1]
            return [ (WalkerGraphNode((x, y), current, direction), 1) ] 

        if isinstance(matrix[i][j], SidewalkBlock):
            offsets = [(1, 0), (0, 1), (-1, 0), (0, -1)]
            random.shuffle(offsets) 
            for direction in offsets:
                x =  i + direction[0]
                y = j + direction[1]

                if check_valid(x, y, SidewalkBlock, self.environment):
                    result.append((WalkerGraphNode((x, y), current), 1))

                elif check_valid(x, y, RoadBlock, self.environment):
                    streets : list[tuple[int, int]] = []
                    while valid_coordinates(x, y, height, width) and isinstance(matrix[x][y], RoadBlock):
                        streets.append((x, y))
                        x += direction[0]
                        y += direction[1]
                    works = True
                    if valid_coordinates(x, y, height, width) and isinstance(matrix[x][y], SidewalkBlock):
                        for index, _  in enumerate(streets):
                            semaphores = get_associated_semaphores(streets[index], self.environment)
                            if len(semaphores) == 0:
                                works =  False
                                break
                    if works:
                        result.append((WalkerGraphNode((i + direction[0], j + direction[1]), current, direction), 1))
            
        return result

    def dijkstra(self, cur_pos: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]:
        x, y = cur_pos
        start_node = WalkerGraphNode(cur_pos, None)

        queue: list[WalkerGraphNode] = []
        heapq.heappush(queue, start_node)

        seen: dict[tuple[int, int], WalkerGraphNode] = {}
        seen[cur_pos] = start_node

        connected = False

        while queue:
            top = heapq.heappop(queue)
            for neighbour, _ in self.get_neighbours(top):
                neighbour_score = neighbour.parent.score + 1
                if neighbour.pos not in seen:
                    seen[neighbour.pos] = neighbour
                    neighbour.score = neighbour_score
                    heapq.heappush(queue, neighbour)
                elif neighbour_score < seen[neighbour.pos].score:
                    seen[neighbour.pos].parent = top
                    seen[neighbour.pos].score = neighbour_score

            if top.pos == goal:
                connected = True
                break

        if connected:
            path = [goal]
            while path[-1] != cur_pos:
                path.append((seen[path[-1]]).parent.pos)
            path.reverse()
            return path[1:]

        return [cur_pos]