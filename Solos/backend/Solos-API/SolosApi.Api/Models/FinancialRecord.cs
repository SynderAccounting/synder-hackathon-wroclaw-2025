namespace SolosApi.Api.Models
{
    public class FinancialRecord
    {
        public string OrderDate { get; set; } = string.Empty;
        public string? DepositDate { get; set; }
        public decimal PotentialIncome { get; set; }
        public decimal ActualProfit { get; set; }
        public decimal PotentialLoss { get; set; }
    }
}
