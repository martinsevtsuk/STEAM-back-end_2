package com.example.steam2.services;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.HashMap;
import java.util.Map;

@Service
public class MLServiceClient {

    private static final Logger logger = LoggerFactory.getLogger(MLServiceClient.class);
    private final RestTemplate restTemplate;

    @Value("${ml.service.url:http://ml-service:5000}")
    private String mlServiceUrl;

    public MLServiceClient() {
        this.restTemplate = new RestTemplate();
    }

    public Integer getPeopleCount(String base64Frame) {
        try {
            String url = mlServiceUrl + "/detect";

            Map<String, String> request = new HashMap<>();
            request.put("frame", base64Frame);

            MLResponse response = restTemplate.postForObject(url, request, MLResponse.class);

            if (response != null && response.isSuccess()) {
                logger.info("Successfully detected {} people", response.getPeople_count());
                return response.getPeople_count();
            } else {
                logger.error("ML service returned failure: {}",
                        response != null ? response.getError() : "null response");
                return null;
            }
        } catch (Exception e) {
            logger.error("Error calling ML service: {}", e.getMessage());
            return null;
        }
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    private static class MLResponse {
        private boolean success;
        private Integer people_count;
        private String timestamp;
        private String error;
    }
}
