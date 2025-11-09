using Microsoft.EntityFrameworkCore;
using SolosApi.Domain.Entities;
using SolosApi.Domain.Interfaces;
using SolosApi.Infrastructure.Data;

namespace SolosApi.Infrastructure.Repositories
{
    public class ExpenseRepository : IExpenseRepository
    {
        private readonly ApplicationDbContext _context;

        public ExpenseRepository(ApplicationDbContext context)
        {
            _context = context;
        }

        public async Task<Expense> AddAsync(Expense expense)
        {
            await _context.Expenses.AddAsync(expense);
            await _context.SaveChangesAsync();
            return expense;
        }

        public async Task<IEnumerable<Expense>> GetByDateRangeAndChannelsAsync(DateTime startDate, DateTime endDate, int[] channelIds)
        {
            return await _context.Expenses
                .Include(e => e.Channel)
                .Where(e => e.Date >= startDate &&
                           e.Date <= endDate &&
                           channelIds.Contains(e.ChannelId))
                .OrderBy(e => e.Date)
                .ToListAsync();
        }
    }
}
