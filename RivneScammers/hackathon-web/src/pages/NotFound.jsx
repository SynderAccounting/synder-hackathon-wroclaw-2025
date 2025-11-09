import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const NotFound = () => {
  const navigate = useNavigate();
  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-slate-950">
      {/* Animated colorful blobs */}
      <div className="absolute -top-40 -left-24 w-[28rem] h-[28rem] bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 rounded-full mix-blend-screen filter blur-3xl opacity-50 animate-blob" />
      <div className="absolute top-1/2 -right-40 w-[30rem] h-[30rem] bg-gradient-to-tr from-cyan-500 via-teal-400 to-lime-300 rounded-full mix-blend-screen filter blur-3xl opacity-40 animate-blobSlow" />
      <div className="absolute bottom-0 left-1/3 w-80 h-80 bg-gradient-to-tr from-fuchsia-500 via-rose-400 to-amber-300 rounded-full mix-blend-screen filter blur-3xl opacity-40 animate-blob" />

      {/* Glass card */}
      <div className="relative z-10 w-full max-w-md px-8 py-12 rounded-3xl border border-white/20 bg-white/10 backdrop-blur-xl shadow-2xl shadow-indigo-900/30 text-center">
        <div className="mb-6">
          <h1 className="text-[70px] leading-none font-extrabold bg-gradient-to-r from-indigo-300 via-sky-200 to-pink-300 text-transparent bg-clip-text drop-shadow">404</h1>
          <p className="mt-2 text-sm text-slate-300">Page not found or was moved</p>
        </div>
        <div className="space-y-4">
          <button
            onClick={() => navigate(-1)}
            className="w-full relative group overflow-hidden rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white font-semibold py-3 shadow-lg shadow-indigo-900/40 focus:outline-none focus:ring-2 focus:ring-pink-300/50 active:scale-[.98] transition"
          >
            <span className="relative z-10">Go Back</span>
            <div className="absolute inset-0 bg-gradient-to-r from-pink-500 via-indigo-500 to-purple-500 opacity-0 group-hover:opacity-100 transition" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default NotFound;

