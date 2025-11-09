import React, { useEffect, useState } from 'react';
import { Outlet, NavLink, Link, useNavigate } from 'react-router-dom';
import {
    LayoutDashboard,
    Package,
    FileOutput,
    Settings as SettingsIcon,
    Sparkles,
    User,
    ShoppingCart,
    LogOut
} from 'lucide-react';
import { getToken } from '../../api/auth';
import { ROUTES } from '../../constants';
import { useAuth } from '../../hooks/useAuth';
import Logo from "../../assets/logo.svg";

const menuItems = [
    {
        title: "Dashboard",
        url: ROUTES.DASHBOARD,
        icon: LayoutDashboard,
    },
    {
        title: "ML Suggestions",
        url: ROUTES.ML_SUGGESTIONS,
        icon: Sparkles,
    },
    {
        title: "Products",
        url: ROUTES.PRODUCTS,
        icon: Package,
    },
    {
        title: "Orders",
        url: ROUTES.ORDERS,
        icon: ShoppingCart,
    },
    {
        title: "Export",
        url: ROUTES.EXPORT,
        icon: FileOutput,
    },
    {
        title: "Settings",
        url: ROUTES.SETTINGS,
        icon: SettingsIcon,
    },
];

const DashboardLayout = ({ children }) => {
    const [userName, setUserName] = useState('');
    const [userEmail, setUserEmail] = useState('');
    const [isAuthed, setIsAuthed] = useState(false);
    const navigate = useNavigate();
    const { logout } = useAuth();

    useEffect(() => {
        const token = getToken && getToken();
        if (!token) {
            setIsAuthed(false);
            return;
        }
        try {
            const parts = token.split('.');
            if (parts.length === 3) {
                const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
                const padded = base64 + '='.repeat((4 - (base64.length % 4)) % 4);
                const json = atob(padded);
                const payload = JSON.parse(json);
                const name = payload?.name || payload?.username || payload?.sub || '';
                const email = payload?.email || '';
                setUserName(name);
                setUserEmail(email);
            }
            setIsAuthed(true);
        } catch {
            setIsAuthed(false);
        }
    }, []);

    return (
        <div className="relative min-h-screen bg-slate-950">
            {/* Animated background blobs */}
            <div
                className="fixed -top-40 -left-20 w-96 h-96 bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 rounded-full mix-blend-screen filter blur-3xl opacity-50 animate-blob"/>
            <div
                className="fixed top-1/2 -right-40 w-[28rem] h-[28rem] bg-gradient-to-tr from-cyan-500 via-teal-400 to-lime-300 rounded-full mix-blend-screen filter blur-3xl opacity-40 animate-blobSlow"/>
            <div
                className="fixed bottom-0 left-1/3 w-80 h-80 bg-gradient-to-tr from-fuchsia-500 via-rose-400 to-amber-300 rounded-full mix-blend-screen filter blur-3xl opacity-40 animate-blob"/>

            {/* Layout */}
            <div className="relative z-10 flex min-h-screen">
                {/* Sidebar */}
                <aside
                    className="fixed top-0 left-0 h-full w-64 border-r border-indigo-500/20 bg-indigo-500/10 backdrop-blur-xl">
                    <div className="flex flex-col h-full">
                        {/* Header */}
                        <Link to="/" className="p-4 inline-flex items-center decoration-0" aria-label="Home">
                            <img src={Logo} alt="CommerceHub logo" className="h-[40px] w-[40px] opacity-[85%]"/>
                            <div className="p-3">
                                <h1 className="text-[22px] font-extrabold tracking-tight bg-gradient-to-r from-indigo-300 via-sky-200 to-pink-300 text-transparent bg-clip-text">CommerceHub</h1>
                            </div>
                        </Link>

                        {/* Navigation */}
                        <nav className="flex-1 p-4">
                            <ul className="space-y-2">
                                {menuItems.map((item) => {
                                    const Icon = item.icon;
                                    return (
                                        <li key={item.title}>
                                            <NavLink
                                                to={item.url}
                                                className={({isActive}) =>
                                                    `flex items-center gap-3 px-3 py-2 rounded-xl transition-colors
                          ${isActive
                                                        ? 'bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white shadow-lg shadow-indigo-900/40'
                                                        : 'text-slate-200 hover:bg-indigo-500/10'
                                                    }`
                                                }
                                                data-testid={`link-${item.title.toLowerCase()}`}
                                            >
                                                <Icon className="h-5 w-5"/>
                                                <span className="font-medium">{item.title}</span>
                                            </NavLink>
                                        </li>
                                    );
                                })}
                            </ul>
                        </nav>

                        {/* Footer */}
                        <div className="p-4 border-t border-indigo-500/20">
                            {isAuthed ? (
                                <div className="flex items-center gap-2 p-2 rounded-xl hover:bg-indigo-500/10 transition">
                                    <div className="h-8 w-8 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-900/40">
                                        <User className="h-4 w-4 text-white" />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium text-slate-200 truncate">{userName || 'User'}</p>
                                        {userEmail && <p className="text-xs text-slate-400 truncate">{userEmail}</p>}
                                    </div>
                                    <button
                                        onClick={() => {
                                            logout();
                                            navigate('/');
                                        }}
                                        className="p-2 rounded-lg text-slate-400 hover:bg-rose-500/10 hover:text-rose-300 transition-colors"
                                        title="Logout"
                                    >
                                        <LogOut className="h-4 w-4" />
                                    </button>
                                </div>
                            ) : (
                                <Link
                                    to="/login"
                                    className="block w-full text-center relative group overflow-hidden rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white font-semibold py-2.5 shadow-lg shadow-indigo-900/40 focus:outline-none focus:ring-2 focus:ring-pink-300/50 active:scale-[.98] transition"
                                >
                                    <span className="relative z-10">Sign In</span>
                                    <span className="absolute inset-0 bg-gradient-to-r from-pink-500 via-indigo-500 to-purple-500 opacity-0 group-hover:opacity-100 transition" />
                                </Link>
                            )}
                        </div>
                    </div>
                </aside>

                {/* Main content */}
                <main className="flex-1 ml-64">
                    {/* Header */}
                    <header
                        className="sticky top-0 z-20 h-16 border-b border-indigo-500/20 bg-slate-950/50 backdrop-blur-xl px-6 flex items-center justify-between">
                        {isAuthed ? (
                            <h2 className="text-lg font-semibold text-slate-200">{`Welcome back, ${userName || 'User'}`}</h2>
                        ) : (
                            <h2 className="text-[22px] font-extrabold tracking-tight bg-gradient-to-r from-indigo-300 via-sky-200 to-pink-300 text-transparent bg-clip-text">Welcome to CommerceHub</h2>
                        )}
                        <span className="text-xs sm:text-sm text-slate-400 italic">
                            Manual refresh keeps data in sync.
                        </span>
                    </header>

                    {/* Page content */}
                    <div className="p-6">
                        {children ?? <Outlet />}
                    </div>
                </main>
            </div>
        </div>
    );
};

export default DashboardLayout;
