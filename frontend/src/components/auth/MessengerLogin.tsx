import { useState } from "react";
import { authApi } from "@/api/auth";
import { useAuthStore } from "@/stores/authStore";
import { useNavigate, Link } from "react-router-dom";

export function MessengerLogin() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const login = useAuthStore((s) => s.login);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    const formData = new FormData(e.currentTarget);
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;

    try {
      const data = await authApi.login(email, password);
      login(data.access_token, {
        id: data.user_id || "1",
        email,
        full_name: data.full_name || email.split("@")[0],
      });
      navigate("/chat");
    } catch (err: any) {
      setError(err?.toString() || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#0084FF] via-[#6C5CE7] to-[#A855F7]">
        {/* Floating orbs */}
        <div className="absolute top-[10%] left-[10%] w-72 h-72 bg-white/10 rounded-full blur-3xl floating-particle" />
        <div className="absolute top-[60%] right-[10%] w-96 h-96 bg-purple-400/10 rounded-full blur-3xl floating-particle" style={{ animationDelay: '2s' }} />
        <div className="absolute bottom-[10%] left-[30%] w-64 h-64 bg-blue-300/10 rounded-full blur-3xl floating-particle" style={{ animationDelay: '4s' }} />
        
        {/* Mesh gradient overlay */}
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_20%_50%,rgba(255,255,255,0.15),transparent_50%)]" />
          <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_80%_20%,rgba(168,85,247,0.2),transparent_50%)]" />
          <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_80%,rgba(0,132,255,0.15),transparent_50%)]" />
        </div>
      </div>

      {/* Left Side — Branding */}
      <div className="hidden lg:flex flex-1 relative z-10 items-center justify-center p-12">
        <div className="max-w-md text-white slide-up">
          {/* Messenger-style icon */}
          <div className="mb-8">
            <div className="w-20 h-20 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center shadow-lg">
              <svg width="44" height="44" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.477 2 2 6.145 2 11.243c0 2.908 1.434 5.503 3.683 7.2V22l3.3-1.815A11.3 11.3 0 0012 20.485c5.523 0 10-4.144 10-9.242S17.523 2 12 2z" fill="white"/>
                <path d="M13.228 13.991L10.58 11.2 5.5 14.05l5.57-5.91 2.648 2.792 5.08-2.85-5.57 5.909z" fill="#0084FF"/>
              </svg>
            </div>
          </div>
          <h1 className="text-5xl font-bold mb-4 leading-tight">
            MemoryChat
          </h1>
          <p className="text-xl text-white/80 mb-6 leading-relaxed">
            Your AI-powered messaging platform that remembers what matters.
          </p>
          <div className="flex flex-col gap-3 text-white/60 text-sm">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
                <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <span>AI-powered relationship intelligence</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
                <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <span>End-to-end encrypted conversations</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
                <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <span>Smart conversation memory</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side — Login Form */}
      <div className="flex-1 flex items-center justify-center p-6 relative z-10">
        <div className="w-full max-w-md slide-up" style={{ animationDelay: '0.2s' }}>
          <div className="glass-card rounded-2xl p-8 shadow-2xl">
            {/* Mobile logo */}
            <div className="lg:hidden flex items-center gap-3 mb-8 justify-center">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-messenger-blue to-messenger-purple flex items-center justify-center">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2C6.477 2 2 6.145 2 11.243c0 2.908 1.434 5.503 3.683 7.2V22l3.3-1.815A11.3 11.3 0 0012 20.485c5.523 0 10-4.144 10-9.242S17.523 2 12 2z" fill="white"/>
                  <path d="M13.228 13.991L10.58 11.2 5.5 14.05l5.57-5.91 2.648 2.792 5.08-2.85-5.57 5.909z" fill="#0084FF"/>
                </svg>
              </div>
              <span className="text-xl font-bold text-white">MemoryChat</span>
            </div>

            <h2 className="text-2xl font-bold text-text-primary mb-1">Welcome back</h2>
            <p className="text-text-secondary text-sm mb-6">Sign in to continue to MemoryChat</p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="login-email" className="block text-sm font-medium text-text-primary mb-1.5">
                  Email address
                </label>
                <input
                  id="login-email"
                  name="email"
                  type="email"
                  required
                  placeholder="you@example.com"
                  className="w-full px-4 py-3 rounded-xl bg-input border border-border text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-messenger-blue focus:border-transparent transition-all text-sm"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label htmlFor="login-password" className="block text-sm font-medium text-text-primary">
                    Password
                  </label>
                  <button type="button" className="text-xs text-messenger-blue hover:underline">
                    Forgot password?
                  </button>
                </div>
                <input
                  id="login-password"
                  name="password"
                  type="password"
                  required
                  placeholder="••••••••"
                  className="w-full px-4 py-3 rounded-xl bg-input border border-border text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-messenger-blue focus:border-transparent transition-all text-sm"
                />
              </div>

              {error && (
                <div className="bg-destructive/10 text-destructive text-sm px-4 py-2.5 rounded-xl flex items-center gap-2">
                  <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl text-white font-semibold text-sm messenger-gradient disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Signing in...
                  </span>
                ) : (
                  "Sign in"
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="flex items-center gap-3 my-6">
              <div className="flex-1 h-px bg-border" />
              <span className="text-xs text-text-tertiary uppercase tracking-wider">or</span>
              <div className="flex-1 h-px bg-border" />
            </div>

            {/* Social logins */}
            <div className="space-y-3">
              <button
                type="button"
                className="w-full py-3 px-4 rounded-xl border border-border bg-background hover:bg-secondary text-text-primary font-medium text-sm flex items-center justify-center gap-3 transition-all hover:shadow-sm"
              >
                <svg width="18" height="18" viewBox="0 0 24 24">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
                Continue with Google
              </button>

              <button
                type="button"
                className="w-full py-3 px-4 rounded-xl border border-border bg-background hover:bg-secondary text-text-primary font-medium text-sm flex items-center justify-center gap-3 transition-all hover:shadow-sm"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701"/>
                </svg>
                Continue with Apple
              </button>
            </div>

            <p className="text-center text-sm text-text-secondary mt-6">
              Don't have an account?{" "}
              <Link to="/signup" className="text-messenger-blue hover:underline font-medium">
                Create one
              </Link>
            </p>
          </div>

          {/* Terms */}
          <p className="text-center text-xs text-white/50 mt-4 px-4">
            By signing in, you agree to our{" "}
            <a href="#" className="underline hover:text-white/70">Terms of Service</a>{" "}
            and{" "}
            <a href="#" className="underline hover:text-white/70">Privacy Policy</a>
          </p>
        </div>
      </div>
    </div>
  );
}
