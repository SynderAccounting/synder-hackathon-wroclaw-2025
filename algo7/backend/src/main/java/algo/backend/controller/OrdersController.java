package algo.backend.controller;

import algo.backend.config.CustomReturnables;
import java.util.Map;

import algo.backend.service.OrdersService;
import lombok.Getter;
import lombok.RequiredArgsConstructor;
import lombok.Setter;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Getter
@RequiredArgsConstructor
@Setter
@RestController
@RequestMapping("/api/v1")
public class OrdersController {
    private final OrdersService ordersService;

    @GetMapping("/orders")
  public Map<String, Object> orders() {
    return CustomReturnables.getOkResponseMap("");
  }

  @GetMapping("/orders/all")
    public Map<String,Object> getAllOrders(){
      return ordersService.getAllOrders();
  }


}
