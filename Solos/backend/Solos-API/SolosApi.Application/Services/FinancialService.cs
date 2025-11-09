using SolosApi.Application.DTOs;
using SolosApi.Application.Interfaces;
using SolosApi.Domain.Interfaces;

namespace SolosApi.Application.Services
{
    public class FinancialService : IFinancialService
    {
        private readonly IIncomeRepository _incomeRepository;
        private readonly IExpenseRepository _expenseRepository;

        public FinancialService(IIncomeRepository incomeRepository, IExpenseRepository expenseRepository)
        {
            _incomeRepository = incomeRepository;
            _expenseRepository = expenseRepository;
        }

        public async Task<IEnumerable<FinancialRecordDto>> GetReceivedIncomeAsync(FinancialRequestDto request)
        {
            var incomes = await _incomeRepository.GetByDateRangeAndChannelsAsync(
                request.StartDate,
                request.EndDate,
                request.ChannelIds);

            return incomes
                .Where(i => i.IsReceived)
                .Select(i => new FinancialRecordDto
                {
                    Date = i.Date,
                    Value = i.Value,
                    ChannelId = i.ChannelId,
                    ChannelName = i.Channel.Name
                });
        }

        public async Task<IEnumerable<FinancialRecordDto>> GetExpectedIncomeAsync(FinancialRequestDto request)
        {
            var incomes = await _incomeRepository.GetByDateRangeAndChannelsAsync(
                request.StartDate,
                request.EndDate,
                request.ChannelIds);

            return incomes
                .Where(i => !i.IsReceived)
                .Select(i => new FinancialRecordDto
                {
                    Date = i.Date,
                    Value = i.Value,
                    ChannelId = i.ChannelId,
                    ChannelName = i.Channel.Name
                });
        }

        public async Task<IEnumerable<FinancialRecordDto>> GetExpensesAsync(FinancialRequestDto request)
        {
            var expenses = await _expenseRepository.GetByDateRangeAndChannelsAsync(
                request.StartDate,
                request.EndDate,
                request.ChannelIds);

            return expenses.Select(e => new FinancialRecordDto
            {
                Date = e.Date,
                Value = e.Amount,
                ChannelId = e.ChannelId,
                ChannelName = e.Channel.Name
            });
        }
    }
}
