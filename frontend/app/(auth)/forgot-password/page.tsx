"use client";

import { useState } from "react";
import { Brain, Eye, EyeOff } from "lucide-react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (newPassword.length < 8) {
        throw new Error("Mật khẩu mới phải có tối thiểu 8 ký tự.");
      }
      if (newPassword !== confirmation) {
        throw new Error("Xác nhận mật khẩu không khớp.");
      }
      const response = await fetch("/api/auth/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          full_name: fullName,
          phone: phone || undefined,
          new_password: newPassword,
        }),
      });
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.error ?? "Không thể gửi yêu cầu đặt lại mật khẩu");
      }
      setSubmitted(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể gửi yêu cầu đặt lại mật khẩu");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="w-full rounded-[28px] sm:rounded-[32px] bg-white p-7 sm:p-9 shadow-[0_20px_50px_rgba(0,0,0,0.06)] border border-slate-100/90 my-4">
      {/* Top Icon & Heading */}
      <div className="text-center mb-6">
        <div className="mx-auto mb-3.5 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
          <Brain className="w-7 h-7 stroke-[1.8]" />
        </div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Quên mật khẩu?</h1>
        <p className="mt-1 text-sm text-slate-500">
          Xác minh thông tin tài khoản để đặt lại mật khẩu trực tiếp.
        </p>
      </div>

      {submitted ? (
        <div className="space-y-4 text-center">
          <div className="rounded-2xl bg-blue-50 p-4 text-sm text-blue-800 border border-blue-100">
            Mật khẩu đã được đặt lại thành công. Bạn có thể đăng nhập bằng mật khẩu mới ngay bây giờ.
          </div>
          <a
            href="/login"
            className="inline-flex h-11 w-full items-center justify-center rounded-2xl bg-blue-600 font-medium text-sm text-white shadow-sm shadow-blue-500/25 transition-all hover:bg-blue-700"
          >
            Đến trang đăng nhập
          </a>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-3.5">
          <div>
            <label htmlFor="email" className="mb-1 block text-xs font-medium text-slate-700">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="email@example.com"
              className="h-11 w-full rounded-2xl border border-slate-200 bg-white px-4 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition-all focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10"
            />
          </div>

          <div>
            <label htmlFor="full-name" className="mb-1 block text-xs font-medium text-slate-700">
              Họ và tên
            </label>
            <input
              id="full-name"
              required
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              placeholder="Nguyễn Văn A"
              className="h-11 w-full rounded-2xl border border-slate-200 bg-white px-4 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition-all focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10"
            />
          </div>

          <div>
            <label htmlFor="phone" className="mb-1 block text-xs font-medium text-slate-700">
              Số điện thoại (nếu tài khoản có đăng ký)
            </label>
            <input
              id="phone"
              type="tel"
              value={phone}
              onChange={(event) => setPhone(event.target.value)}
              placeholder="0912345678"
              className="h-11 w-full rounded-2xl border border-slate-200 bg-white px-4 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition-all focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label htmlFor="new-password" className="mb-1 block text-xs font-medium text-slate-700">
                Mật khẩu mới
              </label>
              <div className="relative">
                <input
                  id="new-password"
                  type={showPassword ? "text" : "password"}
                  required
                  minLength={8}
                  autoComplete="new-password"
                  value={newPassword}
                  onChange={(event) => setNewPassword(event.target.value)}
                  placeholder="••••••••"
                  className="h-11 w-full rounded-2xl border border-slate-200 bg-white px-4 pr-10 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition-all focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-0.5"
                >
                  {showPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>

            <div>
              <label htmlFor="confirm-password" className="mb-1 block text-xs font-medium text-slate-700">
                Xác nhận mật khẩu mới
              </label>
              <div className="relative">
                <input
                  id="confirm-password"
                  type={showConfirmPassword ? "text" : "password"}
                  required
                  minLength={8}
                  autoComplete="new-password"
                  value={confirmation}
                  onChange={(event) => setConfirmation(event.target.value)}
                  placeholder="••••••••"
                  className="h-11 w-full rounded-2xl border border-slate-200 bg-white px-4 pr-10 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition-all focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-0.5"
                >
                  {showConfirmPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>
          </div>

          {error && (
            <div className="rounded-xl bg-red-50 p-3 text-xs text-red-600 border border-red-100">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full h-11 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm shadow-sm shadow-blue-500/25 transition-all active:scale-[0.99] disabled:opacity-60 flex items-center justify-center cursor-pointer mt-3"
          >
            {loading ? "Đang đặt lại..." : "Đặt lại mật khẩu"}
          </button>
        </form>
      )}

      <p className="mt-5 text-center text-sm text-slate-500">
        <a href="/login" className="font-semibold text-blue-600 hover:text-blue-700 hover:underline">
          Quay lại đăng nhập
        </a>
      </p>
    </div>
  );
}
