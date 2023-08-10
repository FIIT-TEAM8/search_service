## data-loader
contains some scripts that load data from articles / sanction lists into search database

## search-service

spring project that contains the meat of the service. Runs on Java 17 and spring boot 3 Needs these ENV variables configured:

* ELASTIC_URI - host + port combo of elastic instance machine.


To run localy, dont forget to to do
```
mvn clean compile
```

This will create all the necessary classes so you can run it in your IDE. This is becasue this project uses OpenAPI spec file to generate the server stup interface + some DTOs that are required for function.


## elastic fields explanation
* name - name of the entity
* name_ascii - name of entity in ASCII only
* aliases - array of aliases
* aliases_ascii - array of ASCII aliases
* aliases_count - histogram of aliases. Similar structure to the locations field but with aliases. 
* type - person / organization
* information_source - array of all identified person sources. Can contain values ams / pep / sl
* locations - histogram of locations where this person was. Its basically a json, its structure can be like this: {"Bratislava": 12, "Vienna": 5}. Using this we can determine the most common locations for an entity
* ams_articles - array of links to articles where this person was found
* sl_record - array of SL record IDs
* pep_record - array of PEP record IDs

## swagger
https://app.swaggerhub.com/apis-docs/dominik-horvath/search-service/1.0.0
