#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 10:44:24 2017

@author: wroscoe
"""

import time
from threading import Thread
from .memory import Memory
#from donkeycar.parts.actuator import PWMThrottle

class Vehicle():
    def __init__(self, mem=None):

        if not mem:
            mem = Memory()
        self.mem = mem
        self.parts = []
        self.on = True
        self.threads = []

    def add(self, part, inputs=[], outputs=[],
            threaded=False, run_condition=None):
        """
        Method to add a part to the vehicle drive loop.

        Parameters
        ----------
            inputs : list
                Channel names to get from memory.
            ouputs : list
                Channel names to save to memory.
            threaded : boolean
                If a part should be run in a separate thread.
        """

        p = part
        print('Adding part {}.'.format(p.__class__.__name__))
        entry={}
        entry['part'] = p
        entry['inputs'] = inputs
        entry['outputs'] = outputs
        entry['run_condition'] = run_condition

        if threaded:
            t = Thread(target=part.update, args=())
            t.daemon = True
            entry['thread'] = t

        self.parts.append(entry)

    def get(self, part_name):
        '''
        **Description**
        Returns the specified part.
        '''
        for entry in self.parts:
            if entry['part'].__class__.__name__ is part_name:
                #print("Returning part " + part_name)
                return entry['part']

    def start(self):
        """
        Start vehicle's main drive loop.

        This is the main thread of the vehicle. It starts all the new
        threads for the threaded parts then starts an infinit loop
        that runs each part and updates the memory.

        Parameters
        ----------

        rate_hz : int
            The max frequency that the drive loop should run. The actual
            frequency may be less than this if there are many blocking parts.
        max_loop_count : int
            Maxiumum number of loops the drive loop should execute. This is
            used for testing the all the parts of the vehicle work.
        """

        try:
            self.on = True

            for entry in self.parts:
                if entry.get('thread'):
                    #start the update thread
                    entry.get('thread').start()

            print('-----------------Vehicle started and ready to go-----------------')
            time.sleep(1)
        except KeyboardInterrupt:
            pass

    def run(self, rate_hz=10, max_loop_count=None):
        '''
        just run the drive loop
        '''
        loop_count = 0
        self.running = True
        print('Starting drive loop')
        while self.running:
            start_time = time.time()
            loop_count += 1

            self.update_parts()

            #stop drive loop if loop_count exceeds max_loopcount
            if max_loop_count and loop_count > max_loop_count:
                self.running = False

            sleep_time = 1.0 / rate_hz - (time.time() - start_time)
            if sleep_time > 0.0:
                time.sleep(sleep_time)
        return self.running

    def pause(self):
        '''
        Shutdown (set to zero) the throttle and steering
        '''
        print('Vehicle is paused.')
        for entry in self.parts:
            if entry['part'].__class__.__name__ is "PWMThrottle":
                print("Shutting down Throttle")
                entry['part'].shutdown()
            if entry['part'].__class__.__name__ is "PWMSteering":
                print("Shutting down Steering")
                entry['part'].shutdown()

    def circle_turn(self, rate_hz=10):
        '''
        **Description**
        Make the rover turn in a circle
        '''
        print("Performing circle turn")
        steering = self.get("PWMSteering")
        throttle = self.get("PWMThrottle")
        turn_duration = 0

        # Perform the first point of the turn
        print("First point of turn")
        steering.run(-1)
        while turn_duration < 100:
            start_time = time.time()
            throttle.run(-.25)
            turn_duration = turn_duration + 1
            sleep_time = 1.0 / rate_hz - (time.time() - start_time)
            if sleep_time > 0.0:
                time.sleep(sleep_time)

    def three_point_turn(self, rate_hz=10):
        '''
        **Description**
        Make the rover perform a three point turn so it's facing 180 degrees from start
        '''

        print("Performing three point turn")
        steering = self.get("PWMSteering")
        throttle = self.get("PWMThrottle")
        print(rate_hz)

        def partial_turn(duration, angle, speed):
            turn_duration = 0
            while turn_duration < duration:
                start_time = time.time()
                steering.run(angle)
                throttle.run(speed)
                turn_duration = turn_duration + 1
                sleep_time = 1.0 / rate_hz - (time.time() - start_time)
                if sleep_time > 0.0:
                    time.sleep(sleep_time)
            self.pause()

        # Perform the first point of the turn
        print("First point of turn")
        partial_turn(25, -1, -.25)
        time.sleep(5)

        # Perform the second point
        print("Second point of turn")
        partial_turn(50, 1, .25)
        time.sleep(5)

        # Perform the third point
        print("Third point of turn")
        partial_turn(25, -1, -.30)

    def update_parts(self):
        '''
        loop over all parts
        '''
        for entry in self.parts:
            #don't run if there is a run condition that is False
            run = True

            if entry.get('run_condition'):
                run_condition = entry.get('run_condition')
                run = self.mem.get([run_condition])[0]
                #print('run_condition', entry['part'], entry.get('run_condition'), run)

            if run:
                p = entry['part']
                #get inputs from memory
                inputs = self.mem.get(entry['inputs'])
                #print(self.mem.d)

                #run the part
                if entry.get('thread'):
                    outputs = p.run_threaded(*inputs)
                    #print(self.mem.d)
                else:
                    outputs = p.run(*inputs)

                #save the output to memory
                if outputs is not None:
                    self.mem.put(entry['outputs'], outputs)

    def stop(self):
        '''
        Shutdown the entire vehicle
        '''
        print('Shutting down vehicle and its parts...')
        for entry in self.parts:
            try:
                entry['part'].shutdown()
            except Exception as e:
                print(e)
        print('-----------------Vehicle has been safely shutdown-----------------')
        print(self.mem.d)
