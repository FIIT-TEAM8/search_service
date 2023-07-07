package com.adversea.searchservice.service;

import com.adversea.searchservice.repository.SearchRepository;
import com.adversea.searchservice.repository.entity.SearchEntityModel;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class SearchService {
    @Autowired
    SearchRepository repository;


    public void test() {
        repository.save(new SearchEntityModel());
    }
}
