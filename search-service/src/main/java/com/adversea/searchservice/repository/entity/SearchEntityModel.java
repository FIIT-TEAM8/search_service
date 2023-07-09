package com.adversea.searchservice.repository.entity;


import lombok.Getter;
import lombok.Setter;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

import java.util.List;
import java.util.Map;

@Getter
@Setter
@Document("adversea_search")
public class SearchEntityModel {


    @Field("name")
    @Indexed
    private String name;

    @Field("name_ascii")
    @Indexed
    private String nameAscii;

    @Field("type")
    private String type;

    @Field("locations")
    private Map<String, Integer> locations;

    @Field("information_source")
    private List<String> source;

}

