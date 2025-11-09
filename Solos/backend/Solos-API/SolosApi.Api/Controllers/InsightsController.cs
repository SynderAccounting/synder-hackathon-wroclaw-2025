using Microsoft.AspNetCore.Mvc;
using SolosApi.Application.DTOs;
using SolosApi.Application.Interfaces;

namespace SolosApi.Api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class InsightsController : ControllerBase
    {
        private readonly IInsightsService _insightsService;

        public InsightsController(IInsightsService insightsService)
        {
            _insightsService = insightsService;
        }

        [HttpGet("financial")]
        public async Task<ActionResult<InsightResponseDto>> GetFinancialInsights(
            [FromQuery] DateTime startDate,
            [FromQuery] DateTime endDate)
        {
            var dateRange = new DateRangeDto
            {
                StartDate = startDate,
                EndDate = endDate
            };

            var insights = await _insightsService.GetFinancialInsightsAsync(dateRange);
            return Ok(insights);
        }
    }
}
