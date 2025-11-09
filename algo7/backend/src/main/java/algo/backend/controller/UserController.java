package algo.backend.controller;

import algo.backend.model.dto.UserDTO;
import algo.backend.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/authorized")
public class UserController {
  private final UserService userService;

  @GetMapping("/user")
  public UserDTO getAuthorizedUser() {
    return userService.getAuthorizedUser();
  }
}
