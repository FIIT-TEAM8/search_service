package com.adversea.searchservice.service;

import com.adversea.searchservice.repository.SearchRepository;
import com.adversea.searchservice.repository.entity.SearchEntityModel;
import com.adversea.searchservice.utility.Mapper;
import org.SwaggerCodeGenAdversea.model.SearchEntityResponse;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class SearchService {
    @Autowired
    SearchRepository repository;

    @Autowired
    Mapper mapper;

    public List<SearchEntityResponse> search(String method,String name) {
        List<SearchEntityModel> mongoResult = new ArrayList<>();
        if (method.equals("exact")) {
            mongoResult = repository.searchExactName(name.toLowerCase());
        } else if (method.equals("rough")) {
            name = StringUtils.stripAccents(name);
            mongoResult = repository.searchRoughName(name.toLowerCase());
        }
        List<SearchEntityResponse> convertedResult = new ArrayList<>();
        for (SearchEntityModel model : mongoResult) {
            convertedResult.add(mapper.modelToResponse(model));
        }
        return convertedResult;
    }
}
