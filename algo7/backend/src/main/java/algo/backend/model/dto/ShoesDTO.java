package algo.backend.model.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
public class ShoesDTO {
    private Long id;
    private String type;
    private Integer size;
    private Integer price;
    private Integer productionPrice;
}
