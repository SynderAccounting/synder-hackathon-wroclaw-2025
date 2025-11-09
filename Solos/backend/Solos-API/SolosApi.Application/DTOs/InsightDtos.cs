using System.Text.Json.Serialization;

namespace SolosApi.Application.DTOs
{
    public class InsightResponseDto
    {
        [JsonPropertyName("insights")]
        public required List<InsightDto> Insights { get; set; }
    }

    public class InsightDto
    {
        [JsonPropertyName("id")]
        public required string Id { get; set; }

        [JsonPropertyName("category")]
        public required string Category { get; set; }

        [JsonPropertyName("title")]
        public required string Title { get; set; }

        [JsonPropertyName("message")]
        public required string Message { get; set; }

        [JsonPropertyName("severity")]
        public required string Severity { get; set; }

        [JsonPropertyName("metric")]
        public required string Metric { get; set; }

        [JsonPropertyName("value")]
        public decimal Value { get; set; }

        [JsonPropertyName("delta")]
        public decimal? Delta { get; set; }

        [JsonPropertyName("period")]
        public required InsightPeriodDto Period { get; set; }

        [JsonPropertyName("confidence")]
        public decimal Confidence { get; set; }

        [JsonPropertyName("evidence")]
        public required List<string> Evidence { get; set; }

        [JsonPropertyName("actions")]
        public List<string>? Actions { get; set; }
    }

    public class InsightPeriodDto
    {
        [JsonPropertyName("from")]
        public required string From { get; set; }

        [JsonPropertyName("to")]
        public required string To { get; set; }
    }

    public class FinancialDataDto
    {
        [JsonPropertyName("date_range")]
        public required InsightPeriodDto DateRange { get; set; }

        [JsonPropertyName("base_currency")]
        public string BaseCurrency { get; set; } = "EUR";

        [JsonPropertyName("kpis")]
        public required KpisDto Kpis { get; set; }

        [JsonPropertyName("time_series")]
        public required TimeSeriesDto TimeSeries { get; set; }

        [JsonPropertyName("baseline")]
        public required BaselineDto Baseline { get; set; }

        [JsonPropertyName("thresholds")]
        public required ThresholdsDto Thresholds { get; set; }
    }

    public class KpisDto
    {
        [JsonPropertyName("potential_income")]
        public decimal PotentialIncome { get; set; }

        [JsonPropertyName("potential_loss")]
        public decimal PotentialLoss { get; set; }

        [JsonPropertyName("actual_profit")]
        public decimal ActualProfit { get; set; }
    }

    public class TimeSeriesDto
    {
        [JsonPropertyName("daily")]
        public required List<DailyDataDto> Daily { get; set; }

        [JsonPropertyName("fees")]
        public required List<FeeDataDto> Fees { get; set; }

        [JsonPropertyName("refunds")]
        public required List<RefundDataDto> Refunds { get; set; }

        [JsonPropertyName("payouts")]
        public required List<PayoutDataDto> Payouts { get; set; }

        [JsonPropertyName("platform_stats")]
        public required List<PlatformStatsDto> PlatformStats { get; set; }
    }

    public class DailyDataDto
    {
        [JsonPropertyName("date")]
        public required string Date { get; set; }

        [JsonPropertyName("potential_income")]
        public decimal PotentialIncome { get; set; }

        [JsonPropertyName("potential_loss")]
        public decimal PotentialLoss { get; set; }

        [JsonPropertyName("actual_profit")]
        public decimal ActualProfit { get; set; }
    }

    public class FeeDataDto
    {
        [JsonPropertyName("platform")]
        public required string Platform { get; set; }

        [JsonPropertyName("fee_amount")]
        public decimal FeeAmount { get; set; }

        [JsonPropertyName("fee_rate")]
        public decimal FeeRate { get; set; }
    }

    public class RefundDataDto
    {
        [JsonPropertyName("platform")]
        public required string Platform { get; set; }

        [JsonPropertyName("amount")]
        public decimal Amount { get; set; }

        [JsonPropertyName("rate")]
        public decimal Rate { get; set; }

        [JsonPropertyName("sku")]
        public string? Sku { get; set; }
    }

    public class PayoutDataDto
    {
        [JsonPropertyName("platform")]
        public required string Platform { get; set; }

        [JsonPropertyName("eta")]
        public required string Eta { get; set; }

        [JsonPropertyName("amount")]
        public decimal Amount { get; set; }

        [JsonPropertyName("status")]
        public required string Status { get; set; }

        [JsonPropertyName("on_time_prob")]
        public decimal OnTimeProb { get; set; }

        [JsonPropertyName("delay_avg_days")]
        public decimal DelayAvgDays { get; set; }

        [JsonPropertyName("delay_change_days")]
        public decimal DelayChangeDays { get; set; }
    }

    public class PlatformStatsDto
    {
        [JsonPropertyName("platform")]
        public required string Platform { get; set; }

        [JsonPropertyName("income_share")]
        public decimal IncomeShare { get; set; }

        [JsonPropertyName("income_growth_pct")]
        public decimal IncomeGrowthPct { get; set; }

        [JsonPropertyName("reliability_pct")]
        public decimal ReliabilityPct { get; set; }

        [JsonPropertyName("delay_avg_days")]
        public decimal DelayAvgDays { get; set; }

        [JsonPropertyName("delay_change_days")]
        public decimal DelayChangeDays { get; set; }
    }

    public class BaselineDto
    {
        [JsonPropertyName("profit")]
        public decimal Profit { get; set; }

        [JsonPropertyName("income")]
        public decimal Income { get; set; }

        [JsonPropertyName("loss")]
        public decimal Loss { get; set; }

        [JsonPropertyName("fee_rate_by_platform")]
        public required Dictionary<string, decimal> FeeRateByPlatform { get; set; }

        [JsonPropertyName("refund_rate")]
        public decimal RefundRate { get; set; }

        [JsonPropertyName("on_time_pct")]
        public decimal OnTimePct { get; set; }
    }

    public class ThresholdsDto
    {
        [JsonPropertyName("min_balance")]
        public decimal MinBalance { get; set; }

        [JsonPropertyName("low_on_time_pct")]
        public decimal LowOnTimePct { get; set; } = 0.85m;

        [JsonPropertyName("high_refund_rate")]
        public decimal HighRefundRate { get; set; } = 0.03m;

        [JsonPropertyName("fee_rate_jump_pp")]
        public decimal FeeRateJumpPp { get; set; } = 0.3m;
    }

    // OpenAI Communication DTOs
    public class OpenAICompletionRequest
    {
        [JsonPropertyName("model")]
        public string Model { get; set; } = "gpt-3.5-turbo";

        [JsonPropertyName("messages")]
        public required List<Message> Messages { get; set; }

        [JsonPropertyName("temperature")]
        public decimal Temperature { get; set; } = 0.7M;
    }

    public class Message
    {
        [JsonPropertyName("role")]
        public required string Role { get; set; }

        [JsonPropertyName("content")]
        public required string Content { get; set; }
    }

    public class OpenAICompletionResponse
    {
        [JsonPropertyName("choices")]
        public required List<Choice> Choices { get; set; }
    }

    public class Choice
    {
        [JsonPropertyName("message")]
        public required Message Message { get; set; }
    }
}
