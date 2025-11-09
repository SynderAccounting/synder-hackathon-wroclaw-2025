package algo.backend.controller;

import algo.backend.config.CustomReturnables;
import java.util.Map;

import algo.backend.service.ShoesService;
import lombok.Getter;
import lombok.RequiredArgsConstructor;
import lombok.Setter;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Getter
@Setter
@RequiredArgsConstructor
@RestController
@RequestMapping("/api/v1")
public class ShoeController {
    private final ShoesService shoesService;

  @GetMapping("/shoes")
  public Map<String, Object> shoes() {
    return CustomReturnables.getOkResponseMap("");
  }

  @GetMapping("/shoes/all")
    public Map<String, Object> getAllShoes() {
    return shoesService.getAllShoes();
    }

}
