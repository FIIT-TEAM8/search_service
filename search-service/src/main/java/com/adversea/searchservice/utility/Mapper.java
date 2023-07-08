package com.adversea.searchservice.utility;


import com.adversea.searchservice.repository.entity.SearchEntityModel;
import org.SwaggerCodeGenAdversea.model.SearchEntityResponse;
import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Component;


import java.util.*;
import java.util.stream.Collectors;

@Component
public class Mapper {

    private static final int TOP_NUMBER_OF_LOCATIONS = 3;

    public SearchEntityResponse modelToResponse(SearchEntityModel model) {
        SearchEntityResponse response = new SearchEntityResponse();
        response.setName(model.getName());
        response.setNameAscii(model.getNameAscii());
        response.setType(SearchEntityResponse.TypeEnum.fromValue(model.getType()));
        response.setSource(model.getSource());
        response.setLocations(sortLocations(model.getLocations(), TOP_NUMBER_OF_LOCATIONS));
        return response;

    }

    private List<String> sortLocations(Map<String, Integer> locations, int numberOfLocations) {
        List<Map.Entry<String, Integer>> list = new ArrayList<>(locations.entrySet());
        list.sort(Collections.reverseOrder(Map.Entry.comparingByValue()));

        List<String> sortedLocations = new ArrayList<>();
        for (Map.Entry<String, Integer> entry : list) {
            sortedLocations.add(entry.getKey());
        }

        return sortedLocations.stream().limit(numberOfLocations).collect(Collectors.toList());
    }



}
