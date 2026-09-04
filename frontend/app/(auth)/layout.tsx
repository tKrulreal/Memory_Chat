import React from "react";
import { Brain, Tag, Search, MessageSquare } from "lucide-react";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="h-screen w-full overflow-y-auto overflow-x-hidden bg-[#fafbfc] text-slate-900">
      <div className="min-h-full w-full flex flex-col lg:flex-row">
        {/* Left Column: Brand Hero */}
        <div className="flex-1 flex flex-col justify-between px-8 py-10 sm:px-12 sm:py-12 lg:px-16 lg:py-16 xl:px-24 bg-white/70 border-b lg:border-b-0 lg:border-r border-slate-100">
          {/* Top: Logo */}
          <div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-blue-600 flex items-center justify-center shadow-md shadow-blue-500/20">
                <svg
                  width="22"
                  height="22"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  className="text-white"
                >
                  <path
                    d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z"
                    fill="currentColor"
                  />
                  <circle cx="8" cy="10" r="1.5" fill="#2563eb" />
                  <circle cx="12" cy="10" r="1.5" fill="#2563eb" />
                  <circle cx="16" cy="10" r="1.5" fill="#2563eb" />
                </svg>
              </div>
              <div className="flex items-baseline tracking-tight">
                <span className="text-2xl font-bold text-slate-900">Memory</span>
                <span className="text-2xl font-bold text-blue-600">Chat</span>
              </div>
            </div>

            {/* Headline */}
            <div className="mt-12 sm:mt-16 lg:mt-20 max-w-xl">
              <h1 className="text-4xl sm:text-5xl xl:text-[54px] font-extrabold text-slate-900 tracking-tight leading-[1.12]">
                Your conversations <br />
                <span className="text-blue-600">remember</span> for you.
              </h1>
              <p className="mt-5 text-base sm:text-lg text-slate-500 leading-relaxed max-w-lg">
                AI hỗ trợ ghi nhớ, trích xuất và tìm kiếm thông tin quan trọng từ mọi cuộc trò chuyện.
              </p>

              {/* Feature Badges */}
              <div className="mt-10 sm:mt-12 space-y-6 sm:space-y-7">
                {/* Feature 1: AI Copilot */}
                <div className="flex items-start gap-4 sm:gap-5">
                  <div className="w-12 h-12 rounded-2xl bg-blue-50/90 border border-blue-100 flex items-center justify-center shrink-0 text-blue-600 shadow-sm shadow-blue-500/5">
                    <Brain className="w-6 h-6 stroke-[1.8]" />
                  </div>
                  <div>
                    <h2 className="text-base font-bold text-slate-900">AI Copilot</h2>
                    <p className="text-sm text-slate-500 mt-0.5">
                      Trợ lý AI thông minh, hiểu ngữ cảnh cuộc trò chuyện.
                    </p>
                  </div>
                </div>

                {/* Feature 2: Auto Tagging */}
                <div className="flex items-start gap-4 sm:gap-5">
                  <div className="w-12 h-12 rounded-2xl bg-blue-50/90 border border-blue-100 flex items-center justify-center shrink-0 text-blue-600 shadow-sm shadow-blue-500/5">
                    <Tag className="w-6 h-6 stroke-[1.8]" />
                  </div>
                  <div>
                    <h2 className="text-base font-bold text-slate-900">Auto Tagging</h2>
                    <p className="text-sm text-slate-500 mt-0.5">
                      Tự động gắn thẻ và tổ chức thông tin quan trọng.
                    </p>
                  </div>
                </div>

                {/* Feature 3: Smart Search */}
                <div className="flex items-start gap-4 sm:gap-5">
                  <div className="w-12 h-12 rounded-2xl bg-blue-50/90 border border-blue-100 flex items-center justify-center shrink-0 text-blue-600 shadow-sm shadow-blue-500/5">
                    <Search className="w-6 h-6 stroke-[1.8]" />
                  </div>
                  <div>
                    <h2 className="text-base font-bold text-slate-900">Smart Search</h2>
                    <p className="text-sm text-slate-500 mt-0.5">
                      Tìm kiếm nhanh chóng, chính xác trong trí nhớ.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Footer Note */}
          <div className="mt-12 pt-6">
            <p className="text-sm text-slate-400">
              Built for teams who value{" "}
              <span className="text-blue-600 font-semibold">context</span>.
            </p>
          </div>
        </div>

        {/* Right Column: Floating Auth Card & Orbital Ambient Background */}
        <div className="flex-1 relative flex items-center justify-center px-4 py-12 sm:px-8 lg:px-12 bg-gradient-to-br from-[#fafbfc] via-[#eff6ff]/35 to-[#e0e7ff]/30 overflow-hidden">
          {/* Ambient Glows */}
          <div className="pointer-events-none absolute -right-16 top-1/3 w-[500px] h-[500px] rounded-full bg-blue-200/35 blur-[100px]" />
          <div className="pointer-events-none absolute right-0 bottom-0 w-[400px] h-[400px] rounded-full bg-indigo-100/40 blur-[80px]" />

          {/* Decorative Orbital Dashed Lines & Floating Ghost Badges */}
          <div className="pointer-events-none absolute inset-0 hidden xl:block">
            <svg
              className="absolute inset-0 w-full h-full"
              viewBox="0 0 600 700"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              preserveAspectRatio="none"
            >
              {/* Curve 1: to top-right badge */}
              <path
                d="M 280 300 C 380 260, 480 180, 550 140"
                stroke="#cbd5e1"
                strokeWidth="1.5"
                strokeDasharray="4 6"
                strokeLinecap="round"
                className="opacity-70"
              />
              {/* Curve 2: to middle-right badge */}
              <path
                d="M 310 370 C 400 365, 480 360, 560 355"
                stroke="#cbd5e1"
                strokeWidth="1.5"
                strokeDasharray="4 6"
                strokeLinecap="round"
                className="opacity-70"
              />
              {/* Curve 3: to bottom-right badge */}
              <path
                d="M 290 440 C 380 470, 470 540, 545 610"
                stroke="#cbd5e1"
                strokeWidth="1.5"
                strokeDasharray="4 6"
                strokeLinecap="round"
                className="opacity-70"
              />
            </svg>

            {/* Ghost Badge 1 (Top right - Message) */}
            <div className="absolute top-[115px] right-[40px] w-12 h-12 rounded-full border border-slate-200/80 bg-white/80 backdrop-blur-sm shadow-sm flex items-center justify-center text-slate-400">
              <MessageSquare className="w-5 h-5 stroke-[1.6]" />
            </div>

            {/* Ghost Badge 2 (Middle right - Tag) */}
            <div className="absolute top-[330px] right-[30px] w-12 h-12 rounded-full border border-slate-200/80 bg-white/80 backdrop-blur-sm shadow-sm flex items-center justify-center text-slate-400">
              <Tag className="w-5 h-5 stroke-[1.6]" />
            </div>

            {/* Ghost Badge 3 (Bottom right - Search) */}
            <div className="absolute bottom-[75px] right-[45px] w-12 h-12 rounded-full border border-slate-200/80 bg-white/80 backdrop-blur-sm shadow-sm flex items-center justify-center text-slate-400">
              <Search className="w-5 h-5 stroke-[1.6]" />
            </div>
          </div>

          {/* Auth Card Container */}
          <div className="relative z-10 w-full max-w-[440px]">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
