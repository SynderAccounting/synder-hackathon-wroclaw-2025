using SolosApi.Domain.Entities;

namespace SolosApi.Domain.Interfaces
{
    public interface IProductRepository : IRepository<Product>
    {
        Task<IEnumerable<Product>> GetProductsByNameAsync(string name);
    }
}
