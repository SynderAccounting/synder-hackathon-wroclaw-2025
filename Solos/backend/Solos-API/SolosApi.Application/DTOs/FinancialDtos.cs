namespace SolosApi.Application.DTOs
{
    public class FinancialRecordDto
    {
        public DateTime Date { get; set; }
        public decimal Value { get; set; }
        public int ChannelId { get; set; }
        public string ChannelName { get; set; } = string.Empty;
    }

    public class DateRangeDto
    {
        public required DateTime StartDate { get; set; }
        public required DateTime EndDate { get; set; }
    }

    public class FinancialRequestDto
    {
        public required DateTime StartDate { get; set; }
        public required DateTime EndDate { get; set; }
        public required int[] ChannelIds { get; set; }
    }
}
