using SolosApi.Domain.Entities;

namespace SolosApi.Domain.Interfaces
{
    public interface IExpenseRepository
    {
        Task<IEnumerable<Expense>> GetByDateRangeAndChannelsAsync(DateTime startDate, DateTime endDate, int[] channelIds);
        Task<Expense> AddAsync(Expense expense);
    }
}
