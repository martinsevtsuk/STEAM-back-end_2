package com.example.steam2.managers;

import com.example.steam2.dao.CameraPeopleDao;
import com.example.steam2.domains.CameraPeopleNumber;
import com.example.steam2.dto.CameraFrameDTO;
import com.example.steam2.services.MLServiceClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequestMapping("/api/camera")
@RestController
public class CameraPeopleManager {

    private final CameraPeopleDao cameraPeopleDao;
    private final MLServiceClient mlServiceClient;

    @Autowired
    public CameraPeopleManager(CameraPeopleDao cameraPeopleDao, MLServiceClient mlServiceClient) {
        this.cameraPeopleDao = cameraPeopleDao;
        this.mlServiceClient = mlServiceClient;
    }

    @PostMapping("/new")
    private void saveCameraPeopleNumber(@RequestBody CameraPeopleNumber cameraPeopleNumber) {
        cameraPeopleDao.savePeopleNumber(cameraPeopleNumber);
    }

    @PostMapping("/frames/process")
    public CameraPeopleNumber processCameraFrame(@RequestBody CameraFrameDTO frameDTO) {
        Integer count = mlServiceClient.getPeopleCount(frameDTO.getFrameData());

        if (count == null) {
            // Fallback or error handling
            count = 0;
        }

        LocalDateTime trackTime = frameDTO.getTimestamp();
        if (trackTime == null) {
            trackTime = LocalDateTime.now();
        }

        CameraPeopleNumber entity = new CameraPeopleNumber(trackTime, count);
        return cameraPeopleDao.savePeopleNumber(entity);
    }

    @GetMapping("/get")
    private List<CameraPeopleNumber> getCameraPeopleNumber(@RequestParam("number_limit") int limit) {
        return cameraPeopleDao.getLatestCameraPeopleNumber(limit);
    }
}
