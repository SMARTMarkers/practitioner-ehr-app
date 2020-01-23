Clinic PGHD Requester App
===========================


A [SMART on FHIR][sf] app to dispatch patient generated health data (PGHD) requests to the `patient`. An array of [instruments][ilist] is compiled from FHIR `ValueSets` stored in the clinic's FHIR server. 

This is a companion app for the [SMART Markers][sm] framework and its apps. As the FHIR `ServiceRequest` is generated, the downstream SMART Markers apps can fulfill those requests by generated or aggregating data and submitting back to the health system's FHIR server.

This app is fully SMART on FHIR compliant and represents the concept of sending PGHD requests with emphasis on interoperability. 


Installation
-----------

1. Clone this repository: 
2. Install modules 
3. Edit `app.py` with the settings for the SMART on FHIR endpoints and SMART credentails 
4. run app.py


```bash
$ git clone https://github.com/SMARTMarkers/practitioner-ehr-app.git
$ cd practitioner-ehr-app
$ pip3 install fhirclient
$ chmod +x app.py

//Edit app.py with settings for the SMART on FHIR endpoints
$ ./app.py
```

Notice
----------
This work is under further development and eventually will become a framework to support multiple SMART EHR apps.

[sf]: https://docs.smarthealthit.org
[ilist]: https://github.com/SMARTMarkers/smartmarkers-ios/tree/master/Sources/Instruments
[sm]: https://github.com/SMARTMarkers/smartmarkers-ios




