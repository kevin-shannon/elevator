import names
import random
import simpy


class Building:
    def __init__(self, env, name, floors, num_elevators):
        self.env = env
        self.name = name
        self.floors = floors
        self.elevators = [Elevator(env, building=self, name=id, position=random.randint(0, self.floors - 1)) for id in range(num_elevators)]


class Elevator:
    def __init__(self, env, building, name, position=0, direction='up', capacity=1, passengers=0):
        self.env = env
        self.building = building
        self.name = name
        self.action = env.process(self.run())
        self.position = position
        self.direction = direction
        self.capacity = capacity
        self.passengers = passengers
        self.arrived = [env.event() for floor in range(self.building.floors)]

    def run(self):
        while True:
            print(f'elevator{self.name} loading on floor {self.position} at time {self.env.now}.')
            self.arrived[self.position].succeed()
            self.arrived[self.position] = env.event()
            yield self.env.timeout(1)
            if self.position + 1 == self.building.floors:
                self.direction = 'down'
            elif self.position == 0:
                self.direction = 'up'

            if self.direction == 'up':
                print(f'elevator{self.name} going up at time {self.env.now}.')
                yield self.env.timeout(5)
                self.position += 1
            elif self.direction == 'down':
                print(f'elevator{self.name} going down at time {self.env.now}.')
                yield self.env.timeout(5)
                self.position -= 1


class Passenger:
    def __init__(self, env, building, call_time, name=None, location=None, destination=None):
        self.env = env
        self.name = names.get_first_name() if name is None else name
        self.building = building
        self.location = random.randint(0, self.building.floors - 1) if location is None else location
        if destination is None:
            self.destination = random.randint(0, self.building.floors - 1)
            while self.location == self.destination:
                self.destination = random.randint(0, self.building.floors - 1)
        else:
            self.destination = destination
        self.call_time = call_time
        self.action = env.process(self.run())

    def wait_for_elevator(self):
        yield simpy.events.AnyOf(self.env, [elevator.arrived[self.location] for elevator in self.building.elevators])
        for elevator in self.building.elevators:
            if elevator.position == self.location and elevator.passengers < elevator.capacity:
                elevator.passengers += 1
                self.elevator = elevator
                return
        yield env.process(self.wait_for_elevator())

    def run(self):
        yield self.env.timeout(self.call_time)
        print(f'My name is {self.name}. I am on floor {self.location}. I would like to go to floor {self.destination}. The current time is {self.env.now}')
        yield env.process(self.wait_for_elevator())
        print(f'{self.name} is getting on elevator{self.elevator.name} at floor {self.location}')
        yield self.elevator.arrived[self.destination]
        print(f'{self.name} is getting off elevator{self.elevator.name} at floor {self.destination}')
        self.elevator.passengers -= 1


env = simpy.Environment()
building = Building(env, name='264', floors=8, num_elevators=2)
for i in range(4):
    Passenger(env, building=building, call_time=(i+1)*4)

env.run(until=150)
