using SolosApi.Domain.Entities;

namespace SolosApi.Domain.Interfaces
{
    public interface IChannelRepository : IRepository<Channel>
    {
        Task<Channel?> GetByNameAsync(string name);
    }
}
