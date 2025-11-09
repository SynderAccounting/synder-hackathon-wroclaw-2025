using SolosApi.Domain.Entities;

namespace SolosApi.Domain.Interfaces
{
    public interface IIncomeRepository
    {
        Task<IEnumerable<Income>> GetByDateRangeAndChannelsAsync(DateTime startDate, DateTime endDate, int[] channelIds);
        Task<Income> AddAsync(Income income);
    }
}
