package algo.backend.service;

import algo.backend.config.CustomReturnables;
import algo.backend.model.dto.OrdersDTO;
import algo.backend.repository.OrderRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class OrdersService {
    private final OrderRepository orderRepository;
    private final ShoesService shoesService;

    public Map<String, Object> getAllOrders() {
        List<OrdersDTO> ordersList = orderRepository.findAll().stream()
                .map(order -> new OrdersDTO(
                        order.getId(),
                        order.getShoes().getId(),
                        order.getShoes().getShoesType().toString(),
                        order.getShoes().getSize(),
                        order.getShoes().getPrice(),
                        order.getShoes().getProductionPrice(),
                        order.getStatus().toString(),
                        order.getDescription(),
                        order.getData().toString(),
                        order.getQuantity()
                )).toList();

        Map<String, Object> response = CustomReturnables.getOkResponseMap("ORDERS WERE DOWNLOADED SUCCESSFULLY");
        response.put("orders", ordersList);
        return response;
    }
}
