package algo.backend.model.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
public class OrdersDTO {
    Long id;
    Long shoesId;
    String shoesType;
    Integer shoesSize;
    Integer shoesPrice;
    Integer shoesProductionPrice;
    String status;
    String description;
    String date;
    Integer quantity;
}
