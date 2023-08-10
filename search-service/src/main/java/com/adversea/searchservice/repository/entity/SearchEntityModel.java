package com.adversea.searchservice.repository.entity;


import lombok.Getter;
import lombok.Setter;
import org.springframework.data.annotation.Id;
import org.springframework.data.elasticsearch.annotations.Document;
import org.springframework.data.elasticsearch.annotations.Field;


import java.util.List;
import java.util.Map;

@Getter
@Setter
@Document(indexName = "adversea_search", createIndex = false)
public class SearchEntityModel {

    @Id
    private String id;

    private String name;

    @Field(name = "name_ascii")
    private String nameAscii;

    private List<String> aliases;

    @Field(name = "aliases_ascii")
    private List<String> aliasesAscii;

    @Field(name = "aliases_count")
    private Map<String, Integer> aliasesCount;

    private String type;

    @Field(name = "information_source")
    private List<String> informationSource;

    private Map<String, Integer> locations;

    @Field(name = "ams_articles")
    private List<String> amsArticles;

    @Field(name = "sl_record")
    private List<String> slRecord;

    @Field(name = "pep_record")
    private List<String> pepRecord;

}

