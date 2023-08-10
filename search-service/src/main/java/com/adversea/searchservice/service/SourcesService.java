package com.adversea.searchservice.service;

import com.adversea.searchservice.repository.SearchRepositoryElastic;
import com.adversea.searchservice.repository.entity.SearchEntityModel;
import com.adversea.searchservice.utility.Mapper;
import org.SwaggerCodeGenAdversea.model.SourcesResult;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.util.Optional;

@Service
public class SourcesService {
    @Autowired
    SearchRepositoryElastic repository;

    @Autowired
    Mapper mapper;

    public SourcesResult getSourcesForEntity(String id) {
        Optional<SearchEntityModel> model = repository.findById(id);
        if (model.isPresent()) {
            return mapper.modelToSourcesResult(model.get());
        } else {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Entity with id " + id + " not found.");
        }
    }
}
