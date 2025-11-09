package algo.backend.repository;

import jakarta.transaction.Transactional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import algo.backend.model.entity.Orders;

@Transactional
@Repository
public interface OrderRepository extends JpaRepository<Orders, Long> {
}
