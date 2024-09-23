import random
from threading import Thread
from environment import Environment, RoadBlock, SidewalkBlock
from sim.Car import Car
from sim.Walker import Walker
from sim.Semaphore import Semaphore

class EventHandler:
    def __init__(self, environment : Environment) -> None:
        self.environment = environment

    def start(self):
        self._start_semaphores()
        
        # Create 20 car-events/walker-events
        for _ in range(20):
            self._car_event()
            self._walker_event()

    def _start_semaphores(self):
        for semaphore_id in self.environment.semaphores:
            semaphore = Semaphore(semaphore_id, self.environment)
            semaphore_tread = Thread(target=semaphore.act)
            semaphore_tread.daemon = True
            semaphore_tread.start()
            

    def _car_event(self):
        with self.environment.lock:
            free_blocks = self._get_free_blocks(RoadBlock)
            block = random.choice(free_blocks)
            car = Car(block.coordinates, self.environment)
            block.car_id = car.id
            car_thread = Thread(target=car.act)
            car_thread.daemon = True
            car_thread.start()

    def _walker_event(self):
        with self.environment.lock:
            free_blocks = self._get_free_blocks(SidewalkBlock)
            block = random.choice(free_blocks)

            walker = Walker(block.coordinates, self.environment)
            walker_thread = Thread(target=walker.act)
            walker_thread.daemon = True
            walker_thread.start()
        
    def _get_free_blocks(self, block_type : type):
        matrix = self.environment.matrix
        height = len(matrix)
        width = len(matrix[0])
        free_blocks : list[RoadBlock] = []

        for i in range(height):
            for j in range(width):
                block = matrix[i][j]
                if isinstance(block, block_type):
                    if block_type == RoadBlock and block.car_id == None:
                        free_blocks.append(block)
                    elif block_type == SidewalkBlock and block.walker_id == None:
                        free_blocks.append(block)
        return free_blocks