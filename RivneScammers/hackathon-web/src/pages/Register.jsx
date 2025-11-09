import React, { useState, useMemo, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register as apiRegister } from '../api/auth';
import { getToken } from '../api/auth';

const usernameRegex = /^[A-Za-z0-9_-]{3,50}$/; // допустимые символы, длина
const passwordHasNumber = (v) => /\d/.test(v);
const passwordHasLetter = (v) => /[A-Za-z]/.test(v);

const Register = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [touched, setTouched] = useState({});
  const [loading, setLoading] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [success, setSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const navigate = useNavigate();

  useEffect(() => {
    const token = getToken && getToken();
    if (token) {
      navigate('/dashboard', { replace: true });
    }
  }, [navigate]);

  const usernameValid = usernameRegex.test(username);
  const passwordValid = password.length >= 8 && password.length <= 100 && passwordHasNumber(password) && passwordHasLetter(password);
  const passwordsMatch = password && confirmPassword && password === confirmPassword;

  const passwordStrength = useMemo(() => {
    if (!password) return 0;
    let score = 0;
    if (password.length >= 8) score += 1;
    if (password.length >= 12) score += 1;
    if (passwordHasNumber(password)) score += 1;
    if (passwordHasLetter(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1; // спец символы
    return Math.min(score, 5);
  }, [password]);

  const canSubmit = usernameValid && passwordValid && passwordsMatch && email;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!canSubmit) return;
    setSubmitError('');
    setSuccess(false);
  setSuccessMessage('');
    setLoading(true);
    try {
      const res = await apiRegister({ username, email, password });
      if (res?.username) {
        setSuccess(true);
        setSuccessMessage(`Account created successfully! Welcome, ${res.username}!`);
        setTimeout(() => navigate('/login'), 3000);
      } else {
        setSubmitError('Unexpected response from server');
      }
    } catch (err) {
      setSubmitError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const markTouched = (field) => setTouched((t) => ({ ...t, [field]: true }));

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-slate-950">
      {/* Animated colorful blobs */}
      <div className="absolute -top-40 -left-20 w-96 h-96 bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 rounded-full mix-blend-screen filter blur-3xl opacity-50 animate-blob" />
      <div className="absolute top-1/2 -right-40 w-[28rem] h-[28rem] bg-gradient-to-tr from-cyan-500 via-teal-400 to-lime-300 rounded-full mix-blend-screen filter blur-3xl opacity-40 animate-blobSlow" />
      <div className="absolute bottom-0 left-1/3 w-80 h-80 bg-gradient-to-tr from-fuchsia-500 via-rose-400 to-amber-300 rounded-full mix-blend-screen filter blur-3xl opacity-40 animate-blob" />

      {/* Card */}
      <div className="relative z-10 w-full max-w-md px-8 py-10 rounded-3xl border border-white/20 bg-white/10 backdrop-blur-xl shadow-2xl shadow-indigo-900/30">
        <div className="mb-8 text-center">
          <h1 className="text-[34px] font-extrabold tracking-tight bg-gradient-to-r from-indigo-300 via-sky-200 to-pink-300 text-transparent bg-clip-text drop-shadow">Create Account</h1>
          <p className="mt-2 text-sm text-slate-300">Fill in the fields below to register</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-6">
          {submitError && (
            <div className="text-xs text-pink-300 bg-pink-500/10 border border-pink-400/30 rounded-md px-3 py-2">{submitError}</div>
          )}
          {success && (
            <div className="text-sm text-emerald-300 bg-emerald-500/10 border border-emerald-400/30 rounded-xl px-4 py-3 flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <div>
                <div className="font-semibold">{successMessage}</div>
                <div className="text-xs opacity-75 mt-1">Redirecting to login...</div>
              </div>
            </div>
          )}
          {/* Username */}
          <div className="group">
            <label htmlFor="username" className="block text-sm font-medium text-slate-200 mb-1">Username</label>
            <div className="relative">
              <input
                id="username"
                type="text"
                value={username}
                onBlur={() => markTouched('username')}
                onChange={(e) => setUsername(e.target.value)}
                required
                className={`peer w-full rounded-xl bg-white/5 border px-4 py-3 text-slate-100 placeholder-slate-400 outline-none transition ${username && !usernameValid ? 'border-pink-400 focus:border-pink-400 focus:ring-pink-400/40' : 'border-white/20 focus:border-indigo-300 focus:ring-indigo-300/40'} focus:ring-2`}
                placeholder="your username"
                autoComplete="username"
              />
              <div className="pointer-events-none absolute inset-0 rounded-xl ring-0 peer-focus:ring-4 peer-focus:ring-indigo-400/30 transition" />
            </div>
            {touched.username && !usernameValid && (
              <p className="mt-2 text-xs text-pink-300">3-50 chars. Letters, numbers, _ and - only.</p>
            )}
          </div>
          {/* Email */}
          <div className="group">
            <label htmlFor="email" className="block text-sm font-medium text-slate-200 mb-1">Email</label>
            <div className="relative">
              <input
                id="email"
                type="email"
                value={email}
                onBlur={() => markTouched('email')}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="peer w-full rounded-xl bg-white/5 border border-white/20 px-4 py-3 text-slate-100 placeholder-slate-400 outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-300/40 transition"
                placeholder="you@example.com"
                autoComplete="email"
              />
              <div className="pointer-events-none absolute inset-0 rounded-xl ring-0 peer-focus:ring-4 peer-focus:ring-indigo-400/30 transition" />
            </div>
          </div>
          {/* Password */}
            <div className="group">
              <label htmlFor="password" className="block text-sm font-medium text-slate-200 mb-1">Password</label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onBlur={() => markTouched('password')}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className={`peer w-full rounded-xl bg-white/5 border px-4 py-3 text-slate-100 placeholder-slate-400 outline-none transition ${password && !passwordValid ? 'border-pink-400 focus:border-pink-400 focus:ring-pink-400/40' : 'border-white/20 focus:border-indigo-300 focus:ring-indigo-300/40'} focus:ring-2`}
                  placeholder="••••••••"
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute top-1/2 -translate-y-1/2 right-3 text-xs font-medium text-indigo-200 hover:text-indigo-100 bg-indigo-500/20 hover:bg-indigo-500/30 px-2 py-1 rounded-md backdrop-blur-sm transition"
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>
              {touched.password && !passwordValid && (
                <p className="mt-2 text-xs text-pink-300">Min 8 chars, needs at least one letter and one number.</p>
              )}
              {/* Strength bar */}
              <div className="mt-3 flex items-center gap-2">
                {[1,2,3,4,5].map((i) => (
                  <div
                    key={i}
                    className={`h-2 flex-1 rounded-full transition ${passwordStrength >= i ? 'bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400' : 'bg-white/10'}`}
                  />
                ))}
              </div>
            </div>
          {/* Confirm Password */}
          <div className="group">
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-slate-200 mb-1">Confirm Password</label>
            <div className="relative">
              <input
                id="confirmPassword"
                type={showPassword ? 'text' : 'password'}
                value={confirmPassword}
                onBlur={() => markTouched('confirmPassword')}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                className={`peer w-full rounded-xl bg-white/5 border px-4 py-3 text-slate-100 placeholder-slate-400 outline-none transition ${confirmPassword && !passwordsMatch ? 'border-pink-400 focus:border-pink-400 focus:ring-pink-400/40' : 'border-white/20 focus:border-indigo-300 focus:ring-indigo-300/40'} focus:ring-2`}
                placeholder="repeat password"
                autoComplete="new-password"
              />
              <div className="pointer-events-none absolute inset-0 rounded-xl ring-0 peer-focus:ring-4 peer-focus:ring-indigo-400/30 transition" />
            </div>
            {touched.confirmPassword && confirmPassword && !passwordsMatch && (
              <p className="mt-2 text-xs text-pink-300">Passwords do not match.</p>
            )}
          </div>

          <button
            type="submit"
            disabled={!canSubmit || loading}
            className="w-full relative group overflow-hidden rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white font-semibold py-3 shadow-lg shadow-indigo-900/40 focus:outline-none focus:ring-2 focus:ring-pink-300/50 active:scale-[.98] transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="relative z-10">{loading ? 'Signing Up...' : 'Sign Up'}</span>
            <div className="absolute inset-0 bg-gradient-to-r from-pink-500 via-indigo-500 to-purple-500 opacity-0 group-hover:opacity-100 transition" />
          </button>
        </form>
        <div className="mt-6 text-center text-xs text-slate-400">
          <p>Already have an account? <Link to="/login" className="text-indigo-300 hover:text-indigo-200 font-medium">Sign In</Link></p>
        </div>
      </div>
    </div>
  );
};

export default Register;
