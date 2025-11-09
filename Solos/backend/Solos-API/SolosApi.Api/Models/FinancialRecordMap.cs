using CsvHelper.Configuration;

namespace SolosApi.Api.Models
{
    public sealed class FinancialRecordMap : ClassMap<FinancialRecord>
    {
        public FinancialRecordMap()
        {
            Map(m => m.OrderDate).Name("Order Date");
            Map(m => m.DepositDate).Name("Deposit Date");
            Map(m => m.PotentialIncome).Name("Potential Income");
            Map(m => m.ActualProfit).Name("Actual Profit");
            Map(m => m.PotentialLoss).Name("Potential Loss");
        }
    }
}
