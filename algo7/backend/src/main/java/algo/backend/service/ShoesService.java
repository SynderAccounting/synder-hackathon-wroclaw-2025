package algo.backend.service;

import algo.backend.config.CustomReturnables;
import algo.backend.model.dto.ShoesDTO;
import algo.backend.model.entity.Shoes;
import algo.backend.repository.ShoesRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class ShoesService {
    private final ShoesRepository shoesRepository;

    public Map<String, Object> getAllShoes() {
        List<ShoesDTO> shoesList = shoesRepository.findAll().stream()
                .map(shoes -> new ShoesDTO(
                        shoes.getId(),
                        shoes.getShoesType().toString(),
                        shoes.getSize(),
                        shoes.getPrice(),
                        shoes.getProductionPrice()
                )).toList();

        Map<String, Object> response = CustomReturnables.getOkResponseMap("SHOES WERE DOWNLOADED SUCCESSFULLY");
        response.put("shoes", shoesList);
        return response;
    }
}
