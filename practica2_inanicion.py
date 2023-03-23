#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 20:49:51 2023

@author: prpa
"""

"""
Solution to the one-way tunnel
"""
"""
Voy a realizar una solución del problema en el que se soluciona la inanición, para ello lo que tendremos 
en cuenta es el número de coches que estan en espera. Cuando hayan esperando x cantidad de coches, los peatones 
deben dejarlos pasar.
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = 1
NORTH = 0

NCARS = 100
NPED = 30
TIME_CARS = 0.5  
TIME_PED = 5
TIME_IN_BRIDGE_CARS = 1 
TIME_IN_BRIDGE_PEDESTRIAN = 10

class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.ncar_pedestrian = Value('i', 0) 
        self.ncar_south = Value('i', 0)
        self.ncar_north = Value ('i', 0)
        self.npedestrian = Value ('i', 0) 
        self.ncar_waiting = Value ('i', 0) 
        self.no_cars_south = Condition (self.mutex) 
        self.no_cars_north = Condition (self.mutex)
        self.no_pedestrian = Condition (self.mutex)  
        self.car_waiting = Condition (self.mutex)
    
    def are_no_pedestrian(self): 
        return self.npedestrian.value == 0 
    
    def are_nobody_south(self): 
        return  self.ncar_south.value == 0 
    
    def are_nobody_north(self): 
        return self.ncar_north.value == 0 
    
    def max_waiting_car(self): 
        return self.ncar_waiting.value < 15
    
    def wants_enter_car(self, direction: int) -> None:
        self.mutex.acquire()
        self.ncar_pedestrian.value += 1
        self.ncar_waiting.value += 1
        self.no_pedestrian.wait_for(self.are_no_pedestrian)
        if direction == 1:  
            self.no_cars_north.wait_for(self.are_nobody_north)  
            self.ncar_south.value += 1
        if direction == 0 :
            self.no_cars_south.wait_for(self.are_nobody_south) 
            self.ncar_north.value += 1
        self.ncar_waiting.value -= 1
        self.car_waiting.notify_all()
        self.mutex.release()

    def leaves_car(self, direction: int) -> None:
        self.mutex.acquire() 
        self.ncar_pedestrian.value += 1
        if direction == 1  :
            self.ncar_south.value -=1 
            if self.ncar_south.value == 0:
                self.no_cars_south.notify_all() 
        if direction ==  0:
            self.ncar_north.value -= 1 
            if self.ncar_north.value == 0:
                self.no_cars_north.notify_all()
        self.mutex.release()

    def wants_enter_pedestrian(self) -> None:
        self.mutex.acquire()
        self.ncar_pedestrian.value += 1
        self.car_waiting.wait_for (self.max_waiting_car)
        self.no_cars_north.wait_for(self.are_nobody_north)
        self.no_cars_south.wait_for(self.are_nobody_south)
        self.npedestrian.value += 1
        self.mutex.release()

    def leaves_pedestrian(self) -> None:
        self.mutex.acquire()
        self.ncar_pedestrian.value += 1 
        self.npedestrian.value -= 1 
        if  self.npedestrian.value == 0: 
            self.no_pedestrian.notify_all()
        self.mutex.release()

    def __repr__(self) -> str:
        return f'Monitor: {self.ncar_pedestrian.value}'

def delay_car_north() -> None:
    time.sleep(TIME_IN_BRIDGE_CARS)
    
def delay_car_south() -> None:
    time.sleep(TIME_IN_BRIDGE_CARS)

def delay_pedestrian() -> None:
    time.sleep(TIME_IN_BRIDGE_PEDESTRIAN)
    

def car(cid: int, direction: int, monitor: Monitor)  -> None:
    print(f"car {cid} heading {direction} wants to enter. {monitor}")
    monitor.wants_enter_car(direction)
    print(f"car {cid} heading {direction} enters the bridge. {monitor}")
    if direction==NORTH :
        delay_car_north()
    else:
        delay_car_south()
    print(f"car {cid} heading {direction} leaving the bridge. {monitor}")
    monitor.leaves_car(direction)
    print(f"car {cid} heading {direction} out of the bridge. {monitor}")

def pedestrian(pid: int, monitor: Monitor) -> None:
    print(f"pedestrian {pid} wants to enter. {monitor}")
    monitor.wants_enter_pedestrian()
    print(f"pedestrian {pid} enters the bridge. {monitor}")
    delay_pedestrian()
    print(f"pedestrian {pid} leaving the bridge. {monitor}")
    monitor.leaves_pedestrian()
    print(f"pedestrian {pid} out of the bridge. {monitor}")



def gen_pedestrian(monitor: Monitor) -> None:
    pid = 0
    plst = []
    for _ in range(NPED):
        pid += 1
        p = Process(target=pedestrian, args=(pid, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/TIME_PED))

    for p in plst:
        p.join()

def gen_cars(monitor) -> Monitor:
    cid = 0
    plst = []
    for _ in range(NCARS):
        direction = NORTH if random.randint(0,1)==1  else SOUTH
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/TIME_CARS))

    for p in plst:
        p.join()

def main():
    monitor = Monitor()
    gcars = Process(target=gen_cars, args=(monitor,))
    gped = Process(target=gen_pedestrian, args=(monitor,))
    gcars.start()
    gped.start()
    gcars.join()
    gped.join()


if __name__== '__main__':
    main()