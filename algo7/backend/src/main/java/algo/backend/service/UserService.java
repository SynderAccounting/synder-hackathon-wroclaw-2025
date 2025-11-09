package algo.backend.service;

import algo.backend.model.dto.UserDTO;
import algo.backend.model.entity.User;
import algo.backend.model.entity.UserRole;
import algo.backend.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.security.oauth2.jwt.Jwt;

import java.sql.Timestamp;
import java.util.Date;

@Service
@RequiredArgsConstructor
public class UserService implements UserDetailsService {
    private final UserRepository userRepository;
    private final BCryptPasswordEncoder bCryptPasswordEncoder;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException("Nie znaleziono użytkownika: " + username));

        return user;
    }

    public UserDTO getAuthorizedUser() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        Object principal = auth.getPrincipal();
        switch (principal) {
            case User foundUser -> {
                return new UserDTO(foundUser.getId(), foundUser.getUsername(), foundUser.getEmail());
            }
            case Jwt jwt -> {
                String username = jwt.getClaimAsString("sub");
                User userEntity = userRepository.findByUsername(username)
                        .orElseThrow(() -> new IllegalStateException("Nie znaleziono użytkownika: " + username));
                return new UserDTO(
                        userEntity.getId(),
                        userEntity.getUsername(),
                        userEntity.getEmail()
                );
            }
            case null, default -> throw new IllegalStateException("Nie udało się pobrać zalogowanego użytkownika.");
        }
    }

    public User registerUser(String username, String password, String email) {
        // Sprawdź czy użytkownik już istnieje
        if (userRepository.findByUsername(username).isPresent()) {
            throw new IllegalArgumentException("Użytkownik o podanej nazwie już istnieje");
        }

        User user = new User(
                username,
                email,
                bCryptPasswordEncoder.encode(password), // Zaszyfruj hasło
                UserRole.ROLE_USER,
                new Timestamp(new Date().getTime())
        );
        user.setEnabled(true); // Ustaw jako aktywny
        user.setLocked(false);

        return userRepository.save(user);
    }
}