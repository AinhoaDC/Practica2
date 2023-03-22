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
en cuenta es el número de coches y peatones que entran. Cuando hayan sobrepasado un límite impuesto, dejan 
pasar a los demás.
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = 1
NORTH = 0

NCARS = 50
NPED = 10
TIME_CARS = 0.5  # a new car enters each 0.5s
TIME_PED = 2 # a new pedestrian enters each 5s
TIME_IN_BRIDGE_CARS = 1 #(1, 0.5) # normal 1s, 0.5s
TIME_IN_BRIDGE_PEDESTRIAN = 3 #(30, 10) # normal 1s, 0.5s

class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.patata = Value('i', 0) 
        self.ncar_south = Value('i', 0)
        self.ncar_north = Value ('i', 0)
        self.npedestrian = Value ('i', 0) 
        self.ncar_waiting_south = Value ('i', 0) 
        self.ncar_waiting_north = Value ('i', 0 ) 
        #self.npedestrian_waiting = Value ('i',0)
        self.no_cars_south = Condition (self.mutex) 
        self.no_cars_north = Condition (self.mutex)
        self.no_pedestrian = Condition (self.mutex)  
        self.car_south_waiting = Condition (self.mutex)
        self.car_north_waiting = Condition (self.mutex) 
        self.max_car_south = Value('i', 0)
        self.max_car_north = Value('i', 0)
        self.max_pedestrian = Value('i',0)
    
    def are_no_pedestrian(self): 
        return self.npedestrian.value == 0 #and self.npedestrian_waiting.value == 0
    
    def are_nobody_south(self): 
        return  self.ncar_south.value == 0 #and  self.ncar_waiting_south.value == 0
    
    def are_nobody_north(self): 
        return self.ncar_north.value == 0 #and  self.ncar_waiting_north.value == 0 
    
    def no_waiting_south(self): 
        return self.ncar_waiting_south.value == 0 
    
    def no_waiting_north(self): 
        return self.ncar_waiting_north.value == 0 
    
    def wants_enter_car(self, direction: int) -> None:
        self.mutex.acquire()
        self.patata.value += 1
        if direction == 1:  
            self.ncar_waiting_south.value += 1
            self.no_cars_north.wait_for(self.are_nobody_north) 
            self.no_pedestrian.wait_for(self.are_no_pedestrian)
            self.ncar_south.value += 1
           # self.ncar_waiting_south.value -= 1
            self.max_car_south.value += 1 
            if self.ncar_south == 0: 
                self.car_south_waiting.notify_all()
        if direction == 0 :
            self.ncar_waiting_north.value += 1
            self.no_cars_south.wait_for(self.are_nobody_south) 
            self.no_pedestrian.wait_for(self.are_no_pedestrian)
            self.ncar_north.value += 1
            #self.ncar_waiting_north.value -= 1
            self.max_car_north.value += 1
            if self.ncar_north == 0: 
                self.car_north_waiting.notify_all()
        self.mutex.release()

    def leaves_car(self, direction: int) -> None:
        self.mutex.acquire() 
        self.patata.value += 1
        if direction == 1  :
            self.ncar_waiting_south.value -= 1
            self.ncar_south.value -=1 
            if self.max_car_south.value > 8 or self.ncar_waiting_south.value == 0 or self.npedestrian.value > 5 or self.ncar_waiting_north.value > 15:
                self.no_cars_south.notify_all() 
                self.max_car_south.value = 0 
        if direction ==  0: 
            self.ncar_waiting_north.value -= 1
            self.ncar_north.value -= 1 
            if self.max_car_north.value > 8 or self.ncar_waiting_north.value == 0 or self.npedestrian.value > 3 or self.ncar_waiting_south.value > 15:
                self.no_cars_north.notify_all()
                self.max_car_north.value = 0
        self.mutex.release()

    def wants_enter_pedestrian(self) -> None:
        self.mutex.acquire()
        self.patata.value += 1
        self.car_south_waiting.wait_for (self.no_waiting_south)
        self.car_north_waiting.wait_for(self.no_waiting_north)
        self.no_cars_north.wait_for(self.are_nobody_north)
        self.no_cars_south.wait_for(self.are_nobody_south)
        self.npedestrian.value += 1  
        self.max_pedestrian.value += 1
        self.mutex.release()

    def leaves_pedestrian(self) -> None:
        self.mutex.acquire()
        self.patata.value += 1 
        self.npedestrian.value -= 1 
        if self.max_pedestrian.value > 3 or self.npedestrian.value == 0 or self.ncar_waiting_north.value > 15 or self.ncar_waiting_south.value > 15: 
            self.no_pedestrian.notify_all()
            self.max_pedestrian.value = 0 
        self.mutex.release()

    def __repr__(self) -> str:
        return f'Monitor: {self.patata.value}'

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