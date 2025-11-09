/**
 * Application Configuration
 * Central configuration file that exports environment variables
 */

// In Vite, use import.meta.env instead of process.env
// The variable must be prefixed with VITE_ to be exposed to the client
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';