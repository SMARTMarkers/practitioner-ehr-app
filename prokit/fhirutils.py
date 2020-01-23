#!/usr/bin/env python3

from fhirclient.models import codeableconcept, coding

class FHIRUtils:

    @staticmethod
    def codeableconcept(code, system, display=None): 
        codeableConcept = codeableconcept.CodeableConcept() 
        newcoding = coding.Coding() 
        newcoding.system = system
        newcoding.code   = code
        newcoding.display = display
        codeableConcept.coding = [newcoding]
        codeableConcept.text = display
        return codeableConcept

