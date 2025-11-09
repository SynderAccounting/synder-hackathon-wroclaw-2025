# SellHub by Algo7 - AI-Driven Refund Analysis and Profit Insights

> Analyze refund causes with AI and visualize net profit from sales.

## About

SellHub is a solution developed during the **Synder Hackathon Wroclaw 2025**. It leverages AI to analyze refund patterns and provides actionable insights to reduce refund rates. Additionally, it offers a comprehensive view of net profit from sales through interactive visualizations.

## Features

- **AI-Powered Refund Analysis**: Identify common refund reasons and receive recommendations to minimize them.
- **Net Profit Visualization**: Interactive charts to track daily profits and sales trends.
- **Customizable Time Periods**: Analyze data for specific months or the last 30 days.
- **Detailed Statistics**: Insights into most returned shoe types, sizes, and total refunds.

## Technology Stack

### Backend

- **Language**: Java
- **Framework**: Spring Boot 3
- **Database**: PostgreSQL
- **AI Integration**: Google Generative AI (Gemini)

### Frontend

- **Language**: TypeScript
- **Framework**: React
- **Build Tool**: Vite
- **Charts**: Recharts library for interactive visualizations.

## Installation

### Prerequisites

- Node.js (v22 or higher)
- Java (v21 or higher)
- PostgreSQL on Docker

### Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd algo7/backend
   ```

2. Run the server:

   ```bash
   mvn spring-boot:run
   ```

### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd algo7/frontend
   ```

2. Install dependencies:

   ```bash
   npm i
   ```

3. Start the development server:

   ```bash
   npm run dev
   ```

## Usage

1. Access the frontend at `http://localhost:5173`.
2. Navigate to the **Statistics** page to view profit insights.
3. Visit the **Refunds** page for AI-driven analysis.

## Team

- [Adrian Goral](https://github.com/xEdziu)
- [Adam Krzywicki](https://github.com/Aiffelowy)
- [Mateusz Andrzejewski](https://github.com/MANDRW)
- [Bartłomiej Kuk](https://github.com/PEXEL2002)

---

*Built during Synder Hackathon Wroclaw 2025*