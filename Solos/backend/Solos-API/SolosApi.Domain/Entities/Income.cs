namespace SolosApi.Domain.Entities
{
    public class Income
    {
        public int Id { get; set; }
        public decimal Value { get; set; }
        public DateTime Date { get; set; }
        public bool IsReceived { get; set; }
        public string? Description { get; set; }
        public int ChannelId { get; set; }
        public Channel Channel { get; set; } = null!;
    }
}
