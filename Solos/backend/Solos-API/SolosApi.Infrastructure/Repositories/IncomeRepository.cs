using Microsoft.EntityFrameworkCore;
using SolosApi.Domain.Entities;
using SolosApi.Domain.Interfaces;
using SolosApi.Infrastructure.Data;

namespace SolosApi.Infrastructure.Repositories
{
    public class IncomeRepository : IIncomeRepository
    {
        private readonly ApplicationDbContext _context;

        public IncomeRepository(ApplicationDbContext context)
        {
            _context = context;
        }

        public async Task<Income> AddAsync(Income income)
        {
            var dbSet = income.IsReceived ? _context.ReceivedIncomes : _context.ExpectedIncomes;
            await dbSet.AddAsync(income);
            await _context.SaveChangesAsync();
            return income;
        }

        public async Task<IEnumerable<Income>> GetByDateRangeAndChannelsAsync(DateTime startDate, DateTime endDate, int[] channelIds)
        {
            var expectedIncomes = _context.ExpectedIncomes.Include(i => i.Channel);
            var receivedIncomes = _context.ReceivedIncomes.Include(i => i.Channel);

            return await expectedIncomes.Concat(receivedIncomes)
                .Where(i => i.Date >= startDate &&
                           i.Date <= endDate &&
                           channelIds.Contains(i.ChannelId))
                .OrderBy(i => i.Date)
                .ToListAsync();
        }
    }
}
