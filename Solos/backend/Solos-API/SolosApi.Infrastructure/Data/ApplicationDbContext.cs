using Microsoft.EntityFrameworkCore;
using SolosApi.Domain.Entities;

namespace SolosApi.Infrastructure.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        public DbSet<Product> Products { get; set; }
        public DbSet<Income> ExpectedIncomes { get; set; }
        public DbSet<Income> ReceivedIncomes { get; set; }
        public DbSet<Expense> Expenses { get; set; }
        public DbSet<Channel> Channels { get; set; }
    }
}
