## data-loader
contains some scripts that load data from articles / sanction lists into search database

## search-service

spring project that contains the meat of the service. Runs on Java 17 and spring boot 3 Needs these ENV variables configured:

* MONGO_HOST
* MONGO_PORT
* MONGO_DATABASE - name of database that is used for search (should be adversea_search)
* MONGO_USERNAME
* MONGO_PASSWORD


To run localy, dont forget to to do
```
mvn clean compile
```

This will create all the necessary classes so you can run it in your IDE. This is becasue this project uses OpenAPI spec file to generate the server stup interface + some DTOs that are required for function.

## swagger
https://app.swaggerhub.com/apis-docs/dominik-horvath/search-service/1.0.0
