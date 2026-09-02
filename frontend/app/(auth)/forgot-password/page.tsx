"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
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
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-md rounded-2xl bg-card p-8 shadow-lg">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-foreground">Quên mật khẩu?</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Xác minh thông tin tài khoản để đặt lại mật khẩu trực tiếp.
          </p>
        </div>

        {submitted ? (
          <p className="rounded-lg bg-muted p-4 text-sm text-muted-foreground">
            Mật khẩu đã được đặt lại. Bạn có thể đăng nhập bằng mật khẩu mới.
          </p>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="mb-1 block text-sm font-medium text-foreground">Email</label>
              <input
                id="email"
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="email@example.com"
                className="h-11 w-full rounded-lg border border-gray-300 px-4 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
              />
            </div>
            <div>
              <label htmlFor="full-name" className="mb-1 block text-sm font-medium text-foreground">Họ và tên</label>
              <input id="full-name" required value={fullName} onChange={(event) => setFullName(event.target.value)} placeholder="Nguyễn Văn A" className="h-11 w-full rounded-lg border border-gray-300 px-4 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20" />
            </div>
            <div>
              <label htmlFor="phone" className="mb-1 block text-sm font-medium text-foreground">Số điện thoại (nếu tài khoản có đăng ký)</label>
              <input id="phone" type="tel" value={phone} onChange={(event) => setPhone(event.target.value)} placeholder="0912345678" className="h-11 w-full rounded-lg border border-gray-300 px-4 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20" />
            </div>
            <div>
              <label htmlFor="new-password" className="mb-1 block text-sm font-medium text-foreground">Mật khẩu mới</label>
              <input id="new-password" type="password" required minLength={8} autoComplete="new-password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} className="h-11 w-full rounded-lg border border-gray-300 px-4 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20" />
            </div>
            <div>
              <label htmlFor="confirm-password" className="mb-1 block text-sm font-medium text-foreground">Xác nhận mật khẩu mới</label>
              <input id="confirm-password" type="password" required minLength={8} autoComplete="new-password" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} className="h-11 w-full rounded-lg border border-gray-300 px-4 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20" />
            </div>
            {error && <p className="text-sm text-red-500">{error}</p>}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Đang đặt lại..." : "Đặt lại mật khẩu"}
            </Button>
          </form>
        )}

        <p className="mt-6 text-center text-sm text-muted-foreground">
          <a href="/login" className="font-medium text-accent hover:text-accent-hover">Quay lại đăng nhập</a>
        </p>
      </div>
    </div>
  );
}
