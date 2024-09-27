from abc import ABC
import random
from uuid import UUID


class Block(ABC):
    def __init__(self, coordinates: tuple[int, int]) -> None:
        self.coordinates = coordinates

class PlaceBlock(Block):
    def __init__(self, coordinates: tuple[int, int], name : str, description : str, representative : tuple[int, int]) -> None:
        super().__init__(coordinates)
        self.name = name
        self.description = description
        self.representative = representative 

class SemaphoreBlock(Block):
    def __init__(
        self, coordinates: tuple[int, int], representative: tuple[int, int]
    ) -> None:
        super().__init__(coordinates)
        self.representative = representative


class RoadBlock(Block):
    def __init__(self, coordinates: tuple[int, int], direction: int) -> None:
        super().__init__(coordinates)
        self.direction = direction
        self.car_id: UUID = None


class SidewalkBlock(Block):
    def __init__(self, coordinates: tuple[int, int], vertical: bool) -> None:
        super().__init__(coordinates)
        self.vertical = vertical
        self.walker_id: UUID = None


class Environment:
    def __init__(self, matrix: list[list[Block]]) -> None:
        # Local imports
        from sim.Car import Car
        from sim.Semaphore import Semaphore
        from sim.Walker import Walker

        # Core logic properties
        self.matrix = matrix
        self.cars: dict[UUID, Car] = {}
        self.walkers: dict[UUID, Walker] = {}
        self.semaphores: dict[tuple[int, int], Semaphore] = {}
        self.places : dict[tuple[int, int], PlaceBlock] = {}
        self._extract_data() # Extract 

        # Testing purpose call
        self._initialize() 

    def _extract_data(self) -> None:
        height = len(self.matrix)
        width = len(self.matrix[0])

        for i in range(height):
            for j in range(width):
                block = self.matrix[i][j]

                # Extract semaphores representatives
                if isinstance(block, SemaphoreBlock) and block.representative not in self.semaphores:
                    from sim.Semaphore import Semaphore
                    self.semaphores[block.representative] = Semaphore(block.representative, self)
                    self.semaphores[block.representative].gui_label = len(self.semaphores)

                # Extract interest places
                if isinstance(block, PlaceBlock):
                    self.places[(i, j)] = block

    # Testing purpose method
    def _initialize(self):
        from sim.event_handler import EventHandler
        event_handler = EventHandler(self)

        for _ in range(20):
            road_blocks = event_handler._get_free_blocks(RoadBlock)
            sidewalk_blocks = event_handler._get_free_blocks(SidewalkBlock)

            from sim.Car import Car
            car = Car(random.choice(road_blocks).coordinates, random.choice(road_blocks).coordinates, self)
            from sim.Walker import Walker
            walker = Walker(random.choice(sidewalk_blocks).coordinates, self)

            self.cars[car.id] = car
            self.walkers[walker.id] = walker