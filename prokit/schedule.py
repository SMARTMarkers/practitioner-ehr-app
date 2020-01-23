#!/usr/bin/env python
""" 
A class to handle the PRO Requesting Resource
Receives FHIR `Timing`
""" 

from enum import Enum 
from datetime import date, timedelta, datetime

class SlotStatus(Enum): 
    due         =   "due" 
    upcoming    =   "upcoming" 
    overdue     =   "overdue" 
    unknown     =   "unknown" 
    completed   =   "completed" 

class Period:

    def __init__(self, start=str, end=str): 

        self.start = start 
        """ Start date of the Period
        Type `str`
        """ 

        self._start = datetime.strptime(start, '%Y-%m-%d').date()

        self._end = datetime.strptime(end, '%Y-%m-%d').date()
        
        self.end = end 
        """ End date of the period
        Type `str` 
        """ 

    def __str__(self): 
        return f'Period: {self.start} -- {self.end}' 

    def contains(self, date=date): 
        if self._start <= date <= self._end:
            return True 
        else: 
            return False 


    def status(self):
        today = date.today() 
        if self.contains(today): 
            return SlotStatus.due 
        elif today < self._start: 
            return SlotStatus.overdue
        elif today > self._end: 
            return SlotStatus.upcoming 
        else:
            return SlotStatus.unknown



class Frequency: 

    def __init__(self, unit, value=0, unit_period=1):
        self.value = value 
        """
        Type `int`
        """ 

        self.unit = unit 
        """
        Type `str`
        """ 

        self.unit_period = unit_period
        """
        Type `period unit`
        """

        self.unitDays = 7 if unit == 'wk' else 1

    def __str__(self): 
        return f'freq: {self.value} every {self.unitDays} days'


class Slot: 

    def __init__(self, period=Period): 

        self.period = period 
        """
        Type `Period` 
        """ 
        
        self.status = period.status() 
        """
        Type: `SlotStatus`
        """ 

    @property
    def iscurrent(self):
        today = date.today()
        return self.period.contains(today) 




class PROSchedule: 


    def __init__(self, period=Period, frequency=Frequency, overrideStatus=None):
        
        self.period = period 
        """ 
        Type `Period`
        """ 

        self.frequency = frequency 
        """ 
        Type `Frequency`
        """ 

        self.status = overrideStatus
        """
        Type `SlotStatus`
        """


    def createTimingResource(self):
        
        from fhirclient.models import timing, fhirdate
        timing_resource = timing.Timing() 

        # once(frequency) per week(period/periodUnit)
        repeat = timing.TimingRepeat()
        repeat.frequency = int(self.frequency.value)
        repeat.periodUnit = self.frequency.unit
        repeat.period = float(self.frequency.unit_period) 

        # Start Date
        start_fhirdate = fhirdate.FHIRDate(self.period.start)
        end_fhirdate   = fhirdate.FHIRDate(self.period.end)

        print(start_fhirdate)
        print(end_fhirdate)
        print(fhirdate.FHIRDate(self.period.start))

        from fhirclient.models import period
        fhir_period = period.Period()
        fhir_period.start = start_fhirdate
        fhir_period.end   = end_fhirdate
        repeat.boundsPeriod = fhir_period 

        timing_resource.repeat = repeat 
        return timing_resource


if __name__ == "__main__": 
   
    today = date.today() 
    past = today - timedelta(days=32) 
    future = today + timedelta(days=23) 
    future2 = future + timedelta(days=23)

    p = Period('2019-01-01', '2020-01-01') 
    slot = Slot(p) 
    print(p) 
    print(slot.iscurrent) 
    print(slot.status) 
    print('future----')
    frequency = Frequency('wk', 1) 
    print(frequency)
    schedule = PROSchedule(p, frequency)
    print(schedule)
    print(schedule.createTimingResource())

    

