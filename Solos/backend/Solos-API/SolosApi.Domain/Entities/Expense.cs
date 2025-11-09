namespace SolosApi.Domain.Entities
{
    public class Expense
    {
        public int Id { get; set; }
        public decimal Amount { get; set; }
        public DateTime Date { get; set; }
        public string? Description { get; set; }
        public int ChannelId { get; set; }
        public Channel Channel { get; set; } = null!;
    }
}
