/**
 * Maps API error responses to user-friendly English messages
 */
export function getErrorMessage(error: unknown, context: 'login' | 'register'): string {
  // Handle Error objects
  if (error instanceof Error) {
    const message = error.message.toLowerCase();

    // Common error patterns
    if (message.includes('network') || message.includes('fetch')) {
      return 'Unable to connect to the server. Please check your internet connection.';
    }

    if (message.includes('timeout')) {
      return 'Request timed out. Please try again.';
    }

    // Polish to English translations for common errors
    if (message.includes('nieprawidłowa nazwa użytkownika lub hasło') ||
        message.includes('nieprawidłowe dane') ||
        message.includes('błędne dane logowania')) {
      return 'Invalid username or password. Please try again.';
    }

    if (message.includes('użytkownik już istnieje') ||
        message.includes('email już istnieje') ||
        message.includes('konto już istnieje')) {
      return 'An account with this username or email already exists.';
    }

    if (message.includes('nieprawidłowy email') || message.includes('błędny adres email')) {
      return 'Please enter a valid email address.';
    }

    if (message.includes('hasło zbyt słabe') || message.includes('słabe hasło')) {
      return 'Password is too weak. Please use a stronger password.';
    }

    // Context-specific errors
    if (context === 'login') {
      if (message.includes('unauthorized') || message.includes('invalid credentials') || message.includes('401')) {
        return 'Invalid username or password. Please try again.';
      }
      if (message.includes('not found') || message.includes('404')) {
        return 'User not found. Please check your credentials.';
      }
      if (message.includes('account locked') || message.includes('locked')) {
        return 'Your account has been locked. Please contact support.';
      }
    }

    if (context === 'register') {
      if (message.includes('already exists')||message.includes("nazwie już istnieje") || message.includes('duplicate') || message.includes('409')) {
        return 'An account with this username or email already exists.';
      }
      if (message.includes('invalid email')) {
        return 'Please enter a valid email address.';
      }
      if (message.includes('password') && message.includes('weak')) {
        return 'Password is too weak. Please use a stronger password.';
      }
      if (message.includes('username') && message.includes('invalid')) {
        return 'Username contains invalid characters.';
      }
    }

    // Return the original error message if no pattern matches
    return error.message;
  }

  // Handle HTTP response errors
  if (typeof error === 'object' && error !== null && 'status' in error) {
    const status = (error as any).status;

    switch (status) {
      case 400:
        return context === 'register'
          ? 'Invalid registration data. Please check all fields.'
          : 'Invalid login credentials. Please try again.';
      case 401:
        return 'Invalid username or password.';
      case 403:
        return 'Access denied. Please check your credentials.';
      case 404:
        return 'User not found.';
      case 409:
        return 'An account with this username or email already exists.';
      case 422:
        return 'Validation failed. Please check your input.';
      case 429:
        return 'Too many attempts. Please try again later.';
      case 500:
        return 'Server error. Please try again later.';
      case 503:
        return 'Service temporarily unavailable. Please try again later.';
      default:
        return 'An unexpected error occurred. Please try again.';
    }
  }

  // Fallback for unknown error types
  if (context === 'login') {
    return 'Login failed. Please check your credentials and try again.';
  }

  return 'Registration failed. Please try again.';
}
