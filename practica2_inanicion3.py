#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 11:35:34 2023

@author: prpa
"""


"""
Voy a realizar una solución del problema en el que se soluciona la inanición, para ello lo que tendremos 
en cuenta es el número de coches y peatones en espera. Cuando hayan esperando x cantidad de coches y x cantidad de peatones, 
los otros deben dejarlos pasar.
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = 1
NORTH = 0

NCARS = 100
NPED = 20
TIME_CARS = 0.5  
TIME_PED = 5
TIME_IN_BRIDGE_CARS = (1, 0.5) 
TIME_IN_BRIDGE_PEDESTRIAN = (30,10)

#Creamos la clase del monitor donde vamos a solucionar el problema del puente.
class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.npedestrian_all = Value('i', 0)
        self.ncar_south = Value('i', 0)
        self.ncar_north = Value ('i', 0)
        self.npedestrian = Value ('i', 0) 
        self.ncar_waiting = Value ('i', 0) 
        self.npedestrian_waiting = Value('i', 0)
        self.no_cars_south = Condition (self.mutex) 
        self.no_cars_north = Condition (self.mutex)
        self.no_pedestrian = Condition (self.mutex)  
        self.car_waiting = Condition (self.mutex)
        self.pedestrian_waiting = Condition(self.mutex)
        self.ncar = Value ('i', 0)
    
    #Las siguientes tres funciones se crean para poder utilizarla con variables de condición. En cada caso se tendrá que esperar hasta que se cumpla la indicada en cada momento:
    def are_no_pedestrian(self): 
        return self.npedestrian.value == 0 
    
    def are_nobody_south(self): 
        return  self.ncar_south.value == 0 
    
    def are_nobody_north(self): 
        return self.ncar_north.value == 0 
    
    #Usaremos la siguiente función para usarlo de condición como máximo de coches esperando. Con esto tratamos la inanición, evitamos que nunca no entren los coches. 
    def max_waiting_car(self): 
        return self.ncar_waiting.value < 15
    
    #Usaremos la siguiente función para usarlo de condición como máximo de peatones esperando. Con esto tratamos la inanición, evitamos que nunca no entren los peatones. 
    def max_waiting_pedestrian(self): 
        return self.npedestrian_waiting.value < 5
    
    #La siguiente función es para cuando los coches quieren y entran al puente: 
    def wants_enter_car(self, direction: int) -> None:
        self.mutex.acquire()
        self.ncar.value += 1 
        self.ncar_waiting.value += 1
        self.pedestrian_waiting.wait_for(self.max_waiting_pedestrian)#Esperamos hasta que se cumpla la condición de que hay menos de 5 peatones esperando. Si se supera esta cifra de peatones, los coches tienen que dejarlos pasar. 
        self.no_pedestrian.wait_for(self.are_no_pedestrian)#Deben esperar a que no hayan peatones.
        if direction == 1:  
            self.no_cars_north.wait_for(self.are_nobody_north)#Si el coche que quiere entrar viene del sur, debe esperar a que no haya coches del norte en el puente. 
            self.ncar_south.value += 1
        if direction == 0 :
            self.no_cars_south.wait_for(self.are_nobody_south)#Si el coche que quiere entrar viene del norte, debe esperar a que no haya coches del sur en el puente.
            self.ncar_north.value += 1
        self.ncar_waiting.value -= 1
        self.car_waiting.notify_all() #Avisamos a todos cuando no hay coches esperando.
        self.mutex.release()

    #La siguiente función te indica cuando un coche ha cruzado el puente:
    def leaves_car(self, direction: int) -> None:
        self.mutex.acquire()
        if direction == 1  :
            self.ncar_south.value -=1 
            if self.ncar_south.value == 0:#Esperamos a que todos los coches del sur hayan cruzado para notificar a los coches del norte y peatones.
                self.no_cars_south.notify_all() 
        if direction ==  0:
            self.ncar_north.value -= 1 
            if self.ncar_north.value == 0:#Esperamos a que todos los coches del norte hayan cruzado para notificar a los coches del sur y peatones.
                self.no_cars_north.notify_all()
        self.mutex.release()

    #Función para cuando los peatones quieren cruzar el puente:
    def wants_enter_pedestrian(self) -> None:
        self.mutex.acquire()
        self.npedestrian_waiting.value += 1
        if self.max_waiting_pedestrian():#Ponemos esta condición para que no se bloquee el sistema cuando hay muchos peatones y coches esperando y no se sepa cual entrar. 
            self.car_waiting.wait_for (self.max_waiting_car)#Esperamos hasta que se cumpla la condición de que hay menos de 15 coches esperando. Si se supera esta cifra de coches, los peatones tienen que dejarlos pasar. 
        #Los peatones esperan a que no hayan coches del sur y del norte cruzando el puente.
        self.no_cars_north.wait_for(self.are_nobody_north)
        self.no_cars_south.wait_for(self.are_nobody_south)
        self.npedestrian_all.value += 1
        self.npedestrian.value += 1
        self.npedestrian_waiting.value -= 1
        self.pedestrian_waiting.notify_all()#Avisamos a todos cuando no haya peatones esperando.
        self.mutex.release()

    #Función para cuando los peatones han cruzado el puente:
    def leaves_pedestrian(self) -> None:
        self.mutex.acquire()
        self.npedestrian.value -= 1 
        if  self.npedestrian.value == 0: #Se espera a que crucen todos los peatones para notificar a los coches de que pueden cruzar. 
            self.no_pedestrian.notify_all()
        self.mutex.release()

    def __repr__(self) -> str:
        return f'Coches: {self.ncar.value}, Peatones: {self.npedestrian_all.value}, Coches_esperando:{self.ncar_waiting.value}, Peatones_esperando:{self.npedestrian_waiting.value}'

def delay_car_north() -> None:
    time.sleep(max(random.normalvariate(1, 0.5),0))
    
def delay_car_south() -> None:
    time.sleep(max(random.normalvariate(1, 0.5),0))
    
def delay_pedestrian() -> None:
    time.sleep(max(random.normalvariate(30, 10),0))


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