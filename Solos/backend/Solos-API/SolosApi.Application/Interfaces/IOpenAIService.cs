using SolosApi.Application.DTOs;

namespace SolosApi.Application.Interfaces
{
    public interface IOpenAIService
    {
        Task<InsightResponseDto> GetInsightsAsync(string financialData);
    }
}
