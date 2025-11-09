using SolosApi.Application.DTOs;

namespace SolosApi.Application.Interfaces
{
    public interface IChannelService
    {
        Task<IEnumerable<ChannelDto>> GetAllChannelsAsync();
        Task<ChannelDto?> GetChannelByIdAsync(int id);
        Task<ChannelDto> CreateChannelAsync(ChannelDto channelDto);
        Task UpdateChannelAsync(ChannelDto channelDto);
        Task DeleteChannelAsync(int id);
        Task<ChannelDto?> GetChannelByNameAsync(string name);
    }
}
