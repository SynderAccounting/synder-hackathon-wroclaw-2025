package algo.backend.config;

import algo.backend.model.entity.*;
import algo.backend.repository.UserRepository;
import algo.backend.repository.ShoesRepository;
import algo.backend.repository.OrderRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

import java.sql.Timestamp;
import java.time.LocalDate;
import java.time.YearMonth;
import java.util.*;
@Configuration
@RequiredArgsConstructor
public class SetupConfig {

    private final UserRepository userRepository;
    private final ShoesRepository shoesRepository;
    private final OrderRepository ordersRepository;
    private final BCryptPasswordEncoder bCryptPasswordEncoder;

    @Bean
    CommandLineRunner initDb() {
        return args -> {

            // 1. Użytkownik testowy
            if (userRepository.findByUsername("andrzej").isEmpty()) {
                User user = new User(
                        "andrzej",
                        "def@gmail.com",
                        bCryptPasswordEncoder.encode("password123"),
                        UserRole.ROLE_USER,
                        new Timestamp(new Date().getTime())
                );
                user.setEnabled(true);
                user.setLocked(false);
                userRepository.save(user);
                System.out.println("✅ Utworzono użytkownika testowego: andrzej / password123");
            }

            // 2. Lista powodów zwrotów
            List<String> returnReasons = List.of(
                "Too small",
                "Too big",
                "Uncomfortable fit",
                "Different color than expected",
                "Mechanical damage after delivery",
                "Wrong pair (two different sizes)",
                "Different model than ordered",
                "Poor build quality",
                "Too stiff sole",
                "Too narrow in the midfoot",
                "Too wide in the midfoot",
                "Missing an item (e.g., shoelaces)",
                "Stitching defects",
                "Stains / dirt",
                "Delayed delivery – purchase no longer relevant",
                "Customer changed their mind",
                "Doesn't match outfit",
                "Too heavy",
                "Unpleasant odor from the material",
                "Complaint – squeaks when walking"
            );

            Random random = new Random();

            // 3. 4 warianty na każdy typ + 4 rozmiary
            int[] sizes = {38, 39};
            List<Shoes> allShoes = new ArrayList<>();

            for (ShoesType type : ShoesType.values()) {
                for (int variant = 1; variant <= 4; variant++) {
                    int baseProduction = 90 + random.nextInt(80); // baza 90-169
                    for (int size : sizes) {
                        int productionPrice = baseProduction + random.nextInt(40);
                        int price = (int) Math.round(productionPrice * 1.2);

                        Shoes shoes = new Shoes(
                                type,
                                size,
                                price,
                                productionPrice
                        );
                        shoesRepository.save(shoes);
                        allShoes.add(shoes);
                    }
                }
            }

            System.out.println("✅ Utworzono buty: " + allShoes.size());

            // 4. Generowanie historii 9.11.2024 - 9.11.2025
            LocalDate start = LocalDate.of(2025, 10, 9);
            LocalDate end = LocalDate.of(2025, 11, 9);

            YearMonth currentYm = YearMonth.of(start.getYear(), start.getMonth());
            YearMonth endYm = YearMonth.of(end.getYear(), end.getMonth());

            while (!currentYm.isAfter(endYm)) {
                LocalDate monthStart = currentYm.atDay(1);
                LocalDate monthEnd = currentYm.atEndOfMonth();

                if (currentYm.equals(YearMonth.of(2025, 10))) {
                    monthStart = start;
                }
                if (currentYm.equals(YearMonth.of(2025, 11))) {
                    monthEnd = end;
                }

                boolean isLastMonth = currentYm.equals(YearMonth.of(2025, 11));

                for (Shoes shoes : allShoes) {

                    // Dla każdego dnia w miesiącu twórz 50 + do 30 zamówień (czyli 50..80) po kolei
                    LocalDate day = monthStart;
                    while (!day.isAfter(monthEnd)) {
                        int totalEntries = 10 + random.nextInt(5); // 50-80

                        // 30–50% to zwroty
                        double returnedRatio = 0.30 + (random.nextDouble() * 0.20);
                        int returnedCount = (int) Math.round(totalEntries * returnedRatio);

                        int inProgressCount = 0;
                        if (isLastMonth) {
                            int remaining = totalEntries - returnedCount;
                            inProgressCount = (int) Math.round(remaining * 0.10); // 10% z niezwroconych
                        }
                        int doneCount = totalEntries - returnedCount - inProgressCount;
                        if (doneCount < 0) doneCount = 0; // bezpieczeństwo

                        // mieszamy kolejność statusów
                        List<OrdersStatus> statuses = new ArrayList<>();
                        for (int i = 0; i < returnedCount; i++) statuses.add(OrdersStatus.RETURNED);
                        for (int i = 0; i < inProgressCount; i++) statuses.add(OrdersStatus.IN_PROGRESS);
                        for (int i = 0; i < doneCount; i++) statuses.add(OrdersStatus.DONE);
                        // Jeśli z jakiegoś powodu lista jest krótsza (np. obcięcie), dopilnuj do totalEntries
                        while (statuses.size() < totalEntries) statuses.add(OrdersStatus.DONE);

                        Collections.shuffle(statuses);

                        for (int i = 0; i < totalEntries; i++) {
                            OrdersStatus status = statuses.get(i);
                            int quantity = 1 + random.nextInt(3);

                            String description = "";
                            if (status == OrdersStatus.RETURNED) {
                                description = returnReasons.get(random.nextInt(returnReasons.size()));
                            }

                            Orders order = new Orders(
                                    shoes,
                                    status,
                                    description,
                                    day, // używamy bezpośrednio dnia
                                    quantity
                            );

                            System.out.println("Tworzę zamówienie: " + order);

                            ordersRepository.save(order);
                        }

                        day = day.plusDays(1);
                    }
                }

                currentYm = currentYm.plusMonths(1);
            }

            System.out.println("✅ Wygenerowano historię zamówień/sprzedaży.");
        };
    }
}
