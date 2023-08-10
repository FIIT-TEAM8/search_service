package com.adversea.searchservice.service;

import com.adversea.searchservice.repository.SearchRepositoryElastic;
import com.adversea.searchservice.repository.entity.SearchEntityModel;
import com.adversea.searchservice.utility.Mapper;
import org.SwaggerCodeGenAdversea.model.SearchEntityResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class SearchService {
    @Autowired
    SearchRepositoryElastic repository;

    @Autowired
    Mapper mapper;

    public List<SearchEntityResponse> search(String name) {
        List<SearchEntityResponse> convertedResult = new ArrayList<>();
        List<SearchEntityModel> result;
        result = repository.searchDatabaseByName(name, PageRequest.of(0,3));
        for (SearchEntityModel model : result) {
            convertedResult.add(mapper.modelToResponse(model));
        }
        return convertedResult;
    }
}
