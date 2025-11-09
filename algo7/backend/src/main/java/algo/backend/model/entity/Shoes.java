package algo.backend.model.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@NoArgsConstructor
@Entity
@ToString
public class Shoes {
    @Id
    @SequenceGenerator(
            name = "shoes_sequence",
            sequenceName = "shoes_sequence",
            allocationSize = 1
    )
    @GeneratedValue(
            strategy = GenerationType.SEQUENCE,
            generator = "shoes_sequence"
    )
    private Long id;
    @Enumerated(EnumType.STRING)
    private ShoesType shoesType;
    private Integer size;
    private Integer price;
    private Integer productionPrice;


    public Shoes(ShoesType shoesType, Integer size, Integer price, Integer productionPrice) {
        this.shoesType = shoesType;
        this.size = size;
        this.price = price;
        this.productionPrice = productionPrice;
    }
}
