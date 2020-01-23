#!/usr/bin/env python3

import datetime
from fhirclient.models import observation, questionnaireresponse, fhirdate, patient, domainresource, fhirreference
from fhirclient.server import FHIRServer
from . import request

class PROResult(object): 

    def __init__(self, identifier=None, description=None,  date=None, value=None, title=None, code=None, codesystem=None, codedisplay=None) : 
      
        self.identifier = identifier

        self.date = date

        self.value = value

        self.title = title 

        self.description = description 
        
        self.code = code 

        self.codesystem = codesystem 

        self.codedisplay = codedisplay 

        self.resource = None 
        
        self.request = None 

        
 

    @classmethod
    def create(cls, value=str, date=datetime.datetime, request=None): 
        
        result = PROResult()
        
        result.value = value 

        result.date = date 
        
        result.code = request.code 

        result.codesystem = request.codesystem

        result.codedisplay = request.title 

        result.request = request

        return result 




    @classmethod
    def fromObservation(cls, observation=observation.Observation): 
        
        result = PROResult() 
        
        result.identifier = observation.id

        result.date = observation.effectiveDateTime.date

        result.title = observation.code.text or f'Observation: #{observation.id}'

        if observation.code:

            result.code = observation.code.coding[0].code or None 

            result.codesystem = observation.code.coding[0].system or None 

            result.codedisplay = observation.code.coding[0].display or None 

        result.resource = observation
        
        return result


    def create_or_update(self, server=FHIRServer, patient=patient.Patient, member=None):

        obs = self.resource or PROResult.createobservation(self.value, self.code, self.codesystem, self.codedisplay, self.date) 

        # Patient
        patientreference = fhirreference.FHIRReference() 
        patientreference.reference = f'Patient/{patient.id}'
        obs.subject = patientreference


        # request
        requestresource = self.request.resource if self.request else None
        if requestresource is not None:
            serviceRequestReference = fhirreference.FHIRReference()
            serviceRequestReference.reference = f'ServiceRequest/{requestresource.id}'
            obs.basedOn = [serviceRequestReference] 
            

        # member resources
        if member is not None:
            ref = fhirreference.FHIRReference()
            ref.reference = f'QuestionnaireResponse/{member.id}'
            ref.hasMember = [ref] 

        response = obs.create(server)
        if response is not None: 
            self.resource = response
            self.identifier = response['id']
            return self.identifier
            
        return None


    @classmethod
    def createobservation(cls, valueString=str, code=None, codesystem=None, codedisplay=None, date=None): 

        from . import fhirutils

        obs = observation.Observation()
        
        # Date
        fdate = fhirdate.FHIRDate()
        fdate.date = date or datetime.datetime.utcnow()
        obs.effectiveDateTime = fdate 
        
       
        # Ontology
        if code is not None and codesystem is not None: 
            obs.code = fhirutils.FHIRUtils.codeableconcept(code, codesystem, codedisplay)

        # status
        obs.status = 'final'

        # Value
        obs.valueString = valueString or None

        return obs

        



   


if __name__ == '__main___':

    pass

