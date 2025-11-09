import { cn } from '@/lib/utils';

// ========================================
// EDITABLE CONTENT - Update this section to change the landing page content
// ========================================
const LANDING_PAGE_CONTENT = {
  title: 'SellHub',
  subtitle: 'Your All-in-One E-commerce Sales Hub',
  description: 'Synchronize, analyze, and optimize your online sales across multiple platforms.',
  features: [
    {
      title: 'Multi-Platform Synchronization',
      description: 'Seamlessly sync your sales data from WooCommerce and Shopify in one centralized dashboard.',
      icon: '🔄',
    },
    {
      title: 'Refund Analysis & Insights',
      description: 'Get AI-powered tips and recommendations on what to change to reduce refunds and improve customer satisfaction.',
      icon: '📊',
    },
    {
      title: 'Restock Prediction',
      description: 'Smart predictions about product quantity needed for restocking. Get monthly restock recommendations based on sales patterns.',
      icon: '📦',
    },
  ],
  ctaText: 'Get Started',
  ctaLink: '/register',
};
// ========================================

export function HomePage() {
  return (
    <div
      className="min-h-screen pt-8"
      style={{
        backgroundColor: 'var(--bg)',
      }}
    >
      <div className="container mx-auto px-4 py-16 max-w-6xl">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1
            className="text-5xl font-bold mb-4"
            style={{ color: 'var(--color-accent)' }}
          >
            {LANDING_PAGE_CONTENT.title}
          </h1>
          <h2
            className="text-2xl font-semibold mb-6"
            style={{ color: 'var(--text)' }}
          >
            {LANDING_PAGE_CONTENT.subtitle}
          </h2>
          <p
            className="text-lg max-w-2xl mx-auto mb-8"
            style={{ color: 'var(--text-muted)' }}
          >
            {LANDING_PAGE_CONTENT.description}
          </p>
          <a
            href={LANDING_PAGE_CONTENT.ctaLink}
            className={cn(
              'inline-block px-8 py-3 rounded-lg font-semibold text-lg',
              'transition-all duration-200 hover:opacity-90 shadow-lg hover:shadow-xl'
            )}
            style={{
              backgroundColor: 'var(--color-accent)',
              color: 'var(--bg)',
            }}
          >
            {LANDING_PAGE_CONTENT.ctaText}
          </a>
        </div>

        {/* Features Section */}
        <div className="grid md:grid-cols-3 gap-8 mt-16">
          {LANDING_PAGE_CONTENT.features.map((feature, index) => (
            <div
              key={index}
              className="rounded-lg shadow-lg border p-6 transition-all duration-200 hover:shadow-xl"
              style={{
                backgroundColor: 'var(--bg-light)',
                borderColor: 'var(--border)',
              }}
            >
              <div className="text-5xl mb-4">{feature.icon}</div>
              <h3
                className="text-xl font-semibold mb-3"
                style={{ color: 'var(--text)' }}
              >
                {feature.title}
              </h3>
              <p
                className="text-base"
                style={{ color: 'var(--text-muted)' }}
              >
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Additional CTA Section */}
        <div className="text-center mt-16">
          <p
            className="text-lg mb-4"
            style={{ color: 'var(--text)' }}
          >
            Ready to streamline your e-commerce operations?
          </p>
          <a
            href="/login"
            className="font-medium hover:underline text-lg"
            style={{ color: 'var(--color-accent)' }}
          >
            Already have an account? Sign in
          </a>
        </div>
      </div>
    </div>
  );
}
