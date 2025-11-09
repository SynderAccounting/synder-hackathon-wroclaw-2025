package algo.backend.repository;

import algo.backend.model.entity.Shoes;
import jakarta.transaction.Transactional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Transactional
@Repository
public interface ShoesRepository extends JpaRepository<Shoes, Long> {
}
