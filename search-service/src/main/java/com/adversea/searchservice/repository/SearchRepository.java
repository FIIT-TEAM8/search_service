package com.adversea.searchservice.repository;

import com.adversea.searchservice.repository.entity.SearchEntityModel;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;

import java.util.List;

public interface SearchRepository extends MongoRepository<SearchEntityModel, String> {

    @Query("{name: '?0'}")
    List<SearchEntityModel> searchExactName(String name);

    @Query("{name_ascii: '?0'}")
    List<SearchEntityModel> searchRoughName(String name);

}
