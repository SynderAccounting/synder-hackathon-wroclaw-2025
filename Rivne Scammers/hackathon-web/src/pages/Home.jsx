import React, {useEffect, useState} from 'react';
import {Link, useNavigate} from 'react-router-dom';
import {getToken} from '../api/auth';
import Logo from '../assets/logo.svg';
import LogoReact from '../assets/tech/ReactIcon.svg';
import LogoVite from '../assets/tech/ViteIcon.svg';
import LogoTailwind from '../assets/tech/TailwindIcon.svg';
import LogoFastApi from '../assets/tech/FastApiIcon.svg';
import LogoPostgres from '../assets/tech/PostgresIcon.svg';
import LogoRedis from '../assets/tech/RedisIcon.svg';
import LogoJwt from '../assets/tech/JwtIcon.svg';
import LogoShopify from '../assets/tech/ShopifyIcon.svg';
import LogoStripe from '../assets/tech/StripeIcon.svg';
import LogoWebhooks from '../assets/tech/WebhooksIcon.svg';

const Home = () => {
    const navigate = useNavigate();
    const [authed, setAuthed] = useState(false);

    useEffect(() => {
        const token = getToken && getToken();
        if (token) {
            setAuthed(true);
        }
    }, []);

    return (
        <div className="relative min-h-screen overflow-hidden bg-slate-950">
            {/* Animated blobs */}
            <div
                className="absolute -top-40 -left-20 w-96 h-96 bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 rounded-full mix-blend-screen filter blur-3xl opacity-50 animate-blob"/>
            <div
                className="absolute top-1/2 -right-40 w-[28rem] h-[28rem] bg-gradient-to-tr from-cyan-500 via-teal-400 to-lime-300 rounded-full mix-blend-screen filter blur-3xl opacity-40 animate-blobSlow"/>
            <div
                className="absolute bottom-0 left-1/3 w-80 h-80 bg-gradient-to-tr from-fuchsia-500 via-rose-400 to-amber-300 rounded-full mix-blend-screen filter blur-3xl opacity-40 animate-blob"/>

            {/* Header */}
            <header
                className="relative z-20 h-16 border-b border-indigo-500/20 bg-slate-950/50 backdrop-blur-xl px-6 flex items-center justify-between">
                <Link to="/" className="inline-flex items-center decoration-0" aria-label="Home">
                    <img src={Logo} alt="CommerceHub logo" className="h-[50px] w-[50px] opacity-[85%]"/>
                    <div className="p-3">
                        <h1 className="text-[22px] font-extrabold tracking-tight bg-gradient-to-r from-indigo-300 via-sky-200 to-pink-300 text-transparent bg-clip-text">CommerceHub</h1>
                    </div>
                </Link>
                <nav className="flex items-center gap-3">
                    {authed ? (
                        <button
                            onClick={() => navigate('/dashboard')}
                            className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 px-5 py-2.5 font-semibold text-white shadow-md shadow-indigo-900/40 focus:outline-none focus:ring-2 focus:ring-pink-300/50 active:scale-[.98]"
                        >
                            <span className="relative z-10">Go to Dashboard</span>
                            <span
                                className="absolute inset-0 bg-gradient-to-r from-pink-500 via-indigo-500 to-purple-500 opacity-0 group-hover:opacity-100 transition"/>
                        </button>
                    ) : (
                        <>
                            <Link
                                to="/login"
                                className="px-4 py-2 rounded-xl border border-indigo-500/30 bg-white/5 text-indigo-200 hover:text-white hover:border-indigo-400 backdrop-blur-xl transition"
                            >
                                Sign In
                            </Link>
                            <Link
                                to="/register"
                                className="relative overflow-hidden px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white shadow-md shadow-indigo-900/40 hover:shadow-indigo-900/60 transition"
                            >
                                <span className="relative z-10">Sign Up</span>
                                <span
                                    className="absolute inset-0 bg-gradient-to-r from-pink-500 via-indigo-500 to-purple-500 opacity-0 hover:opacity-100 transition"/>
                            </Link>
                        </>
                    )}
                </nav>
            </header>

            {/* Hero */}
            <main className="relative z-10 px-6 pt-14 pb-16">
                <section className="max-w-4xl mx-auto text-center">
                    <h1 className="leading-none p-3 text-[110px] uppercase font-extrabold tracking-tight text-transparent bg-clip-text bg-[linear-gradient(90deg,#8b5cf6,#06b6d4,#22c55e,#eab308,#f97316,#ef4444,#ec4899,#8b5cf6)] bg-[length:400%_100%] animate-gradient drop-shadow-[0_2px_8px_rgba(0,0,0,0.35)]">CommerceHub</h1>
                    <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-300 via-sky-200 to-pink-300 text-transparent bg-clip-text mb-6">
                        Unified Commerce Dashboard
                    </h1>
                    <p className="text-[40px] md:text-[20px] text-slate-300 max-w-2xl mx-auto mb-8">
                        CommerceHub helps you monitor sales, manage products and understand customers in one beautiful,
                        fast and secure interface.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        {authed ? (
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 px-8 py-3 font-semibold text-white shadow-lg shadow-indigo-900/40 focus:outline-none focus:ring-2 focus:ring-pink-300/50 active:scale-[.98]"
                            >
                                <span className="relative z-10">Go to Dashboard</span>
                                <span
                                    className="absolute inset-0 bg-gradient-to-r from-pink-500 via-indigo-500 to-purple-500 opacity-0 group-hover:opacity-100 transition"/>
                            </button>
                        ) : (
                            <>
                                <Link
                                    to="/login"
                                    className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 px-8 py-3 font-semibold text-white shadow-lg shadow-indigo-900/40 focus:outline-none focus:ring-2 focus:ring-pink-300/50 active:scale-[.98] text-center"
                                >
                                    <span className="relative z-10">Sign In</span>
                                    <span
                                        className="absolute inset-0 bg-gradient-to-r from-pink-500 via-indigo-500 to-purple-500 opacity-0 group-hover:opacity-100 transition"/>
                                </Link>
                                <Link
                                    to="/register"
                                    className="group relative overflow-hidden rounded-xl border border-indigo-500/30 bg-white/5 backdrop-blur-xl px-8 py-3 font-semibold text-indigo-200 hover:text-white hover:border-indigo-400 shadow-lg shadow-indigo-900/30 focus:outline-none focus:ring-2 focus:ring-indigo-300/40 active:scale-[.98] text-center"
                                >
                                    <span className="relative z-10">Create Account</span>
                                </Link>
                            </>
                        )}
                    </div>
                </section>

                {/* About / Features */}
                <section className="mt-16 max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div
                        className="lg:col-span-2 border border-white/20 bg-white/10 backdrop-blur-xl rounded-2xl p-6 shadow-2xl shadow-indigo-900/30">
                        <h2 className="text-xl font-semibold text-slate-100 mb-3">About CommerceHub</h2>
                        <p className="text-slate-300">
                            We are a team focused on building delightful tools for e‑commerce. CommerceHub unifies your
                            product management, order tracking,
                            and analytics into a single, fast, and secure dashboard with a modern liquid glass design.
                        </p>
                        <p className="text-slate-300 mt-3">
                            Our mission is to give teams clarity and speed — so you can spend less time switching tabs
                            and more time growing your business.
                        </p>
                    </div>
                    <div
                        className="border border-white/20 bg-white/10 backdrop-blur-xl rounded-2xl p-6 shadow-2xl shadow-indigo-900/30">
                        <h3 className="text-lg font-semibold text-slate-100 mb-3">Highlights</h3>
                        <ul className="space-y-2 text-slate-300 list-disc list-inside">
                            <li>Real‑time insights and metrics</li>
                            <li>Powerful product and inventory tools</li>
                            <li>Secure authentication and roles</li>
                            <li>Modern, responsive UI</li>
                        </ul>
                    </div>
                </section>

                {/* Feature Cards */}
                <section className="mt-20 max-w-6xl mx-auto px-2">
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-indigo-300 via-sky-200 to-pink-300 text-transparent bg-clip-text mb-8 text-center">Why Teams Choose CommerceHub</h2>
                    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                        {[
                            {
                                title: 'Real-Time Analytics',
                                desc: 'Live metrics for revenue, conversion and inventory so you react instantly.',
                                icon: '📊',
                            },
                            {
                                title: 'Unified Product Control',
                                desc: 'One panel to create, categorize, bulk update and export products.',
                                icon: '🛍️',
                            },
                            {
                                title: 'Smart Order Flow',
                                desc: 'Statuses, filters, timeline & anomaly hints reduce support time.',
                                icon: '📦',
                            },
                            {
                                title: 'Role-Based Access',
                                desc: 'Granular permissions keep sensitive operations protected.',
                                icon: '🔐',
                            },
                            {
                                title: 'Fast API Integrations',
                                desc: 'Connect Shopify & other platforms via a clean versioned API.',
                                icon: '⚙️',
                            },
                            {
                                title: 'Liquid Glass UI',
                                desc: 'Modern, accessible design with subtle motion & dark-mode first.',
                                icon: '🧪',
                            },
                        ].map(card => (
                            <div key={card.title} className="group relative overflow-hidden rounded-2xl border border-white/15 bg-white/10 backdrop-blur-xl p-6 shadow-lg shadow-indigo-900/30 transition hover:border-indigo-400/40 hover:shadow-indigo-800/40">
                                <div className="absolute -top-20 -right-16 w-56 h-56 bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 opacity-20 blur-3xl rounded-full group-hover:opacity-30 transition" />
                                <div className="text-3xl mb-4 drop-shadow-sm select-none">{card.icon}</div>
                                <h3 className="text-lg font-semibold text-slate-100 mb-2">{card.title}</h3>
                                <p className="text-sm text-slate-300 leading-relaxed">{card.desc}</p>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Company Values */}
                <section className="mt-24 max-w-6xl mx-auto grid lg:grid-cols-2 gap-10">
                    <div className="relative overflow-hidden rounded-3xl border border-white/15 bg-gradient-to-br from-slate-900/70 via-slate-800/40 to-slate-900/70 backdrop-blur-xl p-8 shadow-xl shadow-black/40">
                        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_30%,rgba(99,102,241,0.25),transparent_70%)]" />
                        <h2 className="text-2xl font-bold text-slate-100 mb-4">Our Mission</h2>
                        <p className="text-slate-300 text-sm leading-relaxed">
                            We believe commerce tooling should feel inspiring. We remove friction between data and decisions: fewer clicks,
                            richer context, instant feedback. Our mission is to empower product & growth teams with clarity, speed and
                            confidence across every metric.
                        </p>
                        <ul className="mt-6 space-y-2 text-sm">
                            <li className="flex items-start gap-2"><span className="text-pink-300">◆</span><span className="text-slate-300">Design for focus & flow.</span></li>
                            <li className="flex items-start gap-2"><span className="text-pink-300">◆</span><span className="text-slate-300">Security & privacy as defaults.</span></li>
                            <li className="flex items-start gap-2"><span className="text-pink-300">◆</span><span className="text-slate-300">Performance over complexity.</span></li>
                            <li className="flex items-start gap-2"><span className="text-pink-300">◆</span><span className="text-slate-300">Transparent roadmap & feedback loop.</span></li>
                        </ul>
                    </div>
                    <div className="space-y-6">
                        <div className="rounded-2xl border border-indigo-400/30 bg-indigo-500/10 backdrop-blur-xl p-6 shadow-lg shadow-indigo-900/30">
                            <h3 className="text-lg font-semibold text-indigo-200 mb-2">Security & Reliability</h3>
                            <p className="text-slate-300 text-sm leading-relaxed">JWT, rotating secrets, rate limiting, audit trails & encrypted at rest storage keep your data locked tight.</p>
                        </div>
                        <div className="rounded-2xl border border-pink-400/30 bg-pink-500/10 backdrop-blur-xl p-6 shadow-lg shadow-pink-900/30">
                            <h3 className="text-lg font-semibold text-pink-200 mb-2">Performance</h3>
                            <p className="text-slate-300 text-sm leading-relaxed">Edge‑friendly APIs, aggressive caching and lightweight React components deliver <span className="text-pink-300 font-medium">sub‑100ms</span> median responses.</p>
                        </div>
                        <div className="rounded-2xl border border-cyan-400/30 bg-cyan-500/10 backdrop-blur-xl p-6 shadow-lg shadow-cyan-900/30">
                            <h3 className="text-lg font-semibold text-cyan-200 mb-2">Integrations</h3>
                            <p className="text-slate-300 text-sm leading-relaxed">Native connectors for Shopify (beta), Stripe, and webhooks. Extensible schema for future platforms.</p>
                        </div>
                    </div>
                </section>

                {/* Tech Stack */}
                <section className="mt-24 max-w-7xl mx-auto">
                    <h2 className="text-center text-2xl font-bold text-slate-100 mb-8">Built with Modern Technologies</h2>
                    <div className="relative overflow-hidden py-6">
                        <div className="pointer-events-none absolute inset-y-0 left-0 w-24 bg-gradient-to-r from-slate-950 to-transparent" />
                        <div className="pointer-events-none absolute inset-y-0 right-0 w-24 bg-gradient-to-l from-slate-950 to-transparent" />

                        {(() => {
                          const tech = [
                            { label: 'React', icon: LogoReact },
                            { label: 'Vite', icon: LogoVite },
                            { label: 'TailwindCSS', icon: LogoTailwind },
                            { label: 'FastAPI', icon: LogoFastApi },
                            { label: 'Redis', icon: LogoRedis },
                            { label: 'JWT', icon: LogoJwt },
                            { label: 'Shopify API', icon: LogoShopify },
                          ];
                          const doubled = [...tech, ...tech];
                          return (
                            <ul className="flex w-max flex-nowrap items-center gap-6 sm:gap-8 md:gap-10 animate-marquee-ltr-slow marquee-ltr pl-6">
                              {doubled.map((t, idx) => (
                                <li key={`${t.label}-${idx}`} className="flex-none flex items-center gap-3 px-5 py-3 rounded-xl border border-white/10 bg-white/5 backdrop-blur-md hover:border-indigo-400/40 transition">
                                  <img src={t.icon} alt={`${t.label} logo`} className="h-8 w-8" loading="lazy" />
                                  <span className="tracking-wide whitespace-nowrap text-slate-300">{t.label}</span>
                                </li>
                              ))}
                            </ul>
                          );
                        })()}
                    </div>
                </section>

                {/* CTA Banner */}
                <section className="mt-24 max-w-5xl mx-auto relative overflow-hidden rounded-3xl border border-white/15 bg-gradient-to-r from-indigo-500/20 via-purple-500/20 to-pink-500/20 backdrop-blur-xl p-8 shadow-xl shadow-indigo-900/40">
                    <div className="absolute -top-10 -left-10 w-40 h-40 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-full blur-3xl opacity-30" />
                    <div className="absolute bottom-0 right-0 w-52 h-52 bg-gradient-to-tr from-pink-500 to-fuchsia-500 rounded-full blur-3xl opacity-25" />
                    <h2 className="text-2xl font-bold text-slate-100 mb-3">Ready to simplify your commerce operations?</h2>
                    <p className="text-sm text-slate-300 mb-6">Create a free account and start exploring the dashboard. No credit card required, instant setup.</p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <Link to="/register" className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 px-6 py-3 font-semibold text-white shadow-lg shadow-indigo-900/40 focus:outline-none focus:ring-2 focus:ring-pink-300/50 active:scale-[.98]">
                            <span className="relative z-10">Get Started</span>
                            <span className="absolute inset-0 bg-gradient-to-r from-pink-500 via-indigo-500 to-purple-500 opacity-0 group-hover:opacity-100 transition" />
                        </Link>
                        <Link to="/login" className="px-6 py-3 rounded-xl border border-indigo-500/30 bg-white/5 text-indigo-200 hover:text-white hover:border-indigo-400 backdrop-blur-xl transition font-semibold">
                            Sign In
                        </Link>
                    </div>
                </section>

                {/* Footer */}
                <footer className="mt-24 mb-8 text-center text-xs text-slate-500">
                    <p>© {new Date().getFullYear()} CommerceHub. All rights reserved.</p>
                </footer>

                {!authed && (
                    <p className="mt-12 text-center text-xs text-slate-400">
                        By continuing you agree to our <span className="text-indigo-300">Terms</span> and <span
                        className="text-indigo-300">Privacy Policy</span>.
                    </p>
                )}
            </main>
        </div>
    );
};

export default Home;
