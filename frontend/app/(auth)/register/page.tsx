"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

export default function RegisterPage() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirmation, setPasswordConfirmation] = useState("");
  const [phone, setPhone] = useState("");
  const [gender, setGender] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    if (password !== passwordConfirmation) {
      setError("Mật khẩu xác nhận không khớp");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          password,
          full_name: fullName,
          gender: gender || undefined,
          phone: phone || undefined,
        }),
      });

      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.error ?? "Registration failed");
      }

      window.location.href = "/login";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-md rounded-button border border-subtle bg-card p-8">
        <div className="mb-8 text-center">
          <p className="text-sm font-semibold text-accent">MemoryChat</p>
          <h1 className="mt-2 text-2xl font-bold">Tạo tài khoản</h1>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="fullName" className="mb-1 block text-sm text-muted-foreground">
              Họ và tên
            </label>
            <input
              id="fullName"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="h-11 w-full rounded-button bg-input px-3 text-sm outline-none ring-accent focus:ring-1"
            />
          </div>
          <div>
            <label htmlFor="email" className="mb-1 block text-sm text-muted-foreground">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="h-11 w-full rounded-button bg-input px-3 text-sm outline-none ring-accent focus:ring-1"
            />
          </div>
          <div>
            <label htmlFor="password" className="mb-1 block text-sm text-muted-foreground">
              Mật khẩu
            </label>
            <input
              id="password"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="h-11 w-full rounded-button bg-input px-3 text-sm outline-none ring-accent focus:ring-1"
            />
          </div>
          <div>
            <label htmlFor="passwordConfirmation" className="mb-1 block text-sm text-muted-foreground">
              Nhập lại mật khẩu
            </label>
            <input
              id="passwordConfirmation"
              type="password"
              required
              minLength={8}
              autoComplete="new-password"
              value={passwordConfirmation}
              onChange={(e) => setPasswordConfirmation(e.target.value)}
              className="h-11 w-full rounded-button bg-input px-3 text-sm outline-none ring-accent focus:ring-1"
            />
          </div>
          <div>
            <label htmlFor="phone" className="mb-1 block text-sm text-muted-foreground">
              Số điện thoại (không bắt buộc)
            </label>
            <input
              id="phone"
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="h-11 w-full rounded-button bg-input px-3 text-sm outline-none ring-accent focus:ring-1"
            />
          </div>
          <div>
            <label htmlFor="gender" className="mb-1 block text-sm text-muted-foreground">
              Giới tính (không bắt buộc)
            </label>
            <select
              id="gender"
              value={gender}
              onChange={(e) => setGender(e.target.value)}
              className="h-11 w-full rounded-button bg-input px-3 text-sm outline-none ring-accent focus:ring-1"
            >
              <option value="">Chọn giới tính</option>
              <option value="male">Nam</option>
              <option value="female">Nữ</option>
              <option value="other">Khác</option>
            </select>
          </div>

          {error && <p className="text-sm text-red-400">{error}</p>}

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Đang tạo tài khoản..." : "Tạo tài khoản"}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          Đã có tài khoản?{" "}
          <a href="/login" className="text-accent hover:underline">
            Đăng nhập
          </a>
        </p>
      </div>
    </div>
  );
}
