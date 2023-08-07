package com.adversea.searchservice.controller;


import com.adversea.searchservice.service.SearchService;
import jakarta.validation.constraints.NotNull;
import org.SwaggerCodeGenAdversea.api.SearchApi;
import org.SwaggerCodeGenAdversea.model.SearchEntityResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/")
public class SearchController implements SearchApi {

    @Autowired
    SearchService service;

    @Override
    public ResponseEntity<List<SearchEntityResponse>> searchName(@NotNull String name) {
        List<SearchEntityResponse> response = service.search(name);
        return ResponseEntity.ok(response);
    }
}
