import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { login as apiLogin, setTokenCookie, getToken } from '../api/auth';

const Login = () => {
  const [login, setLogin] = useState(''); // логин или почта
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = getToken && getToken();
    if (token) {
      navigate('/dashboard', { replace: true });
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await apiLogin({ login, password });
      if (res?.access_token) {
        setTokenCookie(res.access_token, rememberMe);
        navigate('/dashboard');
      } else {
        setError('Unexpected response from server');
      }
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-slate-950">
      {/* Animated colorful blobs in background */}
      <div className="absolute -top-40 -left-20 w-96 h-96 bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 rounded-full mix-blend-screen filter blur-3xl opacity-50 animate-blob" />
      <div className="absolute top-1/2 -right-40 w-[28rem] h-[28rem] bg-gradient-to-tr from-cyan-500 via-teal-400 to-lime-300 rounded-full mix-blend-screen filter blur-3xl opacity-40 animate-blobSlow" />
      <div className="absolute bottom-0 left-1/3 w-80 h-80 bg-gradient-to-tr from-fuchsia-500 via-rose-400 to-amber-300 rounded-full mix-blend-screen filter blur-3xl opacity-40 animate-blob" />

      {/* Glass translucent card */}
      <div className="relative z-10 w-full max-w-md px-8 py-10 rounded-3xl border border-white/20 bg-white/10 backdrop-blur-xl shadow-2xl shadow-indigo-900/30">
        <div className="mb-8 text-center">
          <h1 className="text-[34px] font-extrabold tracking-tight bg-gradient-to-r from-indigo-300 via-sky-200 to-pink-300 text-transparent bg-clip-text drop-shadow">Sign In</h1>
          <p className="mt-2 text-sm text-slate-300">Sign in to continue</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="text-xs text-pink-300 bg-pink-500/10 border border-pink-400/30 rounded-md px-3 py-2">
              {error}
            </div>
          )}
          <div className="group">
            <label htmlFor="login" className="block text-sm font-medium text-slate-200 mb-1">Username or Email</label>
            <div className="relative">
              <input
                id="login"
                type="text"
                value={login}
                onChange={(e) => setLogin(e.target.value)}
                required
                className="peer w-full rounded-xl bg-white/5 border border-white/20 px-4 py-3 text-slate-100 placeholder-slate-400 outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-300/40 transition"
                placeholder="username or email"
                autoComplete="username email"
              />
              <div className="pointer-events-none absolute inset-0 rounded-xl ring-0 peer-focus:ring-4 peer-focus:ring-indigo-400/30 transition" />
            </div>
          </div>
          <div className="group">
            <label htmlFor="password" className="block text-sm font-medium text-slate-200 mb-1">Password</label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="peer w-full rounded-xl bg-white/5 border border-white/20 px-4 py-3 text-slate-100 placeholder-slate-400 outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-300/40 transition"
                placeholder="••••••••"
                autoComplete="current-password"
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                className="absolute top-1/2 -translate-y-1/2 right-3 text-xs font-medium text-indigo-200 hover:text-indigo-100 bg-indigo-500/20 hover:bg-indigo-500/30 px-2 py-1 rounded-md backdrop-blur-sm transition"
              >
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between text-sm">
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input type="checkbox" className="accent-indigo-400/80 w-4 h-4 rounded" checked={rememberMe} onChange={(e)=>setRememberMe(e.target.checked)} />
              <span className="text-slate-200">Remember me</span>
            </label>
            <Link to="/forgot" className="text-indigo-300 hover:text-indigo-200 transition underline-offset-4 hover:underline">Forgot password?</Link>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full relative group overflow-hidden rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white font-semibold py-3 shadow-lg shadow-indigo-900/40 focus:outline-none focus:ring-2 focus:ring-pink-300/50 active:scale-[.98] transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="relative z-10">{loading ? 'Signing In...' : 'Sign In'}</span>
            <div className="absolute inset-0 bg-gradient-to-r from-pink-500 via-indigo-500 to-purple-500 opacity-0 group-hover:opacity-100 transition" />
          </button>
        </form>

        <div className="mt-6 text-center text-xs text-slate-400">
          <p>Don't have an account? <Link to="/register" className="text-indigo-300 hover:text-indigo-200 font-medium">Register</Link></p>
        </div>
      </div>
    </div>
  );
};

export default Login;
