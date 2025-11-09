using SolosApi.Application.DTOs;

namespace SolosApi.Application.Interfaces
{
    public interface IFinancialService
    {
        Task<IEnumerable<FinancialRecordDto>> GetReceivedIncomeAsync(FinancialRequestDto request);
        Task<IEnumerable<FinancialRecordDto>> GetExpectedIncomeAsync(FinancialRequestDto request);
        Task<IEnumerable<FinancialRecordDto>> GetExpensesAsync(FinancialRequestDto request);
    }
}
