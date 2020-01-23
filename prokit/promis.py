#!/usr/bin/env python3


from . import instrument

class PROMIS(instrument.PROInstrument): 

    def __init__(self, identifier, title=None, loinc=None):
        super().__init__(identifier)

        self._title = title 

        self.instrumenttype = 'survey'

        if loinc is not None: 
            self.code = loinc
            self.codesystem = 'http://loinc.org'


    @classmethod
    def Fatigue(self):
        return PROMIS('61795-1', 'PROMIS Bank v1.0 - Fatigue', '61795-1')

    @classmethod
    def Anxiety(self):
        return PROMIS('61922-1', 'PROMIS Bank v1.0 - Anxiety', '61922-1') 

    @classmethod
    def Sleep(self): 
        return PROMIS('62010-4', 'PROMIS Bank v1.0 Sleep-Related Impairment', '62010-4') 

    @classmethod
    def PainBehavior(self): 
        return PROMIS('62194-6', 'PROMIS SF v1.0 - Pain Behavior 7a', '62194-6') 


    @classmethod
    def list(cls, filters=None): 
        import json, pkg_resources
        path = 'static/promislist.json'
        filepath = pkg_resources.resource_filename(__name__, path)
        promisjson = json.load(open(filepath, 'r'))
        forms = promisjson['Form']
        promis = [PROMIS(d['OID'], d['Name'], d['LOINC_NUM']) for d in forms]
        return promis


if __name__ == '__main__':

    anxiety = PROMIS('61922-1') 
    print(anxiety) 
    print(PROMIS.Sleep().identifier)  
    p = PROMIS.Sleep() 
    print(p)
    print(p.identifier) 
    print(p.title) 

    print(PROMIS.PainBehavior().title) 
    print(PROMIS.PainBehavior().identifier) 
    print(p.code) 
