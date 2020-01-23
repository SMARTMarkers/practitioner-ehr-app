#!/usr/bin/env python3

import datetime
from fhirclient.server import FHIRServer
from fhirclient.models import codeableconcept, coding, patient, practitioner, fhirreference, servicerequest, fhirdate, domainresource, questionnaire
from . import schedule, request, instrument


class PRORequest(object): 

    def __init__(self, instrument=None):

        self.identifier = None 
        """ Identifier of the Request usually inferred from the Requesting Resource
        Type `str` 
        """ 
        
        self.title = instrument.title if instrument else None
        """ Title of the Request 
        Type `str`
        """ 

        self.status = None 
        """ Status of the Request
        Type `str`
        """ 

        self._requester = None 
        """ Requesting Authority identity; usually a practitioner
        Type `practitioner.Practitioner`
        """ 

        self.requesterentity = None 
        """ Requesting Authority entity; usually a healthcare system
        Type `str`
        """ 

        self._requestdate = None
        """ Date the Request was dispatched
        """ 

        self.category = None 
        """ Category of the request
        """ 

        self.schedule = None 
        """ Associated Schedule of the Request
        Type `PROSchedule`
        """

        self.instrument = instrument
        """ Instrument requested for PRO Assessment
        Type `PROInstrument`
        """ 

        self.resource = None 
        """ Raw FHIR Resource
        Type `DomainResource`
        """ 


    @property
    def requestername(self):
        if self._requester:
            humanname = self._requester.name[0]
            if humanname.text: 
                return humanname.text
            else:
                name = (' ').join(humanname.given) + ' ' + humanname.family
                return f'{name}, {humanname.suffix}' if humanname.suffix else name
        else:
            return f'Practitioner: #{self._requester.id}'



    @property 
    def is_active(self):
        return True if self.status and self.status == 'active' else False

    @property
    def requestdate(self):
        return self._requestdate or self.resource.meta.lastUpdated.date

    @property
    def resourcecoding(self): 
        if self.resource: 
            return self.resource.code.coding[0] 
        else:
            return None
    
    @property
    def code(self): 
        if self.resourcecoding:
            return self.resourcecoding.code
        elif self.instrument.code:
            return self.instrument.code
        else:
            return None 
        
    @property
    def codesystem(self):
        if self.resourcecoding:
            return self.resourcecoding.system
        elif self.instrument.code:
            return self.instrument.codesystem
        else:
            return None 
 
    def is_questionnaire(self): 
        if self.instrument is None: 
            return False
        return True if type(self.instrument.resource) is questionnaire.Questionnaire else False

    def instrument_details(self):
        return 'PRO Instrument #212'
        

    @classmethod
    def fromServiceRequest(cls, servicerequest=servicerequest.ServiceRequest):

        request = PRORequest() 
        request.identifier = servicerequest.id
        request.resource  = servicerequest 
        request.status = servicerequest.status
        if servicerequest.requester is not None:
            request._requester = servicerequest.requester.resolved(practitioner.Practitioner)
        request._requestdate = servicerequest.authoredOn
        # initialize instrument from service request

        if servicerequest.code is not None and servicerequest.code.coding is not None:
            instr = instrument.PROInstrument.fromCoding(code=servicerequest.code.coding[0])
            request.instrument = instr
        

        return request


    def createRequestResource(self, server=FHIRServer, patient=None, practitioner=None, schedule=None): 

        from . import fhirutils

        if self.instrument is None: 
            print("missin instrument to request")
            return None


        # Take instrument or from the argument
        instr = self.instrument 

        # create new `ServiceRequest`
        serviceRequest = servicerequest.ServiceRequest()
        serviceRequest.status = 'active'
        serviceRequest.intent = 'plan' 
        serviceRequest.category = self.category or [PRORequest.EvaluationCodeableConcept()]

        # Coding Request
        if instr.code is not None:
            serviceRequest.code = fhirutils.FHIRUtils.codeableconcept(instr.code, instr.codesystem, instr.title)

        # Tag Patient
        patientreference = fhirreference.FHIRReference() 
        patientreference.reference = f'Patient/{patient.id}'
        serviceRequest.subject = patientreference

        # Tag Practitioner
        if practitioner is not None:
            practitionerreference = fhirreference.FHIRReference() 
            practitionerreference.reference = f'Practitioner/{practitioner.id}'
            practitionerreference.display = practitioner.name[0].text
            serviceRequest.requester = practitionerreference


        # Schedule
        if schedule is not None: 

            timing_resource = schedule.createTimingResource()
            serviceRequest.occurrenceTiming = timing_resource 
        else:
            now = datetime.datetime.utcnow() 
            fhirDate = fhirdate.FHIRDate() 
            fhirDate.date = now
            serviceRequest.occurrenceDateTime = fhirDate
        
        # Questionnaire Extension if Instrument is a `Questionnaire`
        if self.is_questionnaire(): 
            extension = PRORequest.QuestionnaireExtension(questionnaire=self.instrument.resource)
            serviceRequest.extension = [extension] 

        return serviceRequest
    

    #
    # Create Resource on the receiver
    #
    def create(self, server=FHIRServer,  patient=None, practitioner=None, schedule=None): 

        if self.instrument is None: 
            print("cannot create request, instrument not found")
            return None 

        request = self.createRequestResource(server,  patient, practitioner, schedule) 
        response = request.create(server)  
        if response is not None: 
            self.resource = servicerequest.ServiceRequest(response)
            self.identifier = response['id']
            return self.identifier
        return None

    @staticmethod 
    def EvaluationCodeableConcept(): 
        from . import fhirutils
        return fhirutils.FHIRUtils.codeableconcept('386053000', 'http://snowmed.info/sct', 'Evaluation procedure (procedure)')




    @staticmethod
    def QuestionnaireExtension(questionnaire=questionnaire.Questionnaire):
        from fhirclient.models import extension
        extension = extension.Extension() 
        extension.url = 'http://hl7.org/fhir/StructureDefinition/servicerequest-questionnaireRequest'
        reference = fhirreference.FHIRReference()
        reference.reference = f'Questionnaire/{questionnaire.id}'
        extension.valueReference = reference
        return extension 
     
    if __name__ == '__main__':
        import request, smartclient, promis 
        client = smartclient.SMARTClients.hspc_open()
        print(client.patient_id)
        print(client)
        req = request.PRORequest().createRequestResource(client.server, promis.PROMIS.PainBehavior(), client.patient_id) 
        print(req.as_json())
        
