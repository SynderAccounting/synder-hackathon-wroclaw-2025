# Agents.md - Multi-Platform Shopping Hub

This Agents.md file provides comprehensive guidance for AI agents (Claude Sonnet 4.5, OpenAI Codex, and others) working with this multi-platform e-commerce analytics and management system.

---

## Project Overview

**Purpose**: Unified shopping hub that aggregates data from WooCommerce, Square, and Shopify APIs to provide:
- Centralized order and inventory management
- Refund analysis with actionable improvement recommendations
- AI-powered restock prediction (1-month horizon)
- Multi-platform invoice collection and management

**Architecture**: Feature-driven monorepo with Spring Boot backend and React SPA frontend following bulletproof-react principles.

**Key Architectural Principles**:
- Feature-based organization (not file-type based)
- Unidirectional codebase architecture
- Colocation of related files
- Clear public APIs via index files
- Absolute imports with `@/` prefix

---

## Technology Stack

### Backend (Spring Boot 3.x)
```
spring-boot-starter-web
spring-boot-starter-data-jpa
spring-boot-starter-security
spring-boot-starter-validation
spring-boot-devtools
spring-session-jdbc
lombok
postgresql
```

### Frontend (React + Vite)
```
react ^18.x
typescript ^5.x
vite ^5.x
tailwindcss ^3.x
shadcn/ui
lucide-react (icons)
```

### AI Integration
```
Anthropic Claude API (Sonnet 4.5)
- Refund analysis
- Improvement recommendations
- Restock predictions
```

---

## Project Structure

### Root Structure
```
project-root/
├── backend/                          # Spring Boot REST API
│   └── src/main/resources/static/   # Frontend build output (after deployment)
├── frontend/                         # React application (separate development)
├── docs/                             # Documentation
│   ├── API.md
│   ├── SETUP.md
│   └── DEPLOYMENT.md
└── README.md
```

**Development Model:**
- Backend and frontend are **developed independently**
- Backend is **pure REST API** (no view rendering)
- Frontend runs on separate dev server (`npm run dev` on port 3000)
- Backend API runs on port 8080
- Frontend makes API calls to `http://localhost:8080/api/v1/`

**Production Deployment:**
1. Build frontend: `cd frontend && npm run build`
2. Copy `frontend/dist/*` → `backend/src/main/resources/static/`
3. Spring Boot serves frontend as static files
4. All requests to `/api/**` → REST API
5. All other requests → `index.html` (React Router)

### Backend Structure (REST API Only)

**Backend is a pure REST API - no view templates, no server-side rendering:**

```
backend/
├── src/main/java/com/yourcompany/shophub/
│   ├── ShopHubApplication.java       # Main application class
│   │
│   ├── controller/                   # REST API Controllers (@RestController)
│   │   ├── OrderController.java      # /api/v1/orders
│   │   ├── ProductController.java    # /api/v1/products
│   │   ├── RefundController.java     # /api/v1/refunds
│   │   ├── InvoiceController.java    # /api/v1/invoices
│   │   ├── ShopController.java       # /api/v1/shops
│   │   ├── AnalyticsController.java  # /api/v1/analytics
│   │   └── AuthController.java       # /api/v1/auth
│   │
│   ├── service/                      # Business Logic Layer
│   │   ├── OrderService.java
│   │   ├── ProductService.java
│   │   ├── RefundService.java
│   │   ├── RefundAnalysisService.java
│   │   ├── InvoiceService.java
│   │   ├── ShopService.java
│   │   ├── RestockPredictionService.java
│   │   ├── AuthService.java
│   │   │
│   │   ├── platform/                 # External Platform Services
│   │   │   ├── WooCommerceService.java
│   │   │   ├── SquareService.java
│   │   │   └── ShopifyService.java
│   │   │
│   │   └── ai/                       # AI Integration Services
│   │       ├── ClaudeService.java
│   │       └── PromptBuilder.java
│   │
│   ├── repository/                   # Data Access Layer (JPA)
│   │   ├── OrderRepository.java
│   │   ├── ProductRepository.java
│   │   ├── RefundRepository.java
│   │   ├── InvoiceRepository.java
│   │   ├── ShopRepository.java
│   │   ├── UserRepository.java
│   │   └── RestockPredictionRepository.java
│   │
│   ├── model/                        # Domain Models & DTOs
│   │   ├── entity/                   # JPA Entities
│   │   │   ├── Order.java
│   │   │   ├── Product.java
│   │   │   ├── Refund.java
│   │   │   ├── Invoice.java
│   │   │   ├── Shop.java
│   │   │   ├── User.java
│   │   │   └── RestockPrediction.java
│   │   │
│   │   └── dto/                      # Data Transfer Objects (API responses)
│   │       ├── OrderDTO.java
│   │       ├── ProductDTO.java
│   │       ├── RefundDTO.java
│   │       ├── RefundAnalysisDTO.java
│   │       ├── RestockPredictionDTO.java
│   │       ├── InvoiceDTO.java
│   │       ├── ShopDTO.java
│   │       ├── LoginRequest.java
│   │       └── AuthResponse.java
│   │
│   ├── config/                       # Configuration Classes
│   │   ├── SecurityConfig.java       # Spring Security + CORS
│   │   ├── WebConfig.java            # Web MVC configuration
│   │   ├── RestTemplateConfig.java   # RestTemplate beans
│   │   └── JpaConfig.java            # JPA configuration
│   │
│   ├── security/                     # Security Components
│   │   ├── JwtTokenProvider.java
│   │   ├── JwtAuthenticationFilter.java
│   │   ├── CustomUserDetailsService.java
│   │   └── SecurityUtils.java
│   │
│   ├── exception/                    # Exception Handling
│   │   ├── GlobalExceptionHandler.java
│   │   ├── ResourceNotFoundException.java
│   │   ├── BadRequestException.java
│   │   ├── UnauthorizedException.java
│   │   └── PlatformApiException.java
│   │
│   ├── util/                         # Utility Classes
│   │   ├── DateUtils.java
│   │   ├── ValidationUtils.java
│   │   ├── ApiResponseBuilder.java
│   │   └── EncryptionUtils.java
│   │
│   └── enums/                        # Enumerations
│       ├── PlatformType.java         # WOOCOMMERCE, SQUARE, SHOPIFY
│       ├── OrderStatus.java
│       ├── RefundStatus.java
│       └── UserRole.java
│
├── src/main/resources/
│   ├── application.yml               # Main configuration
│   ├── application-dev.yml           # Development profile
│   ├── application-prod.yml          # Production profile
│   │
│   ├── db/migration/                 # Flyway migrations (optional)
│   │   ├── V1__Initial_schema.sql
│   │   └── V2__Add_restock_predictions.sql
│   │
│   └── static/                       # ⭐ Frontend build output goes here
│       ├── index.html                # (copied from frontend/dist/)
│       ├── assets/                   # (copied from frontend/dist/assets/)
│       │   ├── index-[hash].js
│       │   └── index-[hash].css
│       └── favicon.ico
│
├── src/test/java/                    # Test classes
│   └── com/yourcompany/shophub/
│       ├── controller/
│       │   └── OrderControllerTest.java
│       ├── service/
│       │   ├── OrderServiceTest.java
│       │   └── RefundAnalysisServiceTest.java
│       └── repository/
│           └── OrderRepositoryTest.java
│
├── pom.xml                           # Maven dependencies
└── README.md
```

### Important: Static Folder Behavior

**Development (separate servers):**
- Frontend: `http://localhost:3000` (Vite dev server)
- Backend: `http://localhost:8080` (Spring Boot API)
- Frontend calls API via proxy or full URL

**Production (single server):**
- Everything: `http://localhost:8080` (Spring Boot)
- Spring Boot serves:
  - `/api/**` → REST API endpoints
  - `/*` → Static files from `src/main/resources/static/`
  - Unknown routes → `index.html` (for React Router)

### Frontend Structure (Bulletproof React Pattern)

**Frontend follows feature-driven architecture with strict separation of concerns:**

```
frontend/
├── public/                           # Static assets
│   ├── favicon.ico
│   └── images/
│
├── src/
│   ├── app/                          # Application layer
│   │   ├── routes/                   # Route definitions
│   │   │   ├── index.tsx             # Root route component
│   │   │   ├── dashboard.tsx
│   │   │   ├── orders.tsx
│   │   │   ├── refunds.tsx
│   │   │   ├── inventory.tsx
│   │   │   └── invoices.tsx
│   │   ├── provider.tsx              # Global providers wrapper
│   │   └── router.tsx                # Router configuration
│   │
│   ├── components/                   # Shared components (used across features)
│   │   ├── ui/                       # shadcn/ui base components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── table.tsx
│   │   │   ├── select.tsx
│   │   │   └── index.ts              # Public API
│   │   │
│   │   ├── layouts/                  # Layout components
│   │   │   ├── main-layout.tsx
│   │   │   ├── auth-layout.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── common/                   # Common reusable components
│   │   │   ├── loading-spinner.tsx
│   │   │   ├── error-boundary.tsx
│   │   │   ├── page-header.tsx
│   │   │   └── index.ts
│   │   │
│   │   └── charts/                   # Shared chart components
│   │       ├── line-chart.tsx
│   │       ├── bar-chart.tsx
│   │       └── index.ts
│   │
│   ├── features/                     # Feature modules (core of the application)
│   │   │
│   │   ├── auth/                     # Authentication feature
│   │   │   ├── api/
│   │   │   │   ├── login.ts
│   │   │   │   ├── register.ts
│   │   │   │   └── index.ts          # Public API
│   │   │   ├── components/
│   │   │   │   ├── login-form.tsx
│   │   │   │   ├── register-form.tsx
│   │   │   │   └── index.ts
│   │   │   ├── hooks/
│   │   │   │   ├── use-auth.ts
│   │   │   │   └── index.ts
│   │   │   ├── stores/
│   │   │   │   ├── auth-store.ts
│   │   │   │   └── index.ts
│   │   │   ├── types/
│   │   │   │   └── index.ts
│   │   │   └── index.ts              # Feature public API
│   │   │
│   │   ├── orders/                   # Orders feature
│   │   │   ├── api/
│   │   │   │   ├── get-orders.ts
│   │   │   │   ├── get-order.ts
│   │   │   │   ├── sync-orders.ts
│   │   │   │   └── index.ts
│   │   │   ├── components/
│   │   │   │   ├── order-list.tsx
│   │   │   │   ├── order-detail.tsx
│   │   │   │   ├── order-filters.tsx
│   │   │   │   ├── order-table.tsx
│   │   │   │   └── index.ts
│   │   │   ├── hooks/
│   │   │   │   ├── use-orders.ts
│   │   │   │   ├── use-order.ts
│   │   │   │   └── index.ts
│   │   │   ├── types/
│   │   │   │   └── index.ts
│   │   │   └── index.ts
│   │   │
│   │   ├── refunds/                  # Refunds & Analysis feature
│   │   │   ├── api/
│   │   │   │   ├── get-refunds.ts
│   │   │   │   ├── get-analysis.ts
│   │   │   │   ├── create-refund.ts
│   │   │   │   └── index.ts
│   │   │   ├── components/
│   │   │   │   ├── refund-list.tsx
│   │   │   │   ├── refund-analysis.tsx
│   │   │   │   ├── refund-chart.tsx
│   │   │   │   ├── improvement-tips.tsx
│   │   │   │   ├── refund-reason-breakdown.tsx
│   │   │   │   └── index.ts
│   │   │   ├── hooks/
│   │   │   │   ├── use-refunds.ts
│   │   │   │   ├── use-refund-analysis.ts
│   │   │   │   └── index.ts
│   │   │   ├── types/
│   │   │   │   └── index.ts
│   │   │   ├── utils/
│   │   │   │   ├── refund-calculations.ts
│   │   │   │   └── index.ts
│   │   │   └── index.ts
│   │   │
│   │   ├── inventory/                # Inventory & Restock feature
│   │   │   ├── api/
│   │   │   │   ├── get-inventory.ts
│   │   │   │   ├── get-predictions.ts
│   │   │   │   ├── sync-inventory.ts
│   │   │   │   └── index.ts
│   │   │   ├── components/
│   │   │   │   ├── inventory-list.tsx
│   │   │   │   ├── restock-prediction.tsx
│   │   │   │   ├── stock-alerts.tsx
│   │   │   │   ├── inventory-filters.tsx
│   │   │   │   └── index.ts
│   │   │   ├── hooks/
│   │   │   │   ├── use-inventory.ts
│   │   │   │   ├── use-predictions.ts
│   │   │   │   └── index.ts
│   │   │   ├── types/
│   │   │   │   └── index.ts
│   │   │   └── index.ts
│   │   │
│   │   ├── invoices/                 # Invoices feature
│   │   │   ├── api/
│   │   │   │   ├── get-invoices.ts
│   │   │   │   ├── get-invoice.ts
│   │   │   │   ├── download-invoice.ts
│   │   │   │   ├── collect-invoices.ts
│   │   │   │   └── index.ts
│   │   │   ├── components/
│   │   │   │   ├── invoice-list.tsx
│   │   │   │   ├── invoice-detail.tsx
│   │   │   │   ├── invoice-download.tsx
│   │   │   │   └── index.ts
│   │   │   ├── hooks/
│   │   │   │   ├── use-invoices.ts
│   │   │   │   └── index.ts
│   │   │   ├── types/
│   │   │   │   └── index.ts
│   │   │   └── index.ts
│   │   │
│   │   ├── shops/                    # Shop configuration feature
│   │   │   ├── api/
│   │   │   │   ├── get-shops.ts
│   │   │   │   ├── create-shop.ts
│   │   │   │   ├── update-shop.ts
│   │   │   │   ├── delete-shop.ts
│   │   │   │   ├── test-connection.ts
│   │   │   │   └── index.ts
│   │   │   ├── components/
│   │   │   │   ├── shop-list.tsx
│   │   │   │   ├── shop-connection-form.tsx
│   │   │   │   ├── platform-selector.tsx
│   │   │   │   ├── connection-status.tsx
│   │   │   │   └── index.ts
│   │   │   ├── hooks/
│   │   │   │   ├── use-shops.ts
│   │   │   │   └── index.ts
│   │   │   ├── types/
│   │   │   │   └── index.ts
│   │   │   └── index.ts
│   │   │
│   │   └── dashboard/                # Dashboard feature
│   │       ├── api/
│   │       │   ├── get-stats.ts
│   │       │   └── index.ts
│   │       ├── components/
│   │       │   ├── dashboard-stats.tsx
│   │       │   ├── recent-activity.tsx
│   │       │   ├── quick-actions.tsx
│   │       │   └── index.ts
│   │       ├── hooks/
│   │       │   ├── use-dashboard-stats.ts
│   │       │   └── index.ts
│   │       └── index.ts
│   │
│   ├── hooks/                        # Global shared hooks
│   │   ├── use-disclosure.ts
│   │   ├── use-media-query.ts
│   │   └── index.ts
│   │
│   ├── lib/                          # External library configurations
│   │   ├── axios.ts                  # Axios instance with interceptors
│   │   ├── react-query.ts            # React Query configuration
│   │   └── index.ts
│   │
│   ├── stores/                       # Global state stores
│   │   ├── notifications.ts          # Toast notifications store
│   │   └── index.ts
│   │
│   ├── types/                        # Global shared types
│   │   ├── api.ts
│   │   └── index.ts
│   │
│   ├── utils/                        # Global utility functions
│   │   ├── format.ts
│   │   ├── date.ts
│   │   └── index.ts
│   │
│   ├── config/                       # Application configuration
│   │   ├── env.ts                    # Environment variables
│   │   └── index.ts
│   │
│   ├── testing/                      # Test utilities
│   │   ├── test-utils.tsx
│   │   └── mocks/
│   │
│   ├── App.tsx                       # Root App component
│   ├── main.tsx                      # Application entry point
│   └── index.css                     # Global styles
│
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── tsconfig.node.json
├── .eslintrc.cjs
├── .prettierrc
└── package.json
```

### Key Architectural Decisions

**Feature Module Structure:**
Each feature in `src/features/` follows this pattern:
- `api/` - API calls and React Query hooks
- `components/` - Feature-specific components
- `hooks/` - Feature-specific custom hooks
- `stores/` - Feature-specific state (Zustand/Redux)
- `types/` - Feature-specific TypeScript types
- `utils/` - Feature-specific utilities
- `index.ts` - Public API (only exports what other features can use)

**Import Rules (enforced by ESLint):**
```javascript
// ✅ Allowed: Features importing from shared modules
import { Button } from '@/components/ui';
import { useAuth } from '@/hooks';

// ✅ Allowed: Shared modules importing from lib
import { axios } from '@/lib/axios';

// ❌ Forbidden: Features importing from other features directly
import { OrderList } from '@/features/orders/components/order-list';
// Use instead:
import { OrderList } from '@/features/orders';

// ❌ Forbidden: Shared modules importing from features
import { useOrders } from '@/features/orders';
```

---

## Coding Conventions

### Backend (Spring Boot)

#### General Java Conventions
- Use **Java 17+** features
- Follow standard Java naming conventions (PascalCase for classes, camelCase for methods/variables)
- Use `@Slf4j` from Lombok for logging
- Annotate all entity classes with `@Data`, `@Entity`, `@Table`
- Use `@Builder` pattern for DTOs and complex objects

#### Layered Architecture Pattern

**Controller → Service → Repository → Entity**

```
Request → Controller → Service → Repository → Database
                ↓                      ↑
              DTO               Entity
```

#### Controller Layer Patterns
```java
@RestController
@RequestMapping("/api/v1/refunds")
@RequiredArgsConstructor
@Slf4j
public class RefundController {
    
    private final RefundService refundService;
    
    @GetMapping
    public ResponseEntity<List<RefundDTO>> getAllRefunds(
        @RequestParam Long shopId,
        @RequestParam(required = false) String status
    ) {
        log.info("Fetching refunds for shop: {}", shopId);
        List<RefundDTO> refunds = refundService.getRefundsByShop(shopId, status);
        return ResponseEntity.ok(refunds);
    }
    
    @GetMapping("/analysis")
    public ResponseEntity<RefundAnalysisDTO> getRefundAnalysis(
        @RequestParam Long shopId,
        @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
        @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate
    ) {
        log.info("Analyzing refunds for shop: {} from {} to {}", shopId, startDate, endDate);
        RefundAnalysisDTO analysis = refundService.analyzeRefunds(shopId, startDate, endDate);
        return ResponseEntity.ok(analysis);
    }
    
    @PostMapping
    public ResponseEntity<RefundDTO> createRefund(@Valid @RequestBody RefundDTO refundDTO) {
        log.info("Creating new refund for order: {}", refundDTO.getOrderId());
        RefundDTO created = refundService.createRefund(refundDTO);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }
}
```

#### Service Layer Patterns
```java
@Service
@RequiredArgsConstructor
@Slf4j
public class RefundService {
    
    private final RefundRepository refundRepository;
    private final OrderRepository orderRepository;
    private final ClaudeService claudeService;
    
    @Transactional(readOnly = true)
    public List<RefundDTO> getRefundsByShop(Long shopId, String status) {
        List<Refund> refunds;
        if (status != null) {
            refunds = refundRepository.findByShopIdAndStatus(shopId, RefundStatus.valueOf(status));
        } else {
            refunds = refundRepository.findByShopId(shopId);
        }
        return refunds.stream()
            .map(this::convertToDTO)
            .collect(Collectors.toList());
    }
    
    @Transactional
    public RefundDTO createRefund(RefundDTO refundDTO) {
        // Validate order exists
        Order order = orderRepository.findById(refundDTO.getOrderId())
            .orElseThrow(() -> new ResourceNotFoundException("Order not found"));
        
        // Create refund entity
        Refund refund = Refund.builder()
            .order(order)
            .amount(refundDTO.getAmount())
            .reason(refundDTO.getReason())
            .status(RefundStatus.PENDING)
            .createdAt(LocalDateTime.now())
            .build();
        
        Refund saved = refundRepository.save(refund);
        log.info("Refund created with ID: {}", saved.getId());
        
        return convertToDTO(saved);
    }
    
    public RefundAnalysisDTO analyzeRefunds(Long shopId, LocalDate startDate, LocalDate endDate) {
        List<Refund> refunds = refundRepository.findByShopIdAndDateRange(
            shopId, 
            startDate.atStartOfDay(), 
            endDate.atTime(23, 59, 59)
        );
        
        // Use Claude AI for analysis
        String aiAnalysis = claudeService.analyzeRefunds(refunds);
        
        // Build analysis DTO
        return RefundAnalysisDTO.builder()
            .totalRefunds(refunds.size())
            .totalAmount(calculateTotalAmount(refunds))
            .topReasons(calculateTopReasons(refunds))
            .improvements(parseImprovements(aiAnalysis))
            .trends(calculateTrends(refunds))
            .build();
    }
    
    private RefundDTO convertToDTO(Refund refund) {
        return RefundDTO.builder()
            .id(refund.getId())
            .orderId(refund.getOrder().getId())
            .amount(refund.getAmount())
            .reason(refund.getReason())
            .status(refund.getStatus().name())
            .createdAt(refund.getCreatedAt())
            .build();
    }
    
    // Helper methods...
}
```

#### Repository Layer
```java
@Repository
public interface RefundRepository extends JpaRepository<Refund, Long> {
    
    List<Refund> findByShopId(Long shopId);
    
    List<Refund> findByShopIdAndStatus(Long shopId, RefundStatus status);
    
    @Query("SELECT r FROM Refund r WHERE r.order.shop.id = :shopId " +
           "AND r.createdAt BETWEEN :startDate AND :endDate")
    List<Refund> findByShopIdAndDateRange(
        @Param("shopId") Long shopId,
        @Param("startDate") LocalDateTime startDate,
        @Param("endDate") LocalDateTime endDate
    );
    
    @Query("SELECT r.reason, COUNT(r) FROM Refund r " +
           "WHERE r.order.shop.id = :shopId " +
           "GROUP BY r.reason ORDER BY COUNT(r) DESC")
    List<Object[]> findTopReasonsByShop(@Param("shopId") Long shopId);
}
```

#### Entity Patterns
```java
@Entity
@Table(name = "refunds")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Refund {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", nullable = false)
    private Order order;
    
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal amount;
    
    @Column(nullable = false, length = 500)
    private String reason;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private RefundStatus status;
    
    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
```

#### DTO Patterns
```java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RefundDTO {
    
    private Long id;
    
    @NotNull(message = "Order ID is required")
    private Long orderId;
    
    @NotNull(message = "Amount is required")
    @DecimalMin(value = "0.01", message = "Amount must be greater than 0")
    private BigDecimal amount;
    
    @NotBlank(message = "Reason is required")
    @Size(max = 500, message = "Reason must not exceed 500 characters")
    private String reason;
    
    private String status;
    
    private LocalDateTime createdAt;
}
```

#### Configuration Best Practices
- Use `application.yml` for configuration (not .properties)
- Externalize API keys and sensitive data (environment variables)
- Use profiles: `dev`, `test`, `prod`
- Configure CORS for development
- Configure static resource handling for SPA

```yaml
# application.yml
spring:
  application:
    name: shop-hub
    
  datasource:
    url: ${DATABASE_URL}
    username: ${DATABASE_USERNAME}
    password: ${DATABASE_PASSWORD}
    
  jpa:
    hibernate:
      ddl-auto: validate
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect

server:
  port: 8080

anthropic:
  api:
    key: ${ANTHROPIC_API_KEY}
    model: claude-sonnet-4-5-20250929
    
platforms:
  woocommerce:
    base-url: ${WOOCOMMERCE_BASE_URL}
    consumer-key: ${WOOCOMMERCE_CONSUMER_KEY}
    consumer-secret: ${WOOCOMMERCE_CONSUMER_SECRET}
  square:
    base-url: https://connect.squareup.com
    access-token: ${SQUARE_ACCESS_TOKEN}
  shopify:
    base-url: ${SHOPIFY_STORE_URL}
    access-token: ${SHOPIFY_ACCESS_TOKEN}
```

#### WebConfig for SPA Support

**CRITICAL: Configure Spring Boot to serve React SPA correctly**

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    
    /**
     * Configure CORS for development
     * In production, frontend is served from same origin (no CORS needed)
     */
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOrigins("http://localhost:3000") // Vite dev server
            .allowedMethods("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS")
            .allowedHeaders("*")
            .allowCredentials(true);
    }
    
    /**
     * Forward all non-API routes to index.html for React Router
     * This ensures client-side routing works after page refresh
     */
    @Bean
    public WebMvcConfigurer forwardToIndex() {
        return new WebMvcConfigurer() {
            @Override
            public void addViewControllers(ViewControllerRegistry registry) {
                // Don't forward API requests
                // Forward all other requests to index.html
                registry.addViewController("/{spring:\\w+}")
                    .setViewName("forward:/index.html");
                registry.addViewController("/**/{spring:\\w+}")
                    .setViewName("forward:/index.html");
                registry.addViewController("/{spring:\\w+}/**{spring:?!(\\.js|\\.css)$}")
                    .setViewName("forward:/index.html");
            }
        };
    }
    
    /**
     * Configure resource handlers for static files
     */
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/**")
            .addResourceLocations("classpath:/static/")
            .setCachePeriod(3600)
            .resourceChain(true);
    }
}
```

### Frontend (React + TypeScript)

#### Feature Module Pattern

**Each feature should be self-contained with its own API, components, hooks, and types:**

```tsx
// ✅ Good: Feature module structure
features/orders/
  ├── api/
  │   ├── get-orders.ts
  │   └── index.ts              // Export only what other features need
  ├── components/
  │   ├── order-list.tsx        // Private to this feature
  │   └── index.ts              // Export only public components
  ├── hooks/
  │   ├── use-orders.ts
  │   └── index.ts
  ├── types/
  │   └── index.ts
  └── index.ts                  // Feature's public API

// ❌ Bad: Flat component structure
components/
  ├── OrderList.tsx
  ├── OrderDetail.tsx
  ├── RefundList.tsx
  ├── RefundChart.tsx
  └── ... (100+ files)
```

#### Component Structure (Bulletproof Pattern)

```tsx
// features/refunds/components/refund-analysis.tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { AlertCircle } from 'lucide-react';
import { useRefundAnalysis } from '../hooks';
import type { RefundAnalysisProps } from '../types';

/**
 * RefundAnalysis displays AI-powered analysis of refund patterns
 * and provides actionable improvement recommendations.
 */
export const RefundAnalysis = ({ shopId, dateRange }: RefundAnalysisProps) => {
  const { data, isLoading, error } = useRefundAnalysis(shopId, dateRange);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  if (!data) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertCircle className="h-5 w-5" />
          Refund Analysis
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <RefundStats stats={data.stats} />
          <ImprovementTips tips={data.improvements} />
        </div>
      </CardContent>
    </Card>
  );
};
```

#### Feature Public API Pattern

```typescript
// features/orders/index.ts
// This file defines what other features can import from this feature

// Export components that should be available to other features
export { OrderList } from './components/order-list';
export { OrderFilters } from './components/order-filters';

// Export hooks
export { useOrders, useOrder } from './hooks';

// Export types
export type { Order, OrderStatus, OrderFilters } from './types';

// DO NOT export internal implementation details
// ❌ Don't export: order-table-row.tsx, order-utils.ts, etc.
```

#### API Layer Pattern

```typescript
// features/refunds/api/get-analysis.ts
import { useQuery } from '@tanstack/react-query';
import { axios } from '@/lib/axios';
import type { RefundAnalysisData, RefundAnalysisParams } from '../types';

export const getRefundAnalysis = async (
  params: RefundAnalysisParams
): Promise<RefundAnalysisData> => {
  const { data } = await axios.get('/refunds/analysis', { params });
  return data;
};

export const useRefundAnalysis = (params: RefundAnalysisParams) => {
  return useQuery({
    queryKey: ['refund-analysis', params],
    queryFn: () => getRefundAnalysis(params),
    enabled: !!params.shopId && !!params.startDate && !!params.endDate,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// features/refunds/api/index.ts
export { getRefundAnalysis, useRefundAnalysis } from './get-analysis';
export { getRefunds, useRefunds } from './get-refunds';
export { createRefund, useCreateRefund } from './create-refund';
```

#### Type Definitions

```typescript
// features/refunds/types/index.ts
export interface Refund {
  id: string;
  orderId: string;
  platform: 'WOOCOMMERCE' | 'SQUARE' | 'SHOPIFY';
  amount: number;
  reason: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  createdAt: string;
}

export interface RefundAnalysisData {
  totalRefunds: number;
  totalAmount: number;
  topReasons: RefundReason[];
  improvements: string[];
  trends: RefundTrends;
}

export interface RefundReason {
  reason: string;
  count: number;
  percentage: number;
}

export interface RefundTrends {
  weeklyChange: number;
  monthlyChange: number;
}

export interface RefundAnalysisParams {
  shopId: string;
  startDate: string;
  endDate: string;
}

export interface RefundAnalysisProps {
  shopId: string;
  dateRange: { start: Date; end: Date };
}
```

#### Tailwind & Styling Guidelines
- Use Tailwind utility classes exclusively (no custom CSS unless absolutely necessary)
- Follow mobile-first responsive design: `sm:`, `md:`, `lg:`, `xl:` breakpoints
- Use shadcn/ui components for consistent UI
- Use Lucide React icons: `import { IconName } from 'lucide-react'`

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <Card className="hover:shadow-lg transition-shadow">
    {/* Content */}
  </Card>
</div>
```

#### Absolute Imports Configuration

**Always use absolute imports with `@/` prefix instead of relative imports:**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}

// vite.config.ts
import path from 'path';

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

```tsx
// ✅ Good: Absolute imports
import { Button } from '@/components/ui';
import { useAuth } from '@/features/auth';
import { formatDate } from '@/utils/date';

// ❌ Bad: Relative imports
import { Button } from '../../../components/ui';
import { useAuth } from '../../features/auth';
```

#### ESLint Rules for Architecture Enforcement

**Configure ESLint to enforce feature-driven architecture:**

```javascript
// .eslintrc.cjs
module.exports = {
  rules: {
    'import/no-restricted-paths': [
      'error',
      {
        zones: [
          // Prevent features from importing from other features directly
          {
            target: './src/features/*',
            from: './src/features/*',
            except: ['./index.ts'],
            message: 'Features should not directly import from other features. Use the feature\'s public API (index.ts) instead.',
          },
          // Prevent shared modules from importing from features
          {
            target: [
              './src/components',
              './src/hooks',
              './src/lib',
              './src/types',
              './src/utils',
            ],
            from: ['./src/features', './src/app'],
            message: 'Shared modules cannot import from features or app. This creates circular dependencies.',
          },
          // Prevent importing app routes from features
          {
            target: './src/features/*',
            from: './src/app/routes',
            message: 'Features should not import from app routes.',
          },
        ],
      },
    ],
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/explicit-function-return-type': 'off',
    'react/prop-types': 'off',
  },
};
```

---

## AI Integration with Claude

### Claude Service Pattern (Backend)

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class ClaudeService {
    
    @Value("${anthropic.api.key}")
    private String apiKey;
    
    @Value("${anthropic.api.model}")
    private String model;
    
    private final RestTemplate restTemplate;
    
    public String analyzeRefunds(List<Refund> refunds) {
        String prompt = buildRefundAnalysisPrompt(refunds);
        return callClaude(prompt);
    }
    
    public RestockPredictionDTO predictRestock(List<Product> products, List<Order> orders) {
        String prompt = buildRestockPredictionPrompt(products, orders);
        String response = callClaude(prompt);
        return parseRestockResponse(response);
    }
    
    private String callClaude(String prompt) {
        HttpHeaders headers = new HttpHeaders();
        headers.set("x-api-key", apiKey);
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("anthropic-version", "2023-06-01");
        
        Map<String, Object> request = Map.of(
            "model", model,
            "max_tokens", 4096,
            "messages", List.of(
                Map.of("role", "user", "content", prompt)
            )
        );
        
        // Implementation
    }
    
    private String buildRefundAnalysisPrompt(List<Refund> refunds) {
        // Build comprehensive prompt with refund data
        return String.format("""
            Analyze the following refund data and provide:
            1. Top 5 reasons for refunds
            2. Patterns and trends
            3. Actionable improvement recommendations
            
            Refund Data:
            %s
            
            Respond in JSON format.
            """, formatRefundsForPrompt(refunds));
    }
}
```

### Prompt Engineering Guidelines

#### Refund Analysis Prompt Structure
```
Context: E-commerce platform with multiple shop integrations
Task: Analyze refunds and provide actionable insights
Data: [Refund records with reasons, amounts, dates]
Output Format: JSON with { reasons, trends, recommendations }
Constraints: Focus on top 5 issues, provide specific actions
```

#### Restock Prediction Prompt Structure
```
Context: Inventory management across multiple platforms
Task: Predict inventory needs for next 30 days
Data: [Historical sales, current inventory, seasonal trends]
Output Format: JSON with { product_id, current_stock, predicted_need, reorder_quantity }
Constraints: Consider 1.5x safety margin, seasonal patterns
```

---

## REST API Design Patterns

### API Structure

All REST endpoints follow this pattern:
```
http://localhost:8080/api/v1/{resource}
```

### Standard REST Operations

| HTTP Method | Endpoint | Purpose | Request Body | Response |
|------------|----------|---------|--------------|----------|
| GET | `/api/v1/orders` | List all | None | `List<OrderDTO>` |
| GET | `/api/v1/orders/{id}` | Get one | None | `OrderDTO` |
| POST | `/api/v1/orders` | Create | `OrderDTO` | `OrderDTO` |
| PUT | `/api/v1/orders/{id}` | Update | `OrderDTO` | `OrderDTO` |
| PATCH | `/api/v1/orders/{id}` | Partial update | `Map<String, Object>` | `OrderDTO` |
| DELETE | `/api/v1/orders/{id}` | Delete | None | `void` (204) |

### Response Format Standards

**Success Response:**
```json
{
  "id": 1,
  "platformOrderId": "WC-12345",
  "totalAmount": 150.00,
  "status": "COMPLETED",
  "createdAt": "2025-01-15T10:30:00"
}
```

**List Response:**
```json
{
  "data": [
    { "id": 1, "name": "Product 1" },
    { "id": 2, "name": "Product 2" }
  ],
  "total": 2,
  "page": 0,
  "size": 10
}
```

**Error Response:**
```json
{
  "timestamp": "2025-01-15T10:30:00",
  "status": 404,
  "error": "Not Found",
  "message": "Order not found with id: 123",
  "path": "/api/v1/orders/123"
}
```

### Controller Best Practices

**1. Always use @RestController (not @Controller)**
```java
@RestController  // ✅ For REST API
@RequestMapping("/api/v1/orders")
public class OrderController {
    // Returns JSON automatically
}

// NOT:
@Controller  // ❌ For MVC views
```

**2. Use ResponseEntity for flexibility**
```java
@GetMapping("/{id}")
public ResponseEntity<OrderDTO> getOrder(@PathVariable Long id) {
    OrderDTO order = orderService.findById(id);
    return ResponseEntity.ok(order);
}

@PostMapping
public ResponseEntity<OrderDTO> createOrder(@Valid @RequestBody OrderDTO dto) {
    OrderDTO created = orderService.create(dto);
    return ResponseEntity.status(HttpStatus.CREATED).body(created);
}
```

**3. Use proper HTTP status codes**
```java
// 200 OK - Successful GET, PUT, PATCH
return ResponseEntity.ok(data);

// 201 Created - Successful POST
return ResponseEntity.status(HttpStatus.CREATED).body(created);

// 204 No Content - Successful DELETE
return ResponseEntity.noContent().build();

// 400 Bad Request - Validation error
throw new BadRequestException("Invalid data");

// 404 Not Found - Resource not found
throw new ResourceNotFoundException("Order not found");

// 401 Unauthorized - Not authenticated
throw new UnauthorizedException("Please login");

// 403 Forbidden - Not authorized
return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
```

**4. Implement proper validation**
```java
@PostMapping
public ResponseEntity<OrderDTO> createOrder(
    @Valid @RequestBody OrderDTO dto,  // @Valid triggers validation
    BindingResult result
) {
    if (result.hasErrors()) {
        throw new BadRequestException("Validation failed");
    }
    return ResponseEntity.status(HttpStatus.CREATED)
        .body(orderService.create(dto));
}
```

**5. Use query parameters for filtering**
```java
@GetMapping
public ResponseEntity<List<OrderDTO>> getOrders(
    @RequestParam(required = false) Long shopId,
    @RequestParam(required = false) String status,
    @RequestParam(defaultValue = "0") int page,
    @RequestParam(defaultValue = "10") int size
) {
    List<OrderDTO> orders = orderService.findAll(shopId, status, page, size);
    return ResponseEntity.ok(orders);
}
```

### API Endpoint Documentation

#### Orders API
```
GET    /api/v1/orders                  - List all orders
GET    /api/v1/orders/{id}             - Get order by ID
POST   /api/v1/orders                  - Create new order
PUT    /api/v1/orders/{id}             - Update order
DELETE /api/v1/orders/{id}             - Delete order
POST   /api/v1/orders/sync             - Sync orders from platforms
GET    /api/v1/orders/shop/{shopId}    - Get orders by shop
```

#### Refunds API
```
GET    /api/v1/refunds                 - List all refunds
GET    /api/v1/refunds/{id}            - Get refund by ID
POST   /api/v1/refunds                 - Create refund
PATCH  /api/v1/refunds/{id}/status     - Update refund status
GET    /api/v1/refunds/analysis        - Get AI-powered analysis
```

#### Inventory API
```
GET    /api/v1/products                - List inventory
GET    /api/v1/products/{id}           - Get product by ID
PUT    /api/v1/products/{id}           - Update product
POST   /api/v1/products/sync           - Sync from platforms
GET    /api/v1/products/predictions    - Get restock predictions
```

#### Invoices API
```
GET    /api/v1/invoices                - List invoices
GET    /api/v1/invoices/{id}           - Get invoice details
GET    /api/v1/invoices/{id}/download  - Download invoice PDF
POST   /api/v1/invoices/collect        - Collect from selected shops
```

#### Shops API
```
GET    /api/v1/shops                   - List all shops
POST   /api/v1/shops                   - Add shop connection
PUT    /api/v1/shops/{id}              - Update shop
DELETE /api/v1/shops/{id}              - Remove shop
GET    /api/v1/shops/{id}/test         - Test API connection
```

#### Authentication API
```
POST   /api/v1/auth/register           - Register new user
POST   /api/v1/auth/login              - Login (returns JWT)
POST   /api/v1/auth/refresh            - Refresh JWT token
GET    /api/v1/auth/me                 - Get current user
```

---

## API Endpoints Reference

### Order Management
```
GET    /api/v1/orders                  - List all orders
GET    /api/v1/orders/{id}             - Get order details
GET    /api/v1/orders/shop/{shopId}    - Get orders by shop
POST   /api/v1/orders/sync             - Sync orders from platforms
```

### Refund Management
```
GET    /api/v1/refunds                 - List all refunds
GET    /api/v1/refunds/analysis        - Get AI-powered analysis
POST   /api/v1/refunds                 - Create refund
PATCH  /api/v1/refunds/{id}/status     - Update refund status
```

### Inventory Management
```
GET    /api/v1/inventory               - List inventory
GET    /api/v1/inventory/predictions   - Get restock predictions
POST   /api/v1/inventory/sync          - Sync inventory from platforms
PUT    /api/v1/inventory/{id}          - Update inventory
```

### Invoice Management
```
GET    /api/v1/invoices                - List invoices
GET    /api/v1/invoices/{id}           - Get invoice details
GET    /api/v1/invoices/download/{id}  - Download invoice PDF
POST   /api/v1/invoices/collect        - Collect invoices from selected shops
```

### Shop Management
```
GET    /api/v1/shops                   - List all shops
POST   /api/v1/shops                   - Add new shop connection
PUT    /api/v1/shops/{id}              - Update shop settings
DELETE /api/v1/shops/{id}              - Remove shop connection
GET    /api/v1/shops/{id}/test         - Test shop API connection
```

---

## Database Schema Guidelines

### Core Tables

```sql
-- shops
CREATE TABLE shops (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL, -- WOOCOMMERCE, SQUARE, SHOPIFY
    api_url VARCHAR(512),
    api_key_encrypted TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- products
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    shop_id BIGINT REFERENCES shops(id),
    platform_product_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100),
    current_stock INTEGER DEFAULT 0,
    price DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(shop_id, platform_product_id)
);

-- orders
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    shop_id BIGINT REFERENCES shops(id),
    platform_order_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    total_amount DECIMAL(10, 2),
    status VARCHAR(50),
    order_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(shop_id, platform_order_id)
);

-- refunds
CREATE TABLE refunds (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT REFERENCES orders(id),
    amount DECIMAL(10, 2),
    reason TEXT,
    status VARCHAR(50),
    refund_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- restock_predictions
CREATE TABLE restock_predictions (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT REFERENCES products(id),
    predicted_date DATE,
    predicted_quantity INTEGER,
    confidence_score DECIMAL(5, 2),
    analysis_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- invoices
CREATE TABLE invoices (
    id BIGSERIAL PRIMARY KEY,
    shop_id BIGINT REFERENCES shops(id),
    invoice_number VARCHAR(100),
    invoice_date DATE,
    total_amount DECIMAL(10, 2),
    file_path TEXT,
    platform VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Testing Guidelines

### Backend Testing

#### Unit Tests (Service Layer)
```java
@ExtendWith(MockitoExtension.class)
class RefundServiceTest {
    
    @Mock
    private RefundRepository refundRepository;
    
    @Mock
    private OrderRepository orderRepository;
    
    @Mock
    private ClaudeService claudeService;
    
    @InjectMocks
    private RefundService refundService;
    
    @Test
    void shouldGetRefundsByShop() {
        // Given
        Long shopId = 1L;
        List<Refund> mockRefunds = Arrays.asList(
            createMockRefund(1L, "Defective product"),
            createMockRefund(2L, "Wrong item")
        );
        
        when(refundRepository.findByShopId(shopId)).thenReturn(mockRefunds);
        
        // When
        List<RefundDTO> result = refundService.getRefundsByShop(shopId, null);
        
        // Then
        assertNotNull(result);
        assertEquals(2, result.size());
        verify(refundRepository).findByShopId(shopId);
    }
    
    @Test
    void shouldThrowExceptionWhenOrderNotFound() {
        // Given
        RefundDTO refundDTO = RefundDTO.builder()
            .orderId(999L)
            .amount(new BigDecimal("50.00"))
            .reason("Test reason")
            .build();
        
        when(orderRepository.findById(999L)).thenReturn(Optional.empty());
        
        // When & Then
        assertThrows(ResourceNotFoundException.class, () -> {
            refundService.createRefund(refundDTO);
        });
    }
    
    private Refund createMockRefund(Long id, String reason) {
        return Refund.builder()
            .id(id)
            .reason(reason)
            .amount(new BigDecimal("100.00"))
            .status(RefundStatus.PENDING)
            .createdAt(LocalDateTime.now())
            .build();
    }
}
```

#### Integration Tests (Controller Layer)
```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
class RefundControllerIntegrationTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Autowired
    private ObjectMapper objectMapper;
    
    @MockBean
    private RefundService refundService;
    
    @Test
    @WithMockUser(roles = "USER")
    void shouldGetRefundAnalysis() throws Exception {
        // Given
        Long shopId = 1L;
        RefundAnalysisDTO mockAnalysis = RefundAnalysisDTO.builder()
            .totalRefunds(45)
            .totalAmount(new BigDecimal("2500.00"))
            .build();
        
        when(refundService.analyzeRefunds(any(), any(), any()))
            .thenReturn(mockAnalysis);
        
        // When & Then
        mockMvc.perform(get("/api/v1/refunds/analysis")
                .param("shopId", "1")
                .param("startDate", "2025-01-01")
                .param("endDate", "2025-01-31"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.totalRefunds").value(45))
            .andExpect(jsonPath("$.totalAmount").value(2500.00));
    }
    
    @Test
    @WithMockUser(roles = "USER")
    void shouldCreateRefund() throws Exception {
        // Given
        RefundDTO refundDTO = RefundDTO.builder()
            .orderId(1L)
            .amount(new BigDecimal("100.00"))
            .reason("Defective product")
            .build();
        
        RefundDTO savedRefund = RefundDTO.builder()
            .id(1L)
            .orderId(1L)
            .amount(new BigDecimal("100.00"))
            .reason("Defective product")
            .status("PENDING")
            .createdAt(LocalDateTime.now())
            .build();
        
        when(refundService.createRefund(any())).thenReturn(savedRefund);
        
        // When & Then
        mockMvc.perform(post("/api/v1/refunds")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(refundDTO)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").value(1))
            .andExpect(jsonPath("$.status").value("PENDING"));
    }
}
```

#### Repository Tests
```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class RefundRepositoryTest {
    
    @Autowired
    private RefundRepository refundRepository;
    
    @Autowired
    private OrderRepository orderRepository;
    
    @Autowired
    private ShopRepository shopRepository;
    
    @Test
    void shouldFindRefundsByShopId() {
        // Given
        Shop shop = createAndSaveShop();
        Order order = createAndSaveOrder(shop);
        Refund refund1 = createAndSaveRefund(order, "Reason 1");
        Refund refund2 = createAndSaveRefund(order, "Reason 2");
        
        // When
        List<Refund> found = refundRepository.findByShopId(shop.getId());
        
        // Then
        assertEquals(2, found.size());
        assertTrue(found.stream().anyMatch(r -> r.getReason().equals("Reason 1")));
    }
    
    @Test
    void shouldFindRefundsByDateRange() {
        // Given
        Shop shop = createAndSaveShop();
        Order order = createAndSaveOrder(shop);
        Refund refund = createAndSaveRefund(order, "Test reason");
        
        LocalDateTime startDate = LocalDateTime.now().minusDays(1);
        LocalDateTime endDate = LocalDateTime.now().plusDays(1);
        
        // When
        List<Refund> found = refundRepository.findByShopIdAndDateRange(
            shop.getId(), startDate, endDate
        );
        
        // Then
        assertEquals(1, found.size());
        assertEquals("Test reason", found.get(0).getReason());
    }
    
    private Shop createAndSaveShop() {
        return shopRepository.save(Shop.builder()
            .name("Test Shop")
            .platform(PlatformType.WOOCOMMERCE)
            .build());
    }
    
    private Order createAndSaveOrder(Shop shop) {
        return orderRepository.save(Order.builder()
            .shop(shop)
            .platformOrderId("ORD-123")
            .totalAmount(new BigDecimal("200.00"))
            .build());
    }
    
    private Refund createAndSaveRefund(Order order, String reason) {
        return refundRepository.save(Refund.builder()
            .order(order)
            .amount(new BigDecimal("50.00"))
            .reason(reason)
            .status(RefundStatus.PENDING)
            .createdAt(LocalDateTime.now())
            .build());
    }
}
```

### Frontend Testing

#### Test Organization (Following Feature Structure)

```
features/refunds/
  ├── __tests__/
  │   ├── components/
  │   │   ├── refund-analysis.test.tsx
  │   │   └── refund-list.test.tsx
  │   ├── hooks/
  │   │   └── use-refund-analysis.test.ts
  │   └── api/
  │       └── get-analysis.test.ts
  ├── api/
  ├── components/
  └── hooks/
```

#### Component Tests (Vitest + React Testing Library)

```typescript
// features/refunds/__tests__/components/refund-analysis.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@/testing/test-utils';
import { RefundAnalysis } from '../../components/refund-analysis';
import { useRefundAnalysis } from '../../hooks';

vi.mock('../../hooks', () => ({
  useRefundAnalysis: vi.fn(),
}));

describe('RefundAnalysis', () => {
  const mockProps = {
    shopId: '1',
    dateRange: { start: new Date('2025-01-01'), end: new Date('2025-01-31') },
  };

  it('renders loading state', () => {
    vi.mocked(useRefundAnalysis).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as any);

    render(<RefundAnalysis {...mockProps} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('renders refund analysis data', async () => {
    const mockData = {
      totalRefunds: 45,
      totalAmount: 2500,
      topReasons: [
        { reason: 'Defective product', count: 15, percentage: 33.3 },
      ],
      improvements: ['Improve quality control'],
      trends: { weeklyChange: -5, monthlyChange: -10 },
    };

    vi.mocked(useRefundAnalysis).mockReturnValue({
      data: mockData,
      isLoading: false,
      error: null,
    } as any);

    render(<RefundAnalysis {...mockProps} />);

    await waitFor(() => {
      expect(screen.getByText(/Refund Analysis/i)).toBeInTheDocument();
      expect(screen.getByText('45')).toBeInTheDocument();
    });
  });

  it('renders error state', () => {
    vi.mocked(useRefundAnalysis).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Failed to fetch'),
    } as any);

    render(<RefundAnalysis {...mockProps} />);
    expect(screen.getByText(/error/i)).toBeInTheDocument();
  });
});
```

#### Hook Tests

```typescript
// features/refunds/__tests__/hooks/use-refund-analysis.test.ts
import { describe, it, expect } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { createWrapper } from '@/testing/test-utils';
import { useRefundAnalysis } from '../../hooks/use-refund-analysis';

describe('useRefundAnalysis', () => {
  it('fetches refund analysis successfully', async () => {
    const { result } = renderHook(
      () => useRefundAnalysis({
        shopId: '1',
        startDate: '2025-01-01',
        endDate: '2025-01-31',
      }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toBeDefined();
  });

  it('does not fetch when required params are missing', () => {
    const { result } = renderHook(
      () => useRefundAnalysis({
        shopId: '',
        startDate: '2025-01-01',
        endDate: '2025-01-31',
      }),
      { wrapper: createWrapper() }
    );

    expect(result.current.fetchStatus).toBe('idle');
  });
});
```

#### Test Utilities

```typescript
// testing/test-utils.tsx
import { ReactElement } from 'react';
import { render as rtlRender, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

export const createWrapper = () => {
  const testQueryClient = createTestQueryClient();
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={testQueryClient}>
      {children}
    </QueryClientProvider>
  );
};

export const render = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  const Wrapper = createWrapper();
  return rtlRender(ui, { wrapper: Wrapper, ...options });
};

export * from '@testing-library/react';
```

#### Mock Service Worker (MSW) for API Mocking

```typescript
// testing/mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/v1/refunds/analysis', ({ request }) => {
    const url = new URL(request.url);
    const shopId = url.searchParams.get('shopId');

    return HttpResponse.json({
      totalRefunds: 45,
      totalAmount: 2500,
      topReasons: [
        { reason: 'Defective product', count: 15, percentage: 33.3 },
      ],
      improvements: ['Improve quality control'],
      trends: { weeklyChange: -5, monthlyChange: -10 },
    });
  }),

  http.get('/api/v1/orders', () => {
    return HttpResponse.json({
      data: [
        { id: '1', total: 100, status: 'COMPLETED' },
        { id: '2', total: 200, status: 'PENDING' },
      ],
      total: 2,
    });
  }),
];

// testing/mocks/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

#### Vitest Setup

```typescript
// vitest.setup.ts
import { afterAll, afterEach, beforeAll } from 'vitest';
import { server } from './testing/mocks/server';
import '@testing-library/jest-dom/vitest';

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### Running Tests

**Backend:**
```bash
# Run all tests
./mvnw test

# Run specific test class
./mvnw test -Dtest=RefundAnalyticsServiceTest

# Run with coverage
./mvnw test jacoco:report
```

**Frontend:**
```bash
# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage
```

---

## Feature Development Workflow

### Adding a New Feature

**Step 1: Create Feature Structure**

```bash
# Create feature directory structure
mkdir -p src/features/new-feature/{api,components,hooks,types}
touch src/features/new-feature/{api,components,hooks,types}/index.ts
touch src/features/new-feature/index.ts
```

**Step 2: Define Types**

```typescript
// src/features/new-feature/types/index.ts
export interface NewFeatureData {
  id: string;
  name: string;
  // ... other fields
}

export interface NewFeatureParams {
  shopId: string;
  // ... other params
}
```

**Step 3: Implement API Layer**

```typescript
// src/features/new-feature/api/get-data.ts
import { useQuery } from '@tanstack/react-query';
import { axios } from '@/lib/axios';
import type { NewFeatureData, NewFeatureParams } from '../types';

export const getData = async (
  params: NewFeatureParams
): Promise<NewFeatureData[]> => {
  const { data } = await axios.get('/new-feature', { params });
  return data;
};

export const useGetData = (params: NewFeatureParams) => {
  return useQuery({
    queryKey: ['new-feature', params],
    queryFn: () => getData(params),
  });
};

// src/features/new-feature/api/index.ts
export * from './get-data';
```

**Step 4: Build Components**

```typescript
// src/features/new-feature/components/feature-list.tsx
import { useGetData } from '../api';
import type { NewFeatureParams } from '../types';

export const FeatureList = ({ shopId }: { shopId: string }) => {
  const { data, isLoading } = useGetData({ shopId });
  
  // Component implementation
};

// src/features/new-feature/components/index.ts
export { FeatureList } from './feature-list';
```

**Step 5: Create Feature Public API**

```typescript
// src/features/new-feature/index.ts
// Only export what should be available to other features
export { FeatureList } from './components';
export { useGetData } from './api';
export type { NewFeatureData, NewFeatureParams } from './types';
```

**Step 6: Add Route**

```typescript
// src/app/routes/new-feature.tsx
import { FeatureList } from '@/features/new-feature';

export const NewFeatureRoute = () => {
  return (
    <div>
      <h1>New Feature</h1>
      <FeatureList shopId="1" />
    </div>
  );
};

// src/app/router.tsx
import { NewFeatureRoute } from './routes/new-feature';

// Add to router configuration
```

### Feature Communication Guidelines

**When Feature A needs data from Feature B:**

```typescript
// ✅ Good: Use Feature B's public API
import { useOrders } from '@/features/orders';

const MyComponent = () => {
  const { data: orders } = useOrders({ shopId: '1' });
  // Use orders data
};

// ❌ Bad: Import internal implementation
import { OrderService } from '@/features/orders/api/order-service';
```

**When multiple features need shared logic:**

```typescript
// Extract to shared hooks or utils
// src/hooks/use-shop-selection.ts
export const useShopSelection = () => {
  // Shared logic that multiple features can use
};

// Use in features
import { useShopSelection } from '@/hooks';
```

### Refactoring Guidelines

**When a component becomes too large:**

1. Extract smaller components within the same feature
2. Keep extracted components private unless needed elsewhere
3. Only export via index.ts if needed by other features

```typescript
// Before: Large component
// features/orders/components/order-list.tsx (300 lines)

// After: Split into smaller components
// features/orders/components/order-list.tsx (main component)
// features/orders/components/order-list-item.tsx (private)
// features/orders/components/order-list-filters.tsx (private)

// Only OrderList is exported in index.ts
// features/orders/components/index.ts
export { OrderList } from './order-list';
// OrderListItem and OrderListFilters remain private
```

**When shared code emerges:**

1. Move to appropriate shared location:
   - Reusable components → `src/components/`
   - Shared hooks → `src/hooks/`
   - Utility functions → `src/utils/`
   - Type definitions → `src/types/`

2. Update imports to use absolute paths

```typescript
// Before: Duplicated in features
features/orders/utils/format-currency.ts
features/refunds/utils/format-currency.ts

// After: Moved to shared utils
src/utils/format-currency.ts

// Import in features
import { formatCurrency } from '@/utils/format-currency';
```

## Deployment Workflow

### Development Mode (Separate Servers)

**Terminal 1 - Backend:**
```bash
cd backend
./mvnw spring-boot:run
# API available at http://localhost:8080
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
# UI available at http://localhost:3000
# API calls proxied to http://localhost:8080
```

### Production Build & Deployment

**Step 1: Build Frontend**
```bash
cd frontend
npm run build
# Creates frontend/dist/ directory with:
# - index.html
# - assets/index-[hash].js
# - assets/index-[hash].css
# - favicon.ico
```

**Step 2: Copy to Backend Static Folder**
```bash
# Option A: Manual copy (Windows)
xcopy /E /I /Y frontend\dist\* backend\src\main\resources\static\

# Option B: Manual copy (Linux/Mac)
cp -r frontend/dist/* backend/src/main/resources/static/

# Option C: Automated script (recommended)
# Create deploy.sh or deploy.bat
```

**Step 3: Build Backend**
```bash
cd backend
./mvnw clean package -DskipTests
# Creates backend/target/shop-hub-0.0.1-SNAPSHOT.jar
```

**Step 4: Run Production**
```bash
cd backend
java -jar target/shop-hub-0.0.1-SNAPSHOT.jar
# Everything served from http://localhost:8080
# - http://localhost:8080 → React app (index.html)
# - http://localhost:8080/api/** → REST API
```

### Automated Deployment Script

**deploy.sh (Linux/Mac):**
```bash
#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# Step 1: Build Frontend
echo "📦 Building frontend..."
cd frontend
npm run build

# Step 2: Copy to Backend
echo "📂 Copying to backend static folder..."
rm -rf ../backend/src/main/resources/static/*
cp -r dist/* ../backend/src/main/resources/static/

# Step 3: Build Backend
echo "🔨 Building backend..."
cd ../backend
./mvnw clean package -DskipTests

echo "✅ Deployment complete!"
echo "📍 JAR location: backend/target/shop-hub-0.0.1-SNAPSHOT.jar"
echo "🚀 Run with: java -jar target/shop-hub-0.0.1-SNAPSHOT.jar"
```

**deploy.bat (Windows):**
```batch
@echo off
echo 🚀 Starting deployment...

echo 📦 Building frontend...
cd frontend
call npm run build

echo 📂 Copying to backend static folder...
rmdir /s /q ..\backend\src\main\resources\static
xcopy /E /I /Y dist ..\backend\src\main\resources\static

echo 🔨 Building backend...
cd ..\backend
call mvnw clean package -DskipTests

echo ✅ Deployment complete!
echo 📍 JAR location: backend\target\shop-hub-0.0.1-SNAPSHOT.jar
echo 🚀 Run with: java -jar target\shop-hub-0.0.1-SNAPSHOT.jar
```

### Production Application Configuration

```yaml
# backend/src/main/resources/application-prod.yml
spring:
  datasource:
    url: ${DATABASE_URL}
    username: ${DATABASE_USERNAME}
    password: ${DATABASE_PASSWORD}
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false
    
server:
  port: ${PORT:8080}
  compression:
    enabled: true
    mime-types: text/html,text/xml,text/plain,text/css,application/javascript,application/json
  
logging:
  level:
    root: INFO
    com.yourcompany.shophub: INFO
  file:
    name: logs/application.log
```

### Running in Production

```bash
# With environment variables
export DATABASE_URL=jdbc:postgresql://localhost:5432/shophub
export DATABASE_USERNAME=postgres
export DATABASE_PASSWORD=yourpassword
export ANTHROPIC_API_KEY=sk-ant-...

java -jar -Dspring.profiles.active=prod target/shop-hub-0.0.1-SNAPSHOT.jar

# Or with application.properties file
java -jar target/shop-hub-0.0.1-SNAPSHOT.jar \
  --spring.profiles.active=prod \
  --server.port=8080
```

### Docker Deployment (Optional)

If you want to use Docker later:

**Dockerfile:**
```dockerfile
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

COPY target/shop-hub-0.0.1-SNAPSHOT.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

**Build and run:**
```bash
docker build -t shop-hub .
docker run -p 8080:8080 \
  -e DATABASE_URL=... \
  -e ANTHROPIC_API_KEY=... \
  shop-hub
```

---

## Development Workflow

### Starting the Application

**Development Mode (Recommended):**

1. **Start Backend API:**
```bash
cd backend
./mvnw spring-boot:run
# API running at http://localhost:8080
# Swagger UI: http://localhost:8080/swagger-ui.html (if configured)
```

2. **Start Frontend Dev Server:**
```bash
cd frontend
npm install  # First time only
npm run dev
# Frontend running at http://localhost:3000
# Hot reload enabled
```

3. **Access Application:**
- Frontend UI: `http://localhost:3000`
- Backend API: `http://localhost:8080/api/v1`
- API calls from frontend automatically proxied to backend

### Environment Variables Setup

**Backend (`backend/.env` or environment variables):**
```bash
DATABASE_URL=jdbc:postgresql://localhost:5432/shophub
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=yourpassword

ANTHROPIC_API_KEY=sk-ant-...

WOOCOMMERCE_BASE_URL=https://yourstore.com
WOOCOMMERCE_CONSUMER_KEY=ck_...
WOOCOMMERCE_CONSUMER_SECRET=cs_...

SQUARE_ACCESS_TOKEN=sq0atp-...

SHOPIFY_STORE_URL=yourstore.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_...
```

**Frontend (`frontend/.env`):**
```bash
# Vite requires VITE_ prefix
VITE_API_BASE_URL=/api/v1
# In development, this is proxied to http://localhost:8080/api/v1
```

### Git Workflow

```bash
# Feature branch
git checkout -b feature/refund-analysis

# Commit conventions
git commit -m "feat(refunds): add AI analysis endpoint"
git commit -m "fix(orders): resolve date filter issue"
git commit -m "docs: update API documentation"

# Push and create PR
git push origin feature/refund-analysis
```

### .gitignore Configuration

**Backend (.gitignore):**
```
target/
!.mvn/wrapper/maven-wrapper.jar
*.class
*.log
*.jar
*.war
*.ear

# Static folder (frontend build)
src/main/resources/static/*

# Environment
.env
application-local.yml
```

**Frontend (.gitignore):**
```
node_modules/
dist/
.env
.env.local
.env.production

# Editor
.vscode/
.idea/
*.swp
*.swo
```

---

## Error Handling Standards

### Backend Exception Handling

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(PlatformApiException.class)
    public ResponseEntity<ErrorResponse> handlePlatformApiException(
        PlatformApiException ex
    ) {
        ErrorResponse error = ErrorResponse.builder()
            .status(HttpStatus.BAD_GATEWAY.value())
            .message("Platform API error: " + ex.getMessage())
            .timestamp(LocalDateTime.now())
            .build();
        return ResponseEntity.status(HttpStatus.BAD_GATEWAY).body(error);
    }
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleResourceNotFound(
        ResourceNotFoundException ex
    ) {
        ErrorResponse error = ErrorResponse.builder()
            .status(HttpStatus.NOT_FOUND.value())
            .message(ex.getMessage())
            .timestamp(LocalDateTime.now())
            .build();
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
}
```

### Frontend Error Handling

```typescript
// utils/errorHandler.ts
export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.message || 'An error occurred';
  }
  return 'An unexpected error occurred';
};

// In components
try {
  await refundService.getAnalysis(shopId, startDate, endDate);
} catch (error) {
  toast.error(handleApiError(error));
}
```

---

## Security Best Practices

### Backend Security
- Use `@PreAuthorize` for method-level security
- Encrypt sensitive data in database (API keys)
- Implement rate limiting for API endpoints
- Use HTTPS only in production
- Validate all user inputs

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf().disable() // Use token-based auth
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/v1/public/**").permitAll()
                .requestMatchers("/api/v1/**").authenticated()
            )
            .sessionManagement()
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS);
        
        return http.build();
    }
}
```

### Frontend Security
- Store tokens in HttpOnly cookies (not localStorage)
- Sanitize user inputs
- Implement CSRF protection
- Use environment variables for sensitive config

---

## Performance Optimization

### Backend
- Use pagination for large datasets
- Implement caching with Redis (optional)
- Use database indexes on frequently queried fields
- Batch API requests to external platforms

```java
@Cacheable(value = "refundAnalysis", key = "#shopId + '-' + #startDate + '-' + #endDate")
public RefundAnalysisDTO analyzeRefunds(Long shopId, LocalDate startDate, LocalDate endDate) {
    // Expensive operation
}
```

### Frontend
- Use React Query for data caching and refetching
- Implement virtual scrolling for large lists
- Lazy load components with React.lazy()
- Optimize images and assets

```typescript
// React Query caching
const { data, isLoading } = useQuery({
  queryKey: ['refunds', shopId],
  queryFn: () => refundService.getRefunds(shopId),
  staleTime: 5 * 60 * 1000, // 5 minutes
  cacheTime: 10 * 60 * 1000, // 10 minutes
});
```

---

## Platform Integration Guidelines

### WooCommerce API
```java
// Base URL: {store_url}/wp-json/wc/v3/
// Authentication: Basic Auth with Consumer Key/Secret
GET /products
GET /orders
GET /refunds
```

### Square API
```java
// Base URL: https://connect.squareup.com/v2/
// Authentication: Bearer token
GET /catalog/list
GET /orders/search
GET /refunds
```

### Shopify API
```java
// Base URL: {store_url}/admin/api/2024-01/
// Authentication: X-Shopify-Access-Token header
GET /products.json
GET /orders.json
GET /refunds.json
```

---

## Deployment Checklist

### Backend
- [ ] Update application-prod.yml with production values
- [ ] Set all environment variables
- [ ] Run database migrations
- [ ] Build JAR: `./mvnw clean package -DskipTests`
- [ ] Configure logging to file
- [ ] Set up health check endpoint

### Frontend
- [ ] Update VITE_API_BASE_URL for production
- [ ] Build production bundle: `npm run build`
- [ ] Optimize bundle size
- [ ] Configure CDN for static assets
- [ ] Set up error tracking (Sentry, etc.)

---

## Common Commands

### Backend
```bash
# Clean and build
./mvnw clean install

# Run with specific profile
./mvnw spring-boot:run -Dspring-boot.run.profiles=dev

# Generate Javadoc
./mvnw javadoc:javadoc

# Run specific test
./mvnw test -Dtest=ClassName#methodName
```

### Frontend
```bash
# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Format code
npm run format
```

---

## AI Agent Guidelines

When working with this codebase, AI agents should:

### Architecture & Structure
1. **Backend is REST API only** - No view templates, no server-side rendering, pure JSON API
2. **Frontend is separate SPA** - React app built independently, then copied to static folder
3. **Follow feature-driven architecture** (frontend) - Code organized by feature, not file type
4. **Follow layered architecture** (backend) - Controller → Service → Repository pattern
5. **Use absolute imports** - Always use `@/` prefix instead of relative paths (`../../../`)

### Development Process
6. **Develop separately** - Backend and frontend run on different ports during development
7. **Use proxy in development** - Vite proxies API calls to Spring Boot
8. **Build for production** - Run `npm run build` and copy dist/ to static/
9. **Test independently** - Backend and frontend have separate test suites

### Backend (Spring Boot REST API)
10. **Always use @RestController** - Never use @Controller for API endpoints
11. **Return JSON only** - All responses should be JSON, use ResponseEntity
12. **Use proper HTTP status codes** - 200, 201, 204, 400, 404, etc.
13. **Implement CORS** - Configure CORS in WebConfig for development
14. **Configure SPA routing** - Forward non-API routes to index.html
15. **Use Lombok annotations** - Reduce boilerplate with `@Data`, `@Builder`, `@Slf4j`
16. **Keep controllers thin** - Business logic belongs in services

### Frontend (React + TypeScript)
17. **No `any` types** - Always use proper TypeScript types
18. **Use shadcn/ui components** - Don't create custom UI components when shadcn/ui equivalents exist
19. **React Query for data fetching** - All API calls should use React Query hooks
20. **Proper loading/error states** - Every data-fetching component must handle loading and error states
21. **Respect feature boundaries** - Never import directly from another feature's internals

### API Design
22. **RESTful endpoints** - Use proper REST conventions (GET, POST, PUT, DELETE)
23. **Consistent URL structure** - All endpoints under `/api/v1/{resource}`
24. **Use DTOs** - Never expose entities directly through REST endpoints
25. **Validate input** - Use `@Valid` and Bean Validation annotations
26. **Handle errors globally** - Use @RestControllerAdvice for exception handling

### Testing
27. **Write tests for all layers** - Controller, service, and repository tests
28. **Mock external dependencies** - Use @MockBean for service tests
29. **Test features in isolation** - Use MSW to mock external dependencies (frontend)
30. **Follow test structure** - Keep tests organized by layer/feature

### Deployment
31. **Build frontend first** - Always run `npm run build` before deploying
32. **Copy to static folder** - `frontend/dist/*` → `backend/src/main/resources/static/`
33. **Single JAR deployment** - Everything packaged in one executable JAR
34. **Environment variables** - Use env vars for configuration, never hardcode

### Specific to This Project
35. **Platform integration isolation** - Keep WooCommerce/Square/Shopify logic separate in service layer
36. **Claude AI prompt engineering** - Structure prompts with context, task, data, and output format
37. **Multi-shop support** - Always filter data by shopId parameter
38. **Handle async operations** - Use proper error handling for external API calls

### Common Anti-Patterns to Avoid

**❌ Don't do this:**
```java
// Using @Controller for REST API
@Controller  // Wrong! This is for MVC views
public class OrderController {
    @GetMapping("/api/orders")
    public String getOrders() {
        return "orders"; // Returns view name, not JSON
    }
}

// Exposing entities directly
@GetMapping("/{id}")
public Order getOrder(@PathVariable Long id) {
    return orderRepository.findById(id).get(); // Exposes JPA entity
}

// Hardcoded configuration
@Service
public class WooCommerceService {
    private static final String API_URL = "https://mystore.com"; // Wrong!
}
```

**✅ Do this instead:**
```java
// Using @RestController for REST API
@RestController  // Correct! Returns JSON
@RequestMapping("/api/v1/orders")
public class OrderController {
    
    @GetMapping
    public ResponseEntity<List<OrderDTO>> getOrders() {
        return ResponseEntity.ok(orderService.getAllOrders());
    }
}

// Using DTOs
@GetMapping("/{id}")
public ResponseEntity<OrderDTO> getOrder(@PathVariable Long id) {
    OrderDTO dto = orderService.findById(id);
    return ResponseEntity.ok(dto);
}

// Configuration from properties
@Service
@RequiredArgsConstructor
public class WooCommerceService {
    
    @Value("${platforms.woocommerce.base-url}")
    private String apiUrl;
}
```

### REST API Checklist

When creating a new REST endpoint:
- [ ] Use @RestController annotation
- [ ] Map to `/api/v1/{resource}` path
- [ ] Use ResponseEntity for responses
- [ ] Return proper HTTP status codes
- [ ] Use DTOs (not entities)
- [ ] Add @Valid for input validation
- [ ] Handle exceptions with @RestControllerAdvice
- [ ] Document with Swagger/OpenAPI (optional)
- [ ] Write controller tests
- [ ] Test with Postman/curl

### Frontend-Backend Integration Checklist

When adding a new feature:
- [ ] Create backend REST endpoint
- [ ] Test endpoint with Postman
- [ ] Create frontend API service
- [ ] Create React Query hook
- [ ] Create feature components
- [ ] Test with dev servers (separate)
- [ ] Build frontend (`npm run build`)
- [ ] Copy to static folder
- [ ] Test with single server
- [ ] Verify React Router works after refresh

---

## Essential Configuration Files

### Frontend Configuration

#### TypeScript Configuration
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

#### Vite Configuration
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    // Proxy API requests to Spring Boot during development
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  // Production build configuration
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    // Generate source maps for production debugging
    sourcemap: false,
    // Optimize chunks
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['lucide-react'],
        },
      },
    },
  },
});
```

**How the proxy works in development:**
- Frontend runs on `http://localhost:3000`
- API calls to `/api/v1/orders` are proxied to `http://localhost:8080/api/v1/orders`
- No CORS issues during development

#### Tailwind Configuration
```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{ts,tsx,js,jsx}'],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};
```

#### ESLint Configuration
```javascript
// .eslintrc.cjs
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
    'plugin:react/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh', 'import'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    'react/react-in-jsx-scope': 'off',
    '@typescript-eslint/no-explicit-any': 'error',
    'import/no-restricted-paths': [
      'error',
      {
        zones: [
          {
            target: './src/features/*',
            from: './src/features/*',
            except: ['./index.ts'],
            message: 'Use feature public API (index.ts) for cross-feature imports.',
          },
          {
            target: [
              './src/components',
              './src/hooks',
              './src/lib',
              './src/types',
              './src/utils',
            ],
            from: ['./src/features', './src/app'],
            message: 'Shared modules cannot import from features.',
          },
        ],
      },
    ],
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
};
```

#### Prettier Configuration
```json
// .prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "arrowParens": "avoid"
}
```

#### Package.json Scripts
```json
// package.json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint . --ext ts,tsx --fix",
    "format": "prettier --write \"src/**/*.{ts,tsx,json,css}\"",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "type-check": "tsc --noEmit"
  }
}
```

### Backend Configuration

#### Application YAML
```yaml
# src/main/resources/application.yml
spring:
  application:
    name: shop-hub
  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}
  datasource:
    url: ${DATABASE_URL:jdbc:postgresql://localhost:5432/shophub}
    username: ${DATABASE_USERNAME:postgres}
    password: ${DATABASE_PASSWORD:postgres}
    driver-class-name: org.postgresql.Driver
  jpa:
    hibernate:
      ddl-auto: validate
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        format_sql: true
    show-sql: false
  session:
    store-type: jdbc
    jdbc:
      initialize-schema: always

server:
  port: 8080
  error:
    include-message: always
    include-binding-errors: always

logging:
  level:
    root: INFO
    com.yourcompany.shophub: DEBUG
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} - %msg%n"

# API Configuration
anthropic:
  api:
    key: ${ANTHROPIC_API_KEY}
    model: claude-sonnet-4-5-20250929
    base-url: https://api.anthropic.com/v1

# Platform Integrations
platforms:
  woocommerce:
    base-url: ${WOOCOMMERCE_BASE_URL}
    consumer-key: ${WOOCOMMERCE_CONSUMER_KEY}
    consumer-secret: ${WOOCOMMERCE_CONSUMER_SECRET}
    timeout: 30000
  square:
    base-url: https://connect.squareup.com/v2
    access-token: ${SQUARE_ACCESS_TOKEN}
    timeout: 30000
  shopify:
    base-url: ${SHOPIFY_STORE_URL}
    access-token: ${SHOPIFY_ACCESS_TOKEN}
    api-version: 2024-01
    timeout: 30000
```

#### Development Profile
```yaml
# src/main/resources/application-dev.yml
spring:
  jpa:
    show-sql: true
    properties:
      hibernate:
        format_sql: true
  devtools:
    restart:
      enabled: true

logging:
  level:
    com.yourcompany.shophub: DEBUG
    org.hibernate.SQL: DEBUG
    org.hibernate.type.descriptor.sql.BasicBinder: TRACE
```

#### Production Profile
```yaml
# src/main/resources/application-prod.yml
spring:
  jpa:
    show-sql: false
  devtools:
    restart:
      enabled: false

logging:
  level:
    com.yourcompany.shophub: INFO
  file:
    name: /var/log/shophub/application.log
    max-size: 10MB
    max-history: 30
```

---

## Additional Resources

### Architecture & Patterns
- [Bulletproof React](https://github.com/alan2207/bulletproof-react) - Main architectural inspiration
- [Feature-Sliced Design](https://feature-sliced.design/) - Alternative feature-driven methodology
- [Screaming Architecture](https://blog.cleancoder.com/uncle-bob/2011/09/30/Screaming-Architecture.html) - Uncle Bob's architecture philosophy

### Frontend
- [React Documentation](https://react.dev)
- [Tailwind CSS Documentation](https://tailwindcss.com)
- [shadcn/ui Components](https://ui.shadcn.com)
- [TanStack Query (React Query)](https://tanstack.com/query/latest)
- [Zustand State Management](https://zustand-demo.pmnd.rs/)
- [Vitest Testing Framework](https://vitest.dev/)

### Backend
- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [Spring Data JPA](https://spring.io/projects/spring-data-jpa)
- [Spring Security](https://spring.io/projects/spring-security)
- [Lombok](https://projectlombok.org/)

### AI Integration
- [Anthropic Claude API](https://docs.anthropic.com)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

### Platform APIs
- [WooCommerce REST API](https://woocommerce.github.io/woocommerce-rest-api-docs/)
- [Square API Documentation](https://developer.squareup.com/docs)
- [Shopify API Documentation](https://shopify.dev/docs/api)

### Development Tools
- [Vite](https://vitejs.dev/)
- [ESLint](https://eslint.org/)
- [Prettier](https://prettier.io/)

---

*Last Updated: 2025-11-08*
*Version: 2.0.0*
*Architecture: Bulletproof React + Domain-Driven Design*
