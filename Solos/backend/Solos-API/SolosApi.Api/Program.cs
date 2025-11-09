using Microsoft.EntityFrameworkCore;
using SolosApi.Application.Interfaces;
using SolosApi.Application.Services;
using SolosApi.Domain.Entities;
using SolosApi.Domain.Interfaces;
using SolosApi.Infrastructure.Data;
using SolosApi.Infrastructure.Repositories;
using CsvHelper;
using CsvHelper.Configuration;
using System.Globalization;
using SolosApi.Api.Models;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();

// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Add DbContext
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseInMemoryDatabase("SolosApiDb")); // Using InMemoryDatabase for simplicity

// Register services
builder.Services.AddScoped<IProductRepository, ProductRepository>();
builder.Services.AddScoped<IProductService, ProductService>();
builder.Services.AddScoped<IIncomeRepository, IncomeRepository>();
builder.Services.AddScoped<IExpenseRepository, ExpenseRepository>();
builder.Services.AddScoped<IFinancialService, FinancialService>();
builder.Services.AddScoped<IChannelRepository, ChannelRepository>();
builder.Services.AddScoped<IChannelService, ChannelService>();
builder.Services.AddScoped<IInsightsService, InsightsService>();
builder.Services.AddHttpClient();
builder.Services.AddScoped<IOpenAIService, OpenAIService>();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();

using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();

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


            if (!File.Exists("amazon_orders_table.csv") || !File.Exists("shopify_payments_table.csv"))
            {
                Console.WriteLine("Error: Required CSV files not found!");
                return;
            }

            var config = new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                HasHeaderRecord = true,
                MissingFieldFound = null,
                HeaderValidated = null // Ignore header validation
            };

            var amazonRecordsCount = 0;
            var shopifyRecordsCount = 0;

            // Process Amazon Orders
            try
            {
                using var reader = new StreamReader("amazon_orders_table.csv");
                using var csv = new CsvReader(reader, config);
                csv.Context.RegisterClassMap<FinancialRecordMap>();
                var records = csv.GetRecords<FinancialRecord>().ToList();
                Console.WriteLine($"Processing {records.Count} records from Amazon Orders...");

                foreach (var record in records)
                {
                    amazonRecordsCount++;
                    var orderDate = DateTime.Parse(record.OrderDate.Replace(" UTC", ""));
                    var depositDate = !string.IsNullOrEmpty(record.DepositDate) ?
                        DateTime.Parse(record.DepositDate.Replace(" UTC", "")) : orderDate;

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
                csv.Context.RegisterClassMap<FinancialRecordMap>();
                var records = csv.GetRecords<FinancialRecord>().ToList();
                Console.WriteLine($"Processing {records.Count} records from Shopify Payments...");

                foreach (var record in records)
                {
                    shopifyRecordsCount++;
                    var orderDate = DateTime.Parse(record.OrderDate.Replace(" UTC", ""));
                    var depositDate = !string.IsNullOrEmpty(record.DepositDate) ?
                        DateTime.Parse(record.DepositDate.Replace(" UTC", "")) : orderDate;

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

}

app.Run();
