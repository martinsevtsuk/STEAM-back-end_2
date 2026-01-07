package com.example.steam2.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
public class CameraFrameDTO {
    private String frameData; // Base64 encoded JPEG
    private LocalDateTime timestamp;
}
