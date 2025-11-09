using SolosApi.Application.DTOs;
using SolosApi.Application.Interfaces;
using SolosApi.Domain.Entities;
using SolosApi.Domain.Interfaces;

namespace SolosApi.Application.Services
{
    public class ChannelService : IChannelService
    {
        private readonly IChannelRepository _channelRepository;

        public ChannelService(IChannelRepository channelRepository)
        {
            _channelRepository = channelRepository;
        }

        public async Task<ChannelDto> CreateChannelAsync(ChannelDto channelDto)
        {
            var channel = new Channel
            {
                Name = channelDto.Name
            };

            var result = await _channelRepository.AddAsync(channel);
            return new ChannelDto
            {
                Id = result.Id,
                Name = result.Name
            };
        }

        public async Task DeleteChannelAsync(int id)
        {
            var channel = await _channelRepository.GetByIdAsync(id);
            if (channel != null)
            {
                await _channelRepository.DeleteAsync(channel);
            }
        }

        public async Task<IEnumerable<ChannelDto>> GetAllChannelsAsync()
        {
            var channels = await _channelRepository.GetAllAsync();
            return channels.Select(c => new ChannelDto
            {
                Id = c.Id,
                Name = c.Name
            });
        }

        public async Task<ChannelDto?> GetChannelByIdAsync(int id)
        {
            var channel = await _channelRepository.GetByIdAsync(id);
            if (channel == null) return null;

            return new ChannelDto
            {
                Id = channel.Id,
                Name = channel.Name
            };
        }

        public async Task<ChannelDto?> GetChannelByNameAsync(string name)
        {
            var channel = await _channelRepository.GetByNameAsync(name);
            if (channel == null) return null;

            return new ChannelDto
            {
                Id = channel.Id,
                Name = channel.Name
            };
        }

        public async Task UpdateChannelAsync(ChannelDto channelDto)
        {
            var channel = new Channel
            {
                Id = channelDto.Id,
                Name = channelDto.Name
            };

            await _channelRepository.UpdateAsync(channel);
        }
    }
}
