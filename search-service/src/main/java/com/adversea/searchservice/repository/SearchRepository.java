package com.adversea.searchservice.repository;

import com.adversea.searchservice.repository.entity.SearchEntityModel;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface SearchRepository extends MongoRepository<SearchEntityModel, String> {

}
