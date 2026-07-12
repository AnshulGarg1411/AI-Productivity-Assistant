import { Navigate } from "react-router-dom";
import { getGoogleLoginUrl } from "../api/authApi";
import { useAuth } from "../contexts/AuthContext";

const Login = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (!isLoading && isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleGoogleLogin = () => {
    window.location.href = getGoogleLoginUrl();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-canvas px-4">
      <div className="w-full max-w-[360px] text-center">
        <div className="mx-auto w-9 h-9 rounded-md bg-accent text-white flex items-center justify-center text-base font-semibold mb-6">
          F
        </div>

        <h1 className="text-xl font-semibold text-ink">
          Log in to Flow
        </h1>
        <p className="text-sm text-ink-muted mt-1.5 mb-8">
          Your emails, calendar, and tasks, in one workspace.
        </p>

        <button
          onClick={handleGoogleLogin}
          className="w-full flex items-center justify-center gap-3 border border-border rounded-md py-2.5 px-4 text-sm font-medium text-ink hover:bg-surface-hover transition-colors"
        >
          <svg width="16" height="16" viewBox="0 0 48 48">
            <path
              fill="#FFC107"
              d="M43.6 20.5H42V20H24v8h11.3c-1.6 4.6-6 8-11.3 8-6.6 0-12-5.4-12-12s5.4-12 12-12c3 0 5.8 1.1 7.9 3l5.7-5.7C34.6 6 29.6 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.7-.4-3.5z"
            />
            <path
              fill="#FF3D00"
              d="m6.3 14.7 6.6 4.8C14.6 15.9 18.9 13 24 13c3 0 5.8 1.1 7.9 3l5.7-5.7C34.6 6 29.6 4 24 4c-7.4 0-13.8 4.1-17.1 10.1z"
            />
            <path
              fill="#4CAF50"
              d="M24 44c5.5 0 10.4-1.9 14.3-5.1l-6.6-5.4C29.6 35.4 27 36 24 36c-5.2 0-9.6-3.4-11.2-8l-6.5 5C9.9 39.6 16.4 44 24 44z"
            />
            <path
              fill="#1976D2"
              d="M43.6 20.5H42V20H24v8h11.3c-.8 2.3-2.3 4.3-4.2 5.5l6.6 5.4C41.5 35.6 44 30.2 44 24c0-1.3-.1-2.7-.4-3.5z"
            />
          </svg>
          Continue with Google
        </button>

        <p className="text-xs text-ink-faint mt-8 leading-relaxed">
          We only request read access to your Gmail and Calendar.
        </p>
      </div>
    </div>
  );
};

export default Login;
