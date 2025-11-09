# SolosApi - Clean Architecture .NET API

This is a simple .NET API project implementing Clean Architecture principles.

## Project Structure

The solution follows Clean Architecture with the following layers:

- **SolosApi.Domain**: Contains enterprise business rules, entities, and interfaces.
- **SolosApi.Application**: Contains application business rules and use cases.
- **SolosApi.Infrastructure**: Contains external concerns and implementations.
- **SolosApi.Api**: Contains the API endpoints and configuration.

## Technologies

- .NET 8
- Entity Framework Core (with InMemory provider for demo)
- Clean Architecture
- RESTful API principles

## Getting Started

1. Clone the repository
2. Navigate to the solution folder
3. Run the following commands:

```bash
dotnet restore
dotnet build
dotnet run --project SolosApi.Api
```

The API will be available at `https://localhost:7xxx` where xxx is the port assigned by your system.

## API Endpoints

The API provides the following endpoints for managing products:

- GET `/api/products` - Get all products
- GET `/api/products/{id}` - Get a specific product
- GET `/api/products/search/{name}` - Search products by name
- POST `/api/products` - Create a new product
- PUT `/api/products/{id}` - Update an existing product
- DELETE `/api/products/{id}` - Delete a product

## Architecture

This project follows Clean Architecture principles:

1. **Domain Layer**: Contains entities and core business logic
2. **Application Layer**: Contains business workflows and interfaces
3. **Infrastructure Layer**: Contains external concerns implementation
4. **API Layer**: Contains controllers and configuration

## Development

To add new features:

1. Add domain entities and interfaces in the Domain layer
2. Implement use cases in the Application layer
3. Add infrastructure implementations
4. Create API endpoints in the API layer
