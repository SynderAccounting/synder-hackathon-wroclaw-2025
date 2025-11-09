using System.Globalization;
using CsvHelper;
using CsvHelper.Configuration;
using Microsoft.EntityFrameworkCore;
using SolosApi.Domain.Entities;
using SolosApi.Infrastructure.Data;
using SolosApi.DataImport.Models;

namespace SolosApi.DataImport
{
    public class Program
    {

        public static void Main(string[] args)
        {
            var optionsBuilder = new DbContextOptionsBuilder<ApplicationDbContext>();
            optionsBuilder.UseInMemoryDatabase("SolosDb");

            using var context = new ApplicationDbContext(optionsBuilder.Options);

            // Ensure channels exist
            if (!context.Channels.Any())
            {
                context.Channels.AddRange(
                    new Channel { Id = 1, Name = "Amazon Orders" },
                    new Channel { Id = 2, Name = "Shopify Payments" }
                );
                context.SaveChanges();
            }

            Console.WriteLine("Database initialized with channels. Please place your CSV files in the application directory:");
            Console.WriteLine("1. amazon_orders.csv");
            Console.WriteLine("2. shopify_payments_table.csv");
            Console.WriteLine("Press any key when ready...");
            Console.ReadKey();

            if (!File.Exists("amazon_orders_table.csv") || !File.Exists("shopify_payments_table.csv"))
            {
                Console.WriteLine("Error: Required CSV files not found!");
                return;
            }

            var config = new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                HasHeaderRecord = true,
                MissingFieldFound = null
            };

            var amazonRecordsCount = 0;
            var shopifyRecordsCount = 0;

            // Process Amazon Orders
            try
            {
                using var reader = new StreamReader("amazon_orders_table.csv");
                using var csv = new CsvReader(reader, config);
                var records = csv.GetRecords<FinancialRecord>().ToList();
                Console.WriteLine($"Processing {records.Count} records from Amazon Orders...");

                foreach (var record in records)
                {
                    amazonRecordsCount++;
                    var orderDate = DateTime.Parse(record.OrderDate);
                    var depositDate = !string.IsNullOrEmpty(record.DepositDate) ?
                        DateTime.Parse(record.DepositDate) : orderDate;

                    // Expected Income (Potential Income)
                    context.ExpectedIncomes.Add(new Income
                    {
                        Date = depositDate,
                        Value = record.PotentialIncome,
                        ChannelId = 1
                    });

                    // Received Income (Actual Profit)
                    context.ReceivedIncomes.Add(new Income
                    {
                        Date = depositDate,
                        Value = record.ActualProfit,
                        ChannelId = 1
                    });

                    // Expense (Potential Loss)
                    context.Expenses.Add(new Expense
                    {
                        Date = depositDate,
                        Amount = record.PotentialLoss,
                        ChannelId = 1
                    });
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error processing Amazon Orders: {ex.Message}");
                return;
            }

            // Process Shopify Payments
            try
            {
                using var reader = new StreamReader("shopify_payments_table.csv");
                using var csv = new CsvReader(reader, config);
                var records = csv.GetRecords<FinancialRecord>().ToList();
                Console.WriteLine($"Processing {records.Count} records from Shopify Payments...");

                foreach (var record in records)
                {
                    shopifyRecordsCount++;
                    var orderDate = DateTime.Parse(record.OrderDate);
                    var depositDate = !string.IsNullOrEmpty(record.DepositDate) ?
                        DateTime.Parse(record.DepositDate) : orderDate;

                    // Expected Income (Potential Income)
                    context.ExpectedIncomes.Add(new Income
                    {
                        Date = depositDate,
                        Value = record.PotentialIncome,
                        ChannelId = 2
                    });

                    // Received Income (Actual Profit)
                    context.ReceivedIncomes.Add(new Income
                    {
                        Date = depositDate,
                        Value = record.ActualProfit,
                        ChannelId = 2
                    });

                    // Expense (Potential Loss)
                    context.Expenses.Add(new Expense
                    {
                        Date = depositDate,
                        Amount = record.PotentialLoss,
                        ChannelId = 2
                    });
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error processing Shopify Payments: {ex.Message}");
                return;
            }

            context.SaveChanges();
            Console.WriteLine($"Data import completed successfully!");
            Console.WriteLine($"Processed {amazonRecordsCount} Amazon Orders records and {shopifyRecordsCount} Shopify Payments records.");
            Console.WriteLine("Press any key to exit...");
            Console.ReadKey();
        }
    }
}
