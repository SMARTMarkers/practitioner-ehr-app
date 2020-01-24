#!/usr/bin/env python3


from fhirclient.client import FHIRClient
from fhirclient.models import observation, servicerequest, questionnaire, valueset, practitioner
from . import request, result, instrument, promis, schedule

class PROClient(FHIRClient):

    # ---------------- INSTRUMENT LIST --------------------- # 
    
    @property
    def instrumentlist_questionnaires(self): 
       entries = questionnaire.Questionnaire.where(None).perform(self.server).entry
       instruments = [instrument.PROInstrument.fromQuestionnaire(entry.resource) for entry in entries] if entries else []
       return instruments

    
    # IMPORTANT #############################################################################################
    # The PROMIS API service providers AssessmentCenter is undergoing migration.
    # This repo will be updated to fetch PROMIS instruments directly from AC after the migration is completed.
    # please contact http://assessmentcenter.net for more info
             
    @property
    def instrumentlist_promis(self): 
        return promis.PROMIS.list() 

    @property
    def instrumentlist_activetasks(self): 
       entries = valueset.ValueSet.where(struct={'reference': 'http://researchkit.org'}).perform(self.server).entry
       if entries:
           return instrument.PROInstrument.fromValueSet(entries[0].resource, "activetask")
       return None


    @property
    def instrumentlist_devices(self): 
       entries = valueset.ValueSet.where(struct={'code': 'omronBloodPressure'}).perform(self.server).entry
       if entries:
           return instrument.PROInstrument.fromValueSet(entries[0].resource, "webrepository")
       return None


    @property
    def instrumentList_activity(self):
       entries = valueset.ValueSet.where(struct={'code': '41950-7'}).perform(self.server).entry
       if entries:
           return instrument.PROInstrument.fromValueSet(entries[0].resource, "activity")
       return None



    @property
    def instrumentlist_clinicalrecords(self):
        entries = valueset.ValueSet.where(struct={'reference': 'http://apple.com'}).perform(self.server).entry
        if entries:
           return instrument.PROInstrument.fromValueSet(entries[0].resource, "clinicalrecord")
        return None

    # ----------------- FHIR Requests ---------------------- # 

    def getrequests(self):
        searchparam = {
            'patient': self.patient.id
        }
        print(searchparam)
        entries = servicerequest.ServiceRequest.where(searchparam).perform(self.server).entry
        prorequests = [request.PRORequest.fromServiceRequest(entry.resource) for entry in entries] if entries else [] 
        self.requests =  prorequests if len(prorequests) > 0 else None
        return self.requests


    def dispatch_request(self, instrumenttype, instrumentidentifier, practitioner_resource, schedule_type, start_date=None, end_date=None):

        instr = None
        request_schedule = None

        if instrumenttype == 'webrepository':
            instr = [instr for instr in self.instrumentlist_devices if instr.identifier == instrumentidentifier][0]
        elif instrumenttype == 'activity':
            instr = [instr for instr in self.instrumentList_activity if instr.identifier == instrumentidentifier][0]
        elif instrumenttype == 'survey':
            instr = [instr for instr in self.instrumentlist_questionnaires if instr.identifier == instrumentidentifier][0]
        elif instrumenttype == 'activetask':
            instr = [instr for instr in self.instrumentlist_activetasks if instr.identifier == instrumentidentifier][0]
        elif instrumenttype == 'clinicalrecord':
            instr = [instr for instr in self.instrumentlist_clinicalrecords if instr.identifier == instrumentidentifier][0]
        
        if instr is None:
            return None
        
        if schedule_type != 'instant':
            if schedule_type == 'weekly':
                freq = schedule.Frequency('wk', 7, 1)
            else:
                freq = schedule.Frequency('m', 29, 1)
            request_schedule = schedule.PROSchedule(schedule.Period(start_date, end_date), freq)
        
        return self.dispatchRequest(instr, practitioner_resource, selected_schedule=request_schedule)


    def dispatchRequest(self, selected_instrument, practitioner_resource, selected_schedule=None):
        new_request = request.PRORequest(instrument=selected_instrument)
        print((new_request.createRequestResource(self.server, patient=self.patient).as_json()))
        res_id = new_request.create(self.server, patient=self.patient, practitioner=practitioner_resource, schedule=selected_schedule)
        if res_id is not None:
            return new_request
        return None




    def getobservations(self):
        if self.ready:
            entries = observation.Observation.where({
                'patient'   :   self.patient_id or 'b85d7e00-3690-4e2a-87a0-f3d2dfc908b3',
                'category'  :   'survey',
                '_sort'     :   '-date'
                }).perform(self.server).entry
            proresults = [result.PROResult.fromObservation(entry.resource) for entry in entries] if entries else [] 
            self.results = proresults
            return self.results
        else:
            print('server not ready')
            return []


    def user_practitioner(self, practitioner_id):
        if self.ready:
            practitioner_resource = practitioner.Practitioner.read(practitioner_id, self.server)
            return practitioner_resource













class SMARTClients(object): 

    @classmethod
    def hspc_open(self, appId=None):
        appId = appId or 'appIdentifier'
        settings = { 
                'app_id'   : appId,
                'api_base' : 'https://api.logicahealth.org/r4smchip/open'
        }
        client = FHIRClient(settings=settings) 
        client.patient_id = 'SMART-1288992'
        return client


    @classmethod
    def smartsandbox(self, appId=None):
        appId = appId or 'appIdentifier'
        settings = { 
                'app_id'   : appId,
                'api_base' : 'https://r4.smarthealthit.org'
        }
        client = FHIRClient(settings=settings) 
        client.patient_id = '082e1e50-6561-42a4-9b5f-0e5094142756'
        return client

