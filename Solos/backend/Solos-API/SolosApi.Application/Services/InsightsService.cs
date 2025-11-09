using System.Text.Json;
using SolosApi.Application.DTOs;
using SolosApi.Application.Interfaces;

namespace SolosApi.Application.Services
{
    public class InsightsService : IInsightsService
    {
        private readonly IFinancialService _financialService;
        private readonly IOpenAIService _openAIService;

        public InsightsService(IFinancialService financialService, IOpenAIService openAIService)
        {
            _financialService = financialService;
            _openAIService = openAIService;
        }

        public async Task<InsightResponseDto> GetFinancialInsightsAsync(DateRangeDto dateRange)
        {
            // Get all channels for the complete analysis
            var request = new FinancialRequestDto
            {
                StartDate = dateRange.StartDate,
                EndDate = dateRange.EndDate,
                ChannelIds = new[] { 1, 2, 3, 4, 5 } // Including all possible channels
            };

            var receivedIncome = await _financialService.GetReceivedIncomeAsync(request);
            var expectedIncome = await _financialService.GetExpectedIncomeAsync(request);
            var expenses = await _financialService.GetExpensesAsync(request);

            var financialData = new FinancialDataDto
            {
                DateRange = new InsightPeriodDto
                {
                    From = dateRange.StartDate.ToString("yyyy-MM-dd"),
                    To = dateRange.EndDate.ToString("yyyy-MM-dd")
                },
                Kpis = new KpisDto
                {
                    PotentialIncome = receivedIncome.Sum(x => x.Value) + expectedIncome.Sum(x => x.Value),
                    PotentialLoss = expenses.Sum(x => x.Value),
                    ActualProfit = receivedIncome.Sum(x => x.Value) - expenses.Sum(x => x.Value)
                },
                TimeSeries = new TimeSeriesDto
                {
                    Daily = receivedIncome.GroupBy(x => x.Date.Date)
                        .Select(g => new DailyDataDto
                        {
                            Date = g.Key.ToString("yyyy-MM-dd"),
                            PotentialIncome = g.Sum(x => x.Value),
                            PotentialLoss = expenses.Where(e => e.Date.Date == g.Key).Sum(e => e.Value),
                            ActualProfit = g.Sum(x => x.Value) - expenses.Where(e => e.Date.Date == g.Key).Sum(e => e.Value)
                        }).ToList(),
                    Fees = receivedIncome.GroupBy(x => x.ChannelName)
                        .Select(g => new FeeDataDto
                        {
                            Platform = g.Key,
                            FeeAmount = g.Sum(x => x.Value) * 0.1m, // Example fee calculation
                            FeeRate = 0.1m
                        }).ToList(),
                    Refunds = new List<RefundDataDto>(), // Would need refund data
                    Payouts = new List<PayoutDataDto>(), // Would need payout data
                    PlatformStats = receivedIncome.GroupBy(x => x.ChannelName)
                        .Select(g => new PlatformStatsDto
                        {
                            Platform = g.Key,
                            IncomeShare = g.Sum(x => x.Value) / receivedIncome.Sum(x => x.Value),
                            IncomeGrowthPct = 0, // Would need historical data
                            ReliabilityPct = 1,
                            DelayAvgDays = 0,
                            DelayChangeDays = 0
                        }).ToList()
                },
                Baseline = new BaselineDto
                {
                    Profit = receivedIncome.Sum(x => x.Value) - expenses.Sum(x => x.Value),
                    Income = receivedIncome.Sum(x => x.Value),
                    Loss = expenses.Sum(x => x.Value),
                    FeeRateByPlatform = receivedIncome.GroupBy(x => x.ChannelName)
                        .ToDictionary(g => g.Key, _ => 0.1m),
                    RefundRate = 0,
                    OnTimePct = 1
                },
                Thresholds = new ThresholdsDto
                {
                    MinBalance = 1000 // Example minimum balance threshold
                }
            };

            var serializedData = JsonSerializer.Serialize(financialData, new JsonSerializerOptions
            {
                WriteIndented = true
            });

            return await _openAIService.GetInsightsAsync(serializedData);
        }
    }
}
