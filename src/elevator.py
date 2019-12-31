import names
import random
import simpy


class Building:
    def __init__(self, name, floors, num_elevators):
        self.name = name
        self.floors = floors
        self.num_elevators = num_elevators


class Elevator:
    def __init__(self, env):
        self.env = env
        self.action = env.process(self.run())
        self.position = 0
        self.direction = 'up'
        self.capacity = 1
        self.passengers = 0
        self.arrived = [env.event() for floor in range(building.floors)]

    def run(self):
        while True:
            print(f'Loading on floor {self.position} at time {self.env.now}.')
            self.arrived[self.position].succeed()
            self.arrived[self.position] = env.event()
            yield self.env.timeout(1)
            if self.direction == 'up':
                print(f'Going up at time {self.env.now}.')
                yield self.env.timeout(5)
                self.position += 1
                if self.position + 1 == building.floors:
                    self.direction = 'down'
            elif self.direction == 'down':
                print(f'Going down at time {self.env.now}.')
                yield self.env.timeout(5)
                self.position -= 1
                if self.position == 0:
                    self.direction = 'up'


class Passenger:
    def __init__(self, env, call_time, name=None, location=None, destination=None):
        self.name = names.get_first_name() if name is None else name
        self.location = random.randint(0, building.floors - 1) if location is None else location
        if destination is None:
            self.destination = random.randint(0, building.floors - 1)
            while self.location == self.destination:
                self.destination = random.randint(0, building.floors - 1)
        else:
            self.destination = destination
        self.call_time = call_time
        self.action = env.process(self.run())

    def run(self):
        yield env.timeout(self.call_time)
        print(f'My name is {self.name}. I am on floor {self.location}. I would like to go to floor {self.destination}. The current time is {env.now}')

        while True:
            yield elevator.arrived[self.location]
            if elevator.passengers < elevator.capacity:
                elevator.passengers += 1
                break

        print(f'{self.name} is getting on at floor {self.location}')

        yield elevator.arrived[self.destination]
        elevator.passengers -= 1
        print(f'{self.name} is getting off at floor {self.destination}')


building = Building('264', 8, 1)
env = simpy.Environment()
elevator = Elevator(env)
for i in range(4):
    Passenger(env, (i+1)*4)

env.run(until=300)
