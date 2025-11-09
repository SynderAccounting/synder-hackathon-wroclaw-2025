using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Configuration;
using SolosApi.Application.DTOs;
using SolosApi.Application.Interfaces;

namespace SolosApi.Application.Services
{
    public class OpenAIService : IOpenAIService
    {
        private readonly HttpClient _httpClient;
        private readonly string _apiKey;
        private const string SYSTEM_PROMPT = @"You are InsightEngine for ""Solos,"" a cash-flow dashboard for small e-commerce sellers.
Your job: from provided data, produce EXACTLY 6 short, high-signal insight cards, each a one-liner with numeric evidence. Be precise, no guesses.

CATEGORIES (use these values only)
- anomalies
- platform_performance
- fees_refunds
- forecast_whatifs
- timing_reliability
- trend_momentum

REQUIREMENTS
- Pick the TOP 6 insights by impact using the scoring rules below.
- Ensure CATEGORY DIVERSITY: at least 1 from each of [anomalies, platform_performance, fees_refunds, forecast_whatifs]; remaining 2 = highest scores (any category).
- Messages: 8–20 words, plain, decision-oriented. Include currency symbol and %/pp where relevant.
- Use absolute value for ""potential_loss"" when surfacing amounts; keep sign in calculations.
- No hallucinated math. All numbers must be derived from DATA.
- If a category has no signal, emit a ""learning"" insight with severity=""info"" and confidence=0.3.

SCORING (higher = more important)
Score = impact_weighted * recency_weight * confidaence
Where:
- impact_weighted (0–5):
  • Cash shortfall risk (expected_net < threshold in period) → 5
  • Large negative anomaly (|z| ≥ 2) on profit/income → 4
  • Payout delay ↑ ≥ 0.5d or on-time < 85% → 4
  • Fee rate ↑ ≥ 0.3pp vs baseline → 3
  • Refund rate ↑ ≥ 1.5σ or > 3% → 3
  • Platform share shift ≥ 5pp or growth ≥ 20% → 2
  • Positive momentum (profit +10% period-over-period) → 1
- recency_weight: insights tied to the selected date range get 1.2, otherwise 1.0
- confidence (0–1): based on sample size, variance, model fit

Return JSON with 6 insights following the exact schema shown in the example.";

        public OpenAIService(IConfiguration configuration, HttpClient httpClient)
        {
            _httpClient = httpClient;
            _apiKey = configuration["OpenAI:ApiKey"] ?? throw new ArgumentNullException("OpenAI:ApiKey configuration is missing");
            _httpClient.BaseAddress = new Uri("https://api.openai.com/v1/");
            _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_apiKey}");
        }

        public async Task<InsightResponseDto> GetInsightsAsync(string financialData)
        {
            var messages = new List<Message>
            {
                new Message
                {
                    Role = "system",
                    Content = SYSTEM_PROMPT
                },
                new Message
                {
                    Role = "user",
                    Content = financialData
                }
            };

            var request = new OpenAICompletionRequest
            {
                Messages = messages,
                Temperature = 0.3M // Lower temperature for more consistent, data-focused responses
            };

            var response = await _httpClient.PostAsync(
                "chat/completions",
                new StringContent(JsonSerializer.Serialize(request), Encoding.UTF8, "application/json")
            );

            if (!response.IsSuccessStatusCode)
            {
                throw new Exception($"OpenAI API call failed with status code: {response.StatusCode}");
            }

            var content = await response.Content.ReadAsStringAsync();
            var completionResponse = JsonSerializer.Deserialize<OpenAICompletionResponse>(content)
                ?? throw new Exception("Failed to deserialize OpenAI response");

            // First deserialize to a dynamic object to handle the OpenAI response format
            var openAIResponse = JsonSerializer.Deserialize<JsonDocument>(completionResponse.Choices[0].Message.Content)
                ?? throw new Exception("Failed to deserialize insights from OpenAI response");

            // Transform OpenAI format to our InsightDto format
            var insights = openAIResponse.RootElement.GetProperty("insights").EnumerateArray()
                .Select((insight, index) => new InsightDto
                {
                    Id = $"insight_{index + 1}",
                    Category = insight.GetProperty("category").GetString() ?? "unknown",
                    Title = insight.GetProperty("message").GetString() ?? string.Empty,
                    Message = insight.GetProperty("message").GetString() ?? string.Empty,
                    Severity = insight.GetProperty("severity").GetString() ?? "info",
                    Metric = insight.GetProperty("category").GetString() ?? "unknown",
                    Value = 0, // Default value since it's not in the OpenAI response
                    Delta = null,
                    Period = new InsightPeriodDto { From = DateTime.Now.ToString("yyyy-MM-dd"), To = DateTime.Now.ToString("yyyy-MM-dd") },
                    Confidence = insight.GetProperty("confidence").GetDecimal(),
                    Evidence = new List<string> { $"Impact: {insight.GetProperty("impact").GetDecimal()}" }
                })
                .ToList();

            return new InsightResponseDto
            {
                Insights = insights
            };
        }
    }
}
