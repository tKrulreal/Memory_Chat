import { useState } from "react";
import { authApi } from "@/api/auth";
import { useNavigate, Link } from "react-router-dom";

export function MessengerSignup() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    const formData = new FormData(e.currentTarget);
    const name = formData.get("name") as string;
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;
    const confirmPassword = formData.get("confirm-password") as string;

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      setLoading(false);
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      setLoading(false);
      return;
    }

    try {
      await authApi.register(email, password, name);
      navigate("/login");
    } catch (err: any) {
      setError(err?.toString() || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#A855F7] via-[#6C5CE7] to-[#0084FF]">
        <div className="absolute top-[20%] right-[15%] w-80 h-80 bg-white/10 rounded-full blur-3xl floating-particle" />
        <div className="absolute bottom-[20%] left-[10%] w-72 h-72 bg-blue-400/10 rounded-full blur-3xl floating-particle" style={{ animationDelay: '3s' }} />
        <div className="absolute top-[50%] left-[50%] w-64 h-64 bg-purple-300/10 rounded-full blur-3xl floating-particle" style={{ animationDelay: '1s' }} />
        
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_70%_30%,rgba(255,255,255,0.15),transparent_50%)]" />
          <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_30%_70%,rgba(0,132,255,0.2),transparent_50%)]" />
        </div>
      </div>

      {/* Left Side — Branding */}
      <div className="hidden lg:flex flex-1 relative z-10 items-center justify-center p-12">
        <div className="max-w-md text-white slide-up">
          <div className="mb-8">
            <div className="w-20 h-20 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center shadow-lg">
              <svg width="44" height="44" viewBox="0 0 24 24" fill="none">
                <path d="M12 2C6.477 2 2 6.145 2 11.243c0 2.908 1.434 5.503 3.683 7.2V22l3.3-1.815A11.3 11.3 0 0012 20.485c5.523 0 10-4.144 10-9.242S17.523 2 12 2z" fill="white"/>
                <path d="M13.228 13.991L10.58 11.2 5.5 14.05l5.57-5.91 2.648 2.792 5.08-2.85-5.57 5.909z" fill="#A855F7"/>
              </svg>
            </div>
          </div>
          <h1 className="text-5xl font-bold mb-4 leading-tight">
            Join MemoryChat
          </h1>
          <p className="text-xl text-white/80 mb-6 leading-relaxed">
            Start building smarter relationships with AI-powered conversations.
          </p>
          <div className="flex gap-6 text-white/60 text-sm">
            <div className="flex items-center gap-2">
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              <span>Free forever</span>
            </div>
            <div className="flex items-center gap-2">
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              <span>AI-powered</span>
            </div>
            <div className="flex items-center gap-2">
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              <span>Secure</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side — Signup Form */}
      <div className="flex-1 flex items-center justify-center p-6 relative z-10">
        <div className="w-full max-w-md slide-up" style={{ animationDelay: '0.2s' }}>
          <div className="glass-card rounded-2xl p-8 shadow-2xl">
            {/* Mobile logo */}
            <div className="lg:hidden flex items-center gap-3 mb-6 justify-center">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-messenger-purple to-messenger-blue flex items-center justify-center">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2C6.477 2 2 6.145 2 11.243c0 2.908 1.434 5.503 3.683 7.2V22l3.3-1.815A11.3 11.3 0 0012 20.485c5.523 0 10-4.144 10-9.242S17.523 2 12 2z" fill="white"/>
                  <path d="M13.228 13.991L10.58 11.2 5.5 14.05l5.57-5.91 2.648 2.792 5.08-2.85-5.57 5.909z" fill="#A855F7"/>
                </svg>
              </div>
              <span className="text-xl font-bold text-white">MemoryChat</span>
            </div>

            <h2 className="text-2xl font-bold text-text-primary mb-1">Create your account</h2>
            <p className="text-text-secondary text-sm mb-6">Join thousands of smart communicators</p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="signup-name" className="block text-sm font-medium text-text-primary mb-1.5">
                  Full name
                </label>
                <input
                  id="signup-name"
                  name="name"
                  type="text"
                  required
                  placeholder="John Doe"
                  className="w-full px-4 py-3 rounded-xl bg-input border border-border text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-messenger-blue focus:border-transparent transition-all text-sm"
                />
              </div>

              <div>
                <label htmlFor="signup-email" className="block text-sm font-medium text-text-primary mb-1.5">
                  Email address
                </label>
                <input
                  id="signup-email"
                  name="email"
                  type="email"
                  required
                  placeholder="you@example.com"
                  className="w-full px-4 py-3 rounded-xl bg-input border border-border text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-messenger-blue focus:border-transparent transition-all text-sm"
                />
              </div>

              <div>
                <label htmlFor="signup-password" className="block text-sm font-medium text-text-primary mb-1.5">
                  Password
                </label>
                <input
                  id="signup-password"
                  name="password"
                  type="password"
                  required
                  placeholder="At least 8 characters"
                  className="w-full px-4 py-3 rounded-xl bg-input border border-border text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-messenger-blue focus:border-transparent transition-all text-sm"
                />
              </div>

              <div>
                <label htmlFor="signup-confirm" className="block text-sm font-medium text-text-primary mb-1.5">
                  Confirm password
                </label>
                <input
                  id="signup-confirm"
                  name="confirm-password"
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
                    Creating account...
                  </span>
                ) : (
                  "Create account"
                )}
              </button>
            </form>

            <p className="text-center text-sm text-text-secondary mt-6">
              Already have an account?{" "}
              <Link to="/login" className="text-messenger-blue hover:underline font-medium">
                Sign in
              </Link>
            </p>
          </div>

          <p className="text-center text-xs text-white/50 mt-4 px-4">
            By creating an account, you agree to our{" "}
            <a href="#" className="underline hover:text-white/70">Terms of Service</a>{" "}
            and{" "}
            <a href="#" className="underline hover:text-white/70">Privacy Policy</a>
          </p>
        </div>
      </div>
    </div>
  );
}
