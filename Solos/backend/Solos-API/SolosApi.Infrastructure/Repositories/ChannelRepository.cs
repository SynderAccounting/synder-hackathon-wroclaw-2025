using Microsoft.EntityFrameworkCore;
using SolosApi.Domain.Entities;
using SolosApi.Domain.Interfaces;
using SolosApi.Infrastructure.Data;

namespace SolosApi.Infrastructure.Repositories
{
    public class ChannelRepository : IChannelRepository
    {
        private readonly ApplicationDbContext _context;

        public ChannelRepository(ApplicationDbContext context)
        {
            _context = context;
        }

        public async Task<Channel> AddAsync(Channel entity)
        {
            await _context.Channels.AddAsync(entity);
            await _context.SaveChangesAsync();
            return entity;
        }

        public async Task DeleteAsync(Channel entity)
        {
            _context.Channels.Remove(entity);
            await _context.SaveChangesAsync();
        }

        public async Task<IEnumerable<Channel>> GetAllAsync()
        {
            return await _context.Channels.ToListAsync();
        }

        public async Task<Channel?> GetByIdAsync(int id)
        {
            return await _context.Channels.FindAsync(id);
        }

        public async Task<Channel?> GetByNameAsync(string name)
        {
            return await _context.Channels
                .FirstOrDefaultAsync(c => c.Name.ToLower() == name.ToLower());
        }

        public async Task UpdateAsync(Channel entity)
        {
            _context.Channels.Update(entity);
            await _context.SaveChangesAsync();
        }
    }
}
