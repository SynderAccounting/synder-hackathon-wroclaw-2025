package algo.backend.model.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

import java.time.LocalDate;

@Getter
@Setter
@NoArgsConstructor
@Entity
@ToString
public class Orders {
    @Id
    @SequenceGenerator(
            name = "orders_sequence",
            sequenceName = "orders_sequence",
            allocationSize = 1
    )
    @GeneratedValue(
            strategy = GenerationType.SEQUENCE,
            generator = "orders_sequence"
    )
    private Long id;
    @ManyToOne
    @JoinColumn(
            name="shoesId",
            referencedColumnName = "id"
    )
    private Shoes shoes;
    @Enumerated(EnumType.STRING)
    private OrdersStatus status;
    private String description="";
    private LocalDate data;
    private Integer quantity;


    public Orders(Shoes shoes, OrdersStatus status, String description, LocalDate data, Integer quantity) {
        this.shoes = shoes;
        this.status = status;
        this.description = description;
        this.data = data;
        this.quantity = quantity;
    }
}
