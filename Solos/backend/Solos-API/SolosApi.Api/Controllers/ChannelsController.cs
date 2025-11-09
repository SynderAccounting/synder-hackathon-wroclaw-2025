using Microsoft.AspNetCore.Mvc;
using SolosApi.Application.DTOs;
using SolosApi.Application.Interfaces;

namespace SolosApi.Api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ChannelsController : ControllerBase
    {
        private readonly IChannelService _channelService;

        public ChannelsController(IChannelService channelService)
        {
            _channelService = channelService;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<ChannelDto>>> GetAll()
        {
            var channels = await _channelService.GetAllChannelsAsync();
            return Ok(channels);
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<ChannelDto>> GetById(int id)
        {
            var channel = await _channelService.GetChannelByIdAsync(id);
            if (channel == null) return NotFound();
            return Ok(channel);
        }

        [HttpGet("by-name/{name}")]
        public async Task<ActionResult<ChannelDto>> GetByName(string name)
        {
            var channel = await _channelService.GetChannelByNameAsync(name);
            if (channel == null) return NotFound();
            return Ok(channel);
        }

        [HttpPost]
        public async Task<ActionResult<ChannelDto>> Create(ChannelDto channelDto)
        {
            var result = await _channelService.CreateChannelAsync(channelDto);
            return CreatedAtAction(nameof(GetById), new { id = result.Id }, result);
        }

        [HttpPut("{id}")]
        public async Task<IActionResult> Update(int id, ChannelDto channelDto)
        {
            if (id != channelDto.Id)
                return BadRequest();

            await _channelService.UpdateChannelAsync(channelDto);
            return NoContent();
        }

        [HttpDelete("{id}")]
        public async Task<IActionResult> Delete(int id)
        {
            await _channelService.DeleteChannelAsync(id);
            return NoContent();
        }
    }
}
