package com.adversea.searchservice.repository;

import com.adversea.searchservice.repository.entity.SearchEntityModel;
import org.springframework.data.domain.Pageable;
import org.springframework.data.elasticsearch.annotations.Query;
import org.springframework.data.elasticsearch.repository.ElasticsearchRepository;

import java.util.List;

public interface SearchRepositoryElastic extends ElasticsearchRepository<SearchEntityModel, String> {
    @Query("""
            {
            	"query_string": {
            			"query": "?0"
            		}
            }
            """)
    List<SearchEntityModel> searchDatabaseByName(String name, Pageable pageable);
}
