import Groq from 'groq-sdk';

/**
 * Generates a sales summary using AI (Groq).
 * @param {object} salesData - Raw sales data from Shopify or Square.
 * @param {string} platform - Platform type ('Shopify' or 'Square').
 * @returns {Promise<string>} - Text summary returned by the AI.
 */
export async function generateSalesSummary(
  salesData: {
    orderCount: number;
    totalSales: string;
    currency: string;
    topProducts: Array<{ title: string; quantity: number }>;
  },
  platform?: string
): Promise<string> {
  if (!process.env.GROQ_API_KEY) {
    console.error("Missing GROQ_API_KEY");
    return "Error: Missing AI configuration.";
  }

  // Initialize Groq client inside the function
  const groq = new Groq({
    apiKey: process.env.GROQ_API_KEY,
  });

  // Convert data to plain text so the AI can consume it
  const topProductsText = salesData.topProducts
    .map(p => `${p.title} (${p.quantity} pcs)`)
    .join(', ');

  const platformInfo = platform ? `Platform: ${platform}, ` : '';
  const dataString = `${platformInfo}Orders: ${salesData.orderCount}, Total sales: ${salesData.totalSales} ${salesData.currency}, Top products: ${topProductsText}`;

  // Build the system prompt
  const systemPrompt = `You are an e-commerce assistant. Write a short daily summary (max 3 sentences) for the store owner. Be upbeat if sales are good. Always include the number of orders and total sales. Finish with one concrete recommendation.`;

  try {
    console.log("Sending to Groq:", { systemPrompt, dataString });

    const chatCompletion = await groq.chat.completions.create({
      messages: [
        {
          role: 'user',
          content: `${systemPrompt}\n\nDane: ${dataString}`,
        },
      ],
      model: 'meta-llama/llama-4-maverick-17b-128e-instruct',
      temperature: 0.5,
      max_tokens: 100,
    });

    console.log("Groq response:", chatCompletion.choices[0]?.message?.content);
    return chatCompletion.choices[0]?.message?.content || "Failed to generate summary.";

  } catch (error: any) {
    console.error("Groq API error:", error?.message || error);
    console.error("Full error:", error);
    return `API Error: ${error?.message || 'Unknown error'}`;
  }
}
