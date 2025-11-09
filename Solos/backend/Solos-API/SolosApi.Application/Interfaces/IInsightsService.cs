using SolosApi.Application.DTOs;

namespace SolosApi.Application.Interfaces
{
    public interface IInsightsService
    {
        Task<InsightResponseDto> GetFinancialInsightsAsync(DateRangeDto dateRange);
    }
}
