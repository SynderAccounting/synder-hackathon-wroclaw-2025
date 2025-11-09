package algo.backend.controller;

import algo.backend.config.CustomReturnables;
import algo.backend.config.jwt.JwtTokenProvider;
import algo.backend.model.dto.LoginRequest;
import algo.backend.model.dto.LoginResponse;
import algo.backend.model.dto.RegisterRequest;
import algo.backend.model.entity.User;
import algo.backend.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.DisabledException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider jwtTokenProvider;
    private final UserService userService;

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest loginRequest) {
        try {
            // Autentykacja użytkownika
            Authentication authentication = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(
                            loginRequest.getUsername(),
                            loginRequest.getPassword()
                    )
            );

            // Pobierz role użytkownika
            List<String> roles = authentication.getAuthorities().stream()
                    .map(GrantedAuthority::getAuthority)
                    .collect(Collectors.toList());

            // Wygeneruj token JWT
            String token = jwtTokenProvider.createToken(loginRequest.getUsername(), roles);

            // Zwróć odpowiedź z tokenem
            return ResponseEntity.ok(new LoginResponse(
                    token,
                    jwtTokenProvider.getValidityInMs(),
                    loginRequest.getUsername()
            ));

        } catch (DisabledException e) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(CustomReturnables.getErrorResponseMap("Konto jest nieaktywne"));
        } catch (BadCredentialsException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(CustomReturnables.getErrorResponseMap("Nieprawidłowa nazwa użytkownika lub hasło"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(CustomReturnables.getErrorResponseMap("Błąd podczas logowania: " + e.getMessage()));
        }
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody RegisterRequest registerRequest) {
        try {
            User user = userService.registerUser(
                    registerRequest.getUsername(),
                    registerRequest.getPassword(),
                    registerRequest.getEmail()
            );

            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(CustomReturnables.getOkResponseMap(
                            "Użytkownik " + user.getUsername() + " został zarejestrowany pomyślnie"
                    ));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(CustomReturnables.getErrorResponseMap(e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(CustomReturnables.getErrorResponseMap("Błąd podczas rejestracji: " + e.getMessage()));
        }
    }

    @GetMapping("/test")
    public ResponseEntity<Map<String, Object>> test() {
        return ResponseEntity.ok(CustomReturnables.getOkResponseMap("Auth endpoint działa!"));
    }
}