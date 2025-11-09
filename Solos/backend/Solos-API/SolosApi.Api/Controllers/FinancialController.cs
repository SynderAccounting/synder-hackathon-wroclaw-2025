using Microsoft.AspNetCore.Mvc;
using SolosApi.Application.DTOs;
using SolosApi.Application.Interfaces;

namespace SolosApi.Api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class FinancialController : ControllerBase
    {
        private readonly IFinancialService _financialService;

        public FinancialController(IFinancialService financialService)
        {
            _financialService = financialService;
        }

        [HttpGet("received-income")]
        public async Task<ActionResult<IEnumerable<FinancialRecordDto>>> GetReceivedIncome(
            [FromQuery] DateTime startDate,
            [FromQuery] DateTime endDate,
            [FromQuery] int[] channelIds)
        {
            var request = new FinancialRequestDto
            {
                StartDate = startDate,
                EndDate = endDate,
                ChannelIds = channelIds
            };
            var result = await _financialService.GetReceivedIncomeAsync(request);
            return Ok(result);
        }

        [HttpGet("expected-income")]
        public async Task<ActionResult<IEnumerable<FinancialRecordDto>>> GetExpectedIncome(
            [FromQuery] DateTime startDate,
            [FromQuery] DateTime endDate,
            [FromQuery] int[] channelIds)
        {
            var request = new FinancialRequestDto
            {
                StartDate = startDate,
                EndDate = endDate,
                ChannelIds = channelIds
            };
            var result = await _financialService.GetExpectedIncomeAsync(request);
            return Ok(result);
        }

        [HttpGet("expenses")]
        public async Task<ActionResult<IEnumerable<FinancialRecordDto>>> GetExpenses(
            [FromQuery] DateTime startDate,
            [FromQuery] DateTime endDate,
            [FromQuery] int[] channelIds)
        {
            var request = new FinancialRequestDto
            {
                StartDate = startDate,
                EndDate = endDate,
                ChannelIds = channelIds
            };
            var result = await _financialService.GetExpensesAsync(request);
            return Ok(result);
        }
    }
}
