#!/usr/bin/env python3

from fhirclient.models import questionnaire, valueset, coding

class PROInstrument(object): 

    def __init__(self, identifier=None):

        self.identifier = identifier 
        """ Unique Identifier of the Instrument
        Type `str`. """ 

        self._title = None
        """ Title
        Type `str`. """ 

        self.version = None 
        """ Version 
        Type `str`."""

        self.instrumenttype = None
        """ Type: device|survey|activetask|
        Type `str`."""

        self.code = None
        """ Ontological code 
        Type `str`""" 

        self.codesystem = None 
        """ Ontological system uri
        Type `str` """ 

        self.resource = None 
        """ Actual Instrument """ 

    @property
    def title(self):
        return self._title  or f'Code: {self.code}' or ''


    @classmethod
    def fromCoding(cls, code=coding.Coding):
        instr = PROInstrument()
        instr.identifier = f'{code.code}|{code.system}'
        instr._title = code.display
        instr.code = code.code
        instr.codesystem = code.system
        instr.resource = code
        return instr


    @classmethod
    def fromQuestionnaire(cls, q=questionnaire.Questionnaire): 
        instrument = PROInstrument() 
        instrument.title = q.title or q.name
        instrument.identifier = q.id
        instrument.resource = q
        instrument.instrumenttype = 'survey'
        instrument.version = q.version
        if q.code is not None:
            qcoding = q.code[0]
            instrument.code = qcoding.code
            instrument.codesystem = qcoding.system
            instrument.title = q.title or q.name or qcoding.display
        return instrument


    @classmethod
    def fromValueSet(cls, valueset=valueset.ValueSet, instrument_type=None):
        instruments = [] 
        if valueset.compose and valueset.compose.include: 
            vsinclude = valueset.compose.include 
            for element in vsinclude:
                system = element.system
                concepts = element.concept
                for concept in concepts:
                    instrument = PROInstrument()
                    instrument.identifier = f'{concept.code}{system}'
                    instrument.code = concept.code
                    instrument.codesystem = system
                    instrument._title = concept.display
                    instrument.type = instrument_type
                    instruments.append(instrument) 

        return instruments





    def startSession(self): 
        from instrumentrenderer import InstrumentRenderer 
        return InstrumentRenderer(self) 
   



if __name__ == '__main__': 
    p = PROInstrument('identifier')
    print(p)
    print(p.title) 
    print(p.identifier) 
    vars(p)
    print(p.startSession()) 

