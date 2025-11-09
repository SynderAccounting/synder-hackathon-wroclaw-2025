# Synder AI Agent

Synder AI Agent is the client-facing shell for companies that rely on Synder’s AI consultant. Built
with Flutter, it delivers the same experience across iOS, Android, desktop, and web. All business
logic, decisions, and integrations live in n8n, so updating workflows or connecting new services
never requires shipping a new app build.

## Business Value

- Monetization Potential: Synder AI Agent can be launched as a premium add-on - unlocking new
  recurring revenue opportunities.
- Customer Retention: By delivering instant, actionable value, Synder AI Agent transforms your
  platform from a simple tool into an indispensable business companion that keeps users engaged over
  time.
- Ecosystem Engagement: Users spend more time within your product - exploring data, asking
  questions, and generating reports - driving deeper adoption and increasing overall platform
  stickiness.
- Differentiation: While others rely on static dashboards, Synder AI Agent offers a dynamic,
  conversational AI experience that sets your platform apart - simple, smart, and scalable.

## How It Works

- A customer sends a text or voice message.
- The app packs the payload and forwards it to n8n.
- n8n orchestrates the workflow — pulls data, runs analysis, calls external services, composes the
  response.
- The result comes back to the user as text, a PDF link, an image, or an error notification.

> **Key point:** n8n is the single source of truth for business logic. Every script, integration, or
> fallback lives inside the workflow. Adjust the workflow — the app instantly mirrors the new
> behavior.

For technical onboarding details, see [N8N_SETUP.md](./N8N_SETUP.md).

## Feature Highlights

- ChatGPT-style dialogue with animated AI typing.
- Automatic rendering of PDF reports and inline images returned by n8n.
- Voice messaging end-to-end: press-and-hold recording, instant sending, and in-thread playback.
- Smooth handling of long threads with auto-scroll and message history.
- Built-in feedback cues: copy-to-clipboard, error states, “AI is typing” indicator, and more.