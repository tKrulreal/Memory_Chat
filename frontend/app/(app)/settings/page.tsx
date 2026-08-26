"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Settings as SettingsIcon,
  Shield,
  MessageSquare,
  Lock,
  Sparkles,
  Bell,
  Palette,
  Info,
  CheckCircle2,
  AlertCircle,
  KeyRound,
  Eye,
  EyeOff,
  UserCheck,
  UserX,
  Smartphone,
  Trash2,
  Volume2,
  VolumeX,
  Globe,
  Brain,
  HardDrive,
  ExternalLink,
  ChevronRight,
  RefreshCw,
  LogOut,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  getSettings,
  updateSettings,
  changePassword,
  getBlockedUsers,
  unblockUser,
} from "@/lib/api/settings";
import { getMyProfile, updateMyProfile } from "@/lib/api/profile";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useRouter } from "next/navigation";
import type { Setting, BlockedUser } from "@/types";

type SettingTab =
  | "account"
  | "chat"
  | "privacy"
  | "ai"
  | "notifications"
  | "appearance"
  | "about";

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);

  const [activeTab, setActiveTab] = useState<SettingTab>("account");

  // Settings query
  const { data: settings, isLoading: isLoadingSettings } = useQuery({
    queryKey: ["my-settings"],
    queryFn: getSettings,
  });

  // Profile query (for user account details)
  const { data: profile, isLoading: isLoadingProfile } = useQuery({
    queryKey: ["my-profile"],
    queryFn: getMyProfile,
  });

  // Blocked users query
  const { data: blockedUsers = [], isLoading: isLoadingBlocked } = useQuery({
    queryKey: ["blocked-users"],
    queryFn: getBlockedUsers,
  });

  // Password change state
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrentPw, setShowCurrentPw] = useState(false);
  const [showNewPw, setShowNewPw] = useState(false);
  const [passwordError, setPasswordError] = useState("");
  const [passwordSuccess, setPasswordSuccess] = useState("");

  // Alert banner states
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  // Mutations
  const updateSettingsMutation = useMutation({
    mutationFn: (data: Partial<Setting>) => updateSettings(data),
    onSuccess: (newSettings) => {
      queryClient.setQueryData(["my-settings"], newSettings);
      showToast("Cài đặt đã được cập nhật thành công!");
    },
    onError: (err: any) => {
      showToast(err.message || "Không thể lưu cài đặt. Vui lòng thử lại.");
    },
  });

  const updateProfileMutation = useMutation({
    mutationFn: (payload: any) => updateMyProfile(payload),
    onSuccess: (data) => {
      queryClient.setQueryData(["my-profile"], data);
      showToast("Hồ sơ đã được cập nhật!");
    },
  });

  const changePwMutation = useMutation({
    mutationFn: () => changePassword(currentPassword, newPassword),
    onSuccess: (res) => {
      setPasswordSuccess(res.message || "Đổi mật khẩu thành công!");
      setPasswordError("");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setTimeout(() => setPasswordSuccess(""), 4000);
    },
    onError: (err: any) => {
      setPasswordError(err.message || "Đổi mật khẩu thất bại. Vui lòng kiểm tra lại mật khẩu cũ.");
      setPasswordSuccess("");
    },
  });

  const unblockMutation = useMutation({
    mutationFn: (targetId: string) => unblockUser(targetId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["blocked-users"] });
      showToast("Đã mở chặn người dùng thành công!");
    },
  });

  const handleToggleSetting = (key: keyof Setting, val: any) => {
    updateSettingsMutation.mutate({ [key]: val });
  };

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError("");
    setPasswordSuccess("");

    if (!currentPassword) {
      setPasswordError("Vui lòng nhập mật khẩu hiện tại.");
      return;
    }
    if (newPassword.length < 6) {
      setPasswordError("Mật khẩu mới phải có tối thiểu 6 ký tự.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError("Xác nhận mật khẩu mới không trùng khớp.");
      return;
    }

    changePwMutation.mutate();
  };

  const handleClearChatCache = () => {
    if (confirm("Bạn có chắc chắn muốn xóa bộ nhớ đệm và dữ liệu tạm cuộc trò chuyện trên thiết bị này?")) {
      try {
        localStorage.removeItem("chat_drafts");
        localStorage.removeItem("recent_emojis");
        showToast("Đã xóa bộ nhớ đệm ứng dụng thành công!");
      } catch {
        showToast("Không thể xóa bộ nhớ tạm.");
      }
    }
  };

  if (isLoadingSettings || isLoadingProfile) {
    return (
      <main className="flex-1 overflow-y-auto bg-slate-50 p-6 md:p-10">
        <div className="mx-auto max-w-5xl space-y-6">
          <Skeleton className="h-10 w-64 rounded-xl" />
          <Skeleton className="h-48 w-full rounded-2xl" />
          <Skeleton className="h-80 w-full rounded-2xl" />
        </div>
      </main>
    );
  }

  const TABS = [
    { id: "account", label: "Tài khoản & Bảo mật", icon: Shield },
    { id: "chat", label: "Trò chuyện & Media", icon: MessageSquare },
    { id: "privacy", label: "Quyền riêng tư", icon: Lock },
    { id: "ai", label: "Trí tuệ Nhân tạo & AI", icon: Sparkles },
    { id: "notifications", label: "Thông báo & Âm thanh", icon: Bell },
    { id: "appearance", label: "Giao diện & Ngôn ngữ", icon: Palette },
    { id: "about", label: "Về ứng dụng", icon: Info },
  ] as const;

  return (
    <main className="flex-1 overflow-y-auto bg-slate-50 p-6 md:p-10">
      <div className="mx-auto max-w-5xl space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2.5">
              <SettingsIcon className="h-7 w-7 text-blue-600" />
              Cài đặt Hệ thống (Settings)
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Quản lý tài khoản, trải nghiệm trò chuyện, quyền riêng tư và cấu hình AI trợ lý.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push("/profile")}
              className="flex items-center gap-1.5 rounded-xl shadow-xs"
            >
              <ExternalLink size={14} />
              Chỉnh sửa Hồ sơ cá nhân
            </Button>
          </div>
        </div>

        {/* Global Toast */}
        {toastMessage && (
          <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 rounded-2xl bg-slate-900 text-white px-5 py-3.5 shadow-xl border border-slate-700 animate-in fade-in slide-in-from-bottom-5">
            <CheckCircle2 size={18} className="text-green-400" />
            <span className="text-sm font-medium">{toastMessage}</span>
          </div>
        )}

        {/* Layout Grid: Sidebar Tabs + Content Panel */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
          {/* Navigation Sidebar */}
          <Card className="md:col-span-4 rounded-3xl border-slate-100 bg-white p-3 shadow-sm space-y-1">
            {TABS.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as SettingTab)}
                  className={`w-full flex items-center justify-between p-3.5 rounded-2xl text-sm font-semibold transition-all cursor-pointer ${
                    isActive
                      ? "bg-blue-600 text-white shadow-sm shadow-blue-500/20"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon size={18} className={isActive ? "text-white" : "text-slate-400"} />
                    <span>{tab.label}</span>
                  </div>
                  <ChevronRight size={15} className={isActive ? "text-white/80" : "text-slate-300"} />
                </button>
              );
            })}
          </Card>

          {/* Tab Content Panel */}
          <div className="md:col-span-8 space-y-6">
            {/* ================================================================= */}
            {/* TAB 1: TÀI KHOẢN & BẢO MẬT */}
            {/* ================================================================= */}
            {activeTab === "account" && (
              <div className="space-y-6">
                {/* Account Info Card */}
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-5 shadow-sm">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                    <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
                      <Shield size={18} className="text-blue-600" />
                      Thông tin Tài khoản
                    </h2>
                    <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200 text-xs">
                      Đang hoạt động
                    </Badge>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-xs text-slate-400 font-medium">Họ và tên</span>
                      <p className="font-semibold text-slate-800 mt-0.5">{user?.full_name || profile?.full_name || "Chưa đặt tên"}</p>
                    </div>
                    <div>
                      <span className="text-xs text-slate-400 font-medium">Email đăng nhập</span>
                      <p className="font-semibold text-slate-800 mt-0.5">{user?.email || profile?.email}</p>
                    </div>
                    <div>
                      <span className="text-xs text-slate-400 font-medium">Số điện thoại</span>
                      <p className="font-semibold text-slate-800 mt-0.5">{profile?.phone || "Chưa liên kết"}</p>
                    </div>
                    <div>
                      <span className="text-xs text-slate-400 font-medium">Chức danh / Vị trí</span>
                      <p className="font-semibold text-slate-800 mt-0.5">{profile?.profession || "Chưa cập nhật"}</p>
                    </div>
                  </div>

                  <div className="pt-2 flex justify-end">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => router.push("/profile")}
                      className="rounded-xl text-xs font-semibold"
                    >
                      Chỉnh sửa hồ sơ tại trang Profile →
                    </Button>
                  </div>
                </Card>

                {/* Change Password Card */}
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-5 shadow-sm">
                  <h2 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-4 flex items-center gap-2">
                    <KeyRound size={18} className="text-blue-600" />
                    Đổi Mật khẩu
                  </h2>

                  {passwordSuccess && (
                    <div className="flex items-center gap-2 rounded-xl bg-green-50 border border-green-200 p-3 text-xs text-green-700 font-medium">
                      <CheckCircle2 size={16} />
                      <span>{passwordSuccess}</span>
                    </div>
                  )}

                  {passwordError && (
                    <div className="flex items-center gap-2 rounded-xl bg-red-50 border border-red-200 p-3 text-xs text-red-700 font-medium">
                      <AlertCircle size={16} />
                      <span>{passwordError}</span>
                    </div>
                  )}

                  <form onSubmit={handlePasswordSubmit} className="space-y-4">
                    <div>
                      <label className="block text-xs font-medium text-slate-600 mb-1">
                        Mật khẩu hiện tại
                      </label>
                      <div className="relative">
                        <Input
                          type={showCurrentPw ? "text" : "password"}
                          value={currentPassword}
                          onChange={(e) => setCurrentPassword(e.target.value)}
                          placeholder="Nhập mật khẩu đang dùng"
                          className="bg-slate-50 pr-10"
                        />
                        <button
                          type="button"
                          onClick={() => setShowCurrentPw(!showCurrentPw)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                        >
                          {showCurrentPw ? <EyeOff size={16} /> : <Eye size={16} />}
                        </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-medium text-slate-600 mb-1">
                          Mật khẩu mới
                        </label>
                        <div className="relative">
                          <Input
                            type={showNewPw ? "text" : "password"}
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            placeholder="Tối thiểu 6 ký tự"
                            className="bg-slate-50 pr-10"
                          />
                          <button
                            type="button"
                            onClick={() => setShowNewPw(!showNewPw)}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                          >
                            {showNewPw ? <EyeOff size={16} /> : <Eye size={16} />}
                          </button>
                        </div>
                      </div>

                      <div>
                        <label className="block text-xs font-medium text-slate-600 mb-1">
                          Xác nhận mật khẩu mới
                        </label>
                        <Input
                          type={showNewPw ? "text" : "password"}
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                          placeholder="Nhập lại mật khẩu mới"
                          className="bg-slate-50"
                        />
                      </div>
                    </div>

                    <div className="flex justify-end pt-2">
                      <Button
                        type="submit"
                        disabled={changePwMutation.isPending || !currentPassword || !newPassword}
                        className="rounded-xl shadow-sm bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs px-5"
                      >
                        {changePwMutation.isPending ? "Đang xử lý..." : "Cập nhật Mật khẩu"}
                      </Button>
                    </div>
                  </form>
                </Card>

                {/* Active Sessions & Security Info */}
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-4 shadow-sm">
                  <h2 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-3 flex items-center gap-2">
                    <Smartphone size={18} className="text-blue-600" />
                    Phiên Đăng nhập & Thiết bị
                  </h2>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 border border-slate-100">
                      <div className="flex items-center gap-3">
                        <div className="h-9 w-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
                          💻
                        </div>
                        <div>
                          <p className="text-xs font-bold text-slate-800">Trình duyệt Hiện tại (Web Browser)</p>
                          <p className="text-[11px] text-slate-400">Đang trực tuyến • Địa chỉ IP mạng nội bộ</p>
                        </div>
                      </div>
                      <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200 text-[10px]">
                        Thiết bị này
                      </Badge>
                    </div>
                  </div>
                </Card>
              </div>
            )}

            {/* ================================================================= */}
            {/* TAB 2: TRÒ CHUYỆN & ĐA PHƯƠNG TIỆN */}
            {/* ================================================================= */}
            {activeTab === "chat" && (
              <div className="space-y-6">
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-6 shadow-sm">
                  <h2 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-4 flex items-center gap-2">
                    <MessageSquare size={18} className="text-blue-600" />
                    Hành vi Trò chuyện (Chat Behavior)
                  </h2>

                  {/* Enter to Send */}
                  <div className="flex items-center justify-between gap-4">
                    <div className="space-y-0.5">
                      <p className="text-sm font-semibold text-slate-800">Bấm phím Enter để gửi tin nhắn</p>
                      <p className="text-xs text-slate-400">
                        Khi bật: Bấm Enter để gửi ngay, Shift + Enter để xuống dòng mới.
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={settings?.enter_is_send !== false}
                        onChange={(e) => handleToggleSetting("enter_is_send", e.target.checked)}
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <hr className="border-slate-100" />

                  {/* Auto Download Media */}
                  <div className="flex items-center justify-between gap-4">
                    <div className="space-y-0.5">
                      <p className="text-sm font-semibold text-slate-800">Tự động tải phương tiện (Media)</p>
                      <p className="text-xs text-slate-400">
                        Tự động hiển thị trước và tải hình ảnh, tài liệu đính kèm trong phòng chat.
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={settings?.media_auto_download !== false}
                        onChange={(e) => handleToggleSetting("media_auto_download", e.target.checked)}
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <hr className="border-slate-100" />

                  {/* Font Size */}
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    <div className="space-y-0.5">
                      <p className="text-sm font-semibold text-slate-800">Cỡ chữ trong khung chat</p>
                      <p className="text-xs text-slate-400">Điều chỉnh kích thước hiển thị của bong bóng tin nhắn.</p>
                    </div>
                    <select
                      value={settings?.font_size || "medium"}
                      onChange={(e) => handleToggleSetting("font_size", e.target.value)}
                      className="h-9 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-700 focus:border-blue-500 focus:outline-none"
                    >
                      <option value="small">Nhỏ (13px)</option>
                      <option value="medium">Tiêu chuẩn (14px)</option>
                      <option value="large">Lớn (16px)</option>
                    </select>
                  </div>
                </Card>

                {/* Storage and Cache */}
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-4 shadow-sm">
                  <h2 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-3 flex items-center gap-2">
                    <HardDrive size={18} className="text-blue-600" />
                    Dữ liệu & Bộ nhớ tạm
                  </h2>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-slate-800">Xóa bộ nhớ đệm trò chuyện trên máy</p>
                      <p className="text-xs text-slate-400">
                        Giải phóng dung lượng bản nháp và bộ đệm tin nhắn cục bộ.
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleClearChatCache}
                      className="text-red-600 hover:bg-red-50 hover:border-red-200 rounded-xl text-xs"
                    >
                      <Trash2 size={14} className="mr-1" />
                      Xóa Cache
                    </Button>
                  </div>
                </Card>
              </div>
            )}

            {/* ================================================================= */}
            {/* TAB 3: QUYỀN RIÊNG TƯ & BẢO MẬT */}
            {/* ================================================================= */}
            {activeTab === "privacy" && (
              <div className="space-y-6">
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-6 shadow-sm">
                  <h2 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-4 flex items-center gap-2">
                    <Lock size={18} className="text-blue-600" />
                    Quyền Riêng tư & Hiển thị
                  </h2>

                  {/* Public Profile */}
                  <div className="flex items-center justify-between gap-4">
                    <div className="space-y-0.5">
                      <p className="text-sm font-semibold text-slate-800">Chế độ Công khai Hồ sơ (Public Profile)</p>
                      <p className="text-xs text-slate-400">
                        Cho phép người dùng khác tìm kiếm hồ sơ và gửi lời mời kết nối tới bạn.
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={profile?.is_public !== false}
                        onChange={(e) => updateProfileMutation.mutate({ is_public: e.target.checked })}
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                    </label>
                  </div>

                  <hr className="border-slate-100" />

                  {/* Read Receipts */}
                  <div className="flex items-center justify-between gap-4">
                    <div className="space-y-0.5">
                      <p className="text-sm font-semibold text-slate-800">Hiển thị trạng thái "Đã xem" (Read Receipts)</p>
                      <p className="text-xs text-slate-400">
                        Cho phép đối phương biết khi bạn đã đọc tin nhắn của họ.
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={settings?.read_receipts !== false}
                        onChange={(e) => handleToggleSetting("read_receipts", e.target.checked)}
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <hr className="border-slate-100" />

                  {/* Online Status */}
                  <div className="flex items-center justify-between gap-4">
                    <div className="space-y-0.5">
                      <p className="text-sm font-semibold text-slate-800">Trạng thái Hoạt động (Online Status)</p>
                      <p className="text-xs text-slate-400">
                        Hiển thị chấm xanh báo hiệu bạn đang trực tuyến hoặc vừa mới truy cập.
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={settings?.online_status !== false}
                        onChange={(e) => handleToggleSetting("online_status", e.target.checked)}
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </Card>

                {/* Blocked Users Card */}
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-4 shadow-sm">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
                      <UserX size={18} className="text-red-500" />
                      Danh sách Người dùng đã Chặn ({blockedUsers.length})
                    </h2>
                  </div>

                  {blockedUsers.length === 0 ? (
                    <p className="text-xs text-slate-400 py-3">Bạn chưa chặn người dùng nào.</p>
                  ) : (
                    <div className="space-y-2">
                      {blockedUsers.map((bu) => (
                        <div
                          key={bu.id}
                          className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 border border-slate-100 text-xs"
                        >
                          <div>
                            <p className="font-bold text-slate-800">{bu.full_name || bu.email}</p>
                            <p className="text-[11px] text-slate-400">{bu.email}</p>
                          </div>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => unblockMutation.mutate(bu.id)}
                            disabled={unblockMutation.isPending}
                            className="rounded-xl text-xs text-blue-600 hover:bg-blue-50"
                          >
                            Bỏ chặn
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </Card>
              </div>
            )}

            {/* ================================================================= */}
            {/* TAB 4: TRÍ TUỆ NHÂN TẠO & AI COPILOT */}
            {/* ================================================================= */}
            {activeTab === "ai" && (
              <div className="space-y-6">
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-6 shadow-sm">
                  <h2 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-4 flex items-center gap-2">
                    <Brain size={18} className="text-blue-600" />
                    Cấu hình Trí tuệ Nhân tạo (AI & Copilot)
                  </h2>

                  {/* Master AI Assistant Toggle */}
                  <div className="flex items-center justify-between gap-4 p-4 rounded-2xl bg-blue-50/60 border border-blue-100">
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-2">
                        <Sparkles size={16} className="text-blue-600" />
                        <p className="text-sm font-bold text-slate-800">Kích hoạt Trợ lý AI (Master AI Switch)</p>
                      </div>
                      <p className="text-xs text-slate-500">
                        Bật/tắt toàn bộ hệ sinh thái tính năng AI (Copilot, gợi ý tin nhắn, matchmaker, tagging).
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={settings?.ai_enabled !== false}
                        onChange={(e) => handleToggleSetting("ai_enabled", e.target.checked)}
                      />
                      <div className="w-12 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  {settings?.ai_enabled !== false && (
                    <>
                      <hr className="border-slate-100" />

                      {/* FEATURE REQUEST: TOGGLE CHO PHÉP AI TRÍCH XUẤT ĐOẠN CHAT */}
                      <div className="flex items-center justify-between gap-4 p-4 rounded-2xl bg-slate-50 border border-slate-200">
                        <div className="space-y-1 max-w-md">
                          <div className="flex items-center gap-2">
                            <MessageSquare size={16} className="text-blue-600" />
                            <p className="text-sm font-bold text-slate-800">
                              Cho phép AI trích xuất phân tích đoạn chat
                            </p>
                          </div>
                          <p className="text-xs text-slate-500 leading-relaxed">
                            {settings?.ai_extract_chat !== false
                              ? "BẬT: Trợ lý AI và Memory Worker sẽ phân tích nội dung cuộc hội thoại để tự động học hỏi thói quen, điểm quan tâm, thông tin liên lạc và hỗ trợ bạn tốt nhất."
                              : "TẮT (Bảo mật tối đa): AI sẽ bị khóa hoàn toàn quyền đọc và trích xuất tin nhắn chat của bạn."}
                          </p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer shrink-0">
                          <input
                            type="checkbox"
                            className="sr-only peer"
                            checked={settings?.ai_extract_chat !== false}
                            onChange={(e) => handleToggleSetting("ai_extract_chat", e.target.checked)}
                          />
                          <div className="w-12 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                      </div>

                      <hr className="border-slate-100" />

                      {/* Allow AI to Read Profile */}
                      <div className="flex items-center justify-between gap-4">
                        <div className="space-y-0.5">
                          <p className="text-sm font-semibold text-slate-800">Cho phép AI đọc Hồ sơ (Profile Matching)</p>
                          <p className="text-xs text-slate-400">
                            Cho phép thuật toán AI Matchmaker đọc kỹ năng, kinh nghiệm để gợi ý bạn bè và đối tác.
                          </p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            className="sr-only peer"
                            checked={settings?.ai_read_profile !== false}
                            onChange={(e) => handleToggleSetting("ai_read_profile", e.target.checked)}
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                      </div>

                      <hr className="border-slate-100" />

                      {/* Copilot Context Turns */}
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                        <div className="space-y-0.5">
                          <p className="text-sm font-semibold text-slate-800">Số tin nhắn ngữ cảnh Copilot</p>
                          <p className="text-xs text-slate-400">
                            Số lượng tin nhắn gần nhất AI Copilot tham khảo để trả lời chính xác.
                          </p>
                        </div>
                        <select
                          value={settings?.ai_copilot_context_turns ?? 10}
                          onChange={(e) => handleToggleSetting("ai_copilot_context_turns", parseInt(e.target.value))}
                          className="h-9 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-700 focus:border-blue-500 focus:outline-none"
                        >
                          <option value="5">5 tin nhắn gần nhất</option>
                          <option value="10">10 tin nhắn (Đề xuất)</option>
                          <option value="20">20 tin nhắn</option>
                          <option value="50">50 tin nhắn</option>
                          <option value="0">Toàn bộ cuộc trò chuyện</option>
                        </select>
                      </div>

                      <hr className="border-slate-100" />

                      {/* Memory Refresh Interval */}
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                        <div className="space-y-0.5">
                          <p className="text-sm font-semibold text-slate-800">Chu kỳ cập nhật Trí nhớ AI</p>
                          <p className="text-xs text-slate-400">Tần suất hệ thống tổng hợp thông tin quan trọng từ chat.</p>
                        </div>
                        <select
                          value={settings?.ai_memory_refresh_interval || "realtime"}
                          onChange={(e) => handleToggleSetting("ai_memory_refresh_interval", e.target.value)}
                          className="h-9 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-700 focus:border-blue-500 focus:outline-none"
                        >
                          <option value="realtime">Tức thì (Realtime)</option>
                          <option value="5_mins">Mỗi 5 phút sau khi chat</option>
                          <option value="hourly">Hàng giờ</option>
                          <option value="daily">Hàng ngày</option>
                        </select>
                      </div>
                    </>
                  )}
                </Card>
              </div>
            )}

            {/* ================================================================= */}
            {/* TAB 5: THÔNG BÁO & ÂM THANH */}
            {/* ================================================================= */}
            {activeTab === "notifications" && (
              <div className="space-y-6">
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-6 shadow-sm">
                  <h2 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-4 flex items-center gap-2">
                    <Bell size={18} className="text-blue-600" />
                    Thông báo & Âm báo (Notifications)
                  </h2>

                  {/* Push Notifications */}
                  <div className="flex items-center justify-between gap-4">
                    <div className="space-y-0.5">
                      <p className="text-sm font-semibold text-slate-800">Bật thông báo đẩy (Push Notifications)</p>
                      <p className="text-xs text-slate-400">
                        Nhận thông báo khi có tin nhắn mới, lời mời kết nối hoặc gợi ý AI.
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={settings?.notifications_enabled !== false && settings?.notification !== false}
                        onChange={(e) => handleToggleSetting("notifications_enabled", e.target.checked)}
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <hr className="border-slate-100" />

                  {/* Sound Alerts */}
                  <div className="flex items-center justify-between gap-4">
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-1.5">
                        {settings?.sound_enabled !== false ? <Volume2 size={16} className="text-blue-600" /> : <VolumeX size={16} className="text-slate-400" />}
                        <p className="text-sm font-semibold text-slate-800">Âm thanh Tin nhắn đến</p>
                      </div>
                      <p className="text-xs text-slate-400">Phát âm thanh thông báo chuông khi nhận được tin nhắn mới.</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={settings?.sound_enabled !== false}
                        onChange={(e) => handleToggleSetting("sound_enabled", e.target.checked)}
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <hr className="border-slate-100" />

                  {/* Message Preview */}
                  <div className="flex items-center justify-between gap-4">
                    <div className="space-y-0.5">
                      <p className="text-sm font-semibold text-slate-800">Hiển thị trước Nội dung tin nhắn</p>
                      <p className="text-xs text-slate-400">
                        Hiển thị tên người gửi và đoạn trích tin nhắn trong cửa sổ thông báo pop-up.
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={settings?.message_preview !== false}
                        onChange={(e) => handleToggleSetting("message_preview", e.target.checked)}
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </Card>
              </div>
            )}

            {/* ================================================================= */}
            {/* TAB 6: GIAO DIỆN & NGÔN NGỮ */}
            {/* ================================================================= */}
            {activeTab === "appearance" && (
              <div className="space-y-6">
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-6 shadow-sm">
                  <h2 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-4 flex items-center gap-2">
                    <Palette size={18} className="text-blue-600" />
                    Giao diện & Ngôn ngữ (Appearance)
                  </h2>

                  {/* Theme Selector */}
                  <div className="space-y-2">
                    <p className="text-sm font-semibold text-slate-800">Chế độ hiển thị (Theme Mode)</p>
                    <div className="grid grid-cols-3 gap-3 pt-1">
                      {[
                        { id: "light", label: "Sáng", icon: "☀️" },
                        { id: "dark", label: "Tối", icon: "🌙" },
                        { id: "system", label: "Hệ thống", icon: "💻" },
                      ].map((th) => (
                        <button
                          key={th.id}
                          type="button"
                          onClick={() => handleToggleSetting("theme", th.id)}
                          className={`flex flex-col items-center justify-center p-3.5 rounded-2xl border text-xs font-bold transition-all cursor-pointer ${
                            (settings?.theme || "system") === th.id
                              ? "border-blue-600 bg-blue-50 text-blue-700 shadow-xs"
                              : "border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100"
                          }`}
                        >
                          <span className="text-lg mb-1">{th.icon}</span>
                          <span>{th.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  <hr className="border-slate-100" />

                  {/* Accent Color */}
                  <div className="space-y-2">
                    <p className="text-sm font-semibold text-slate-800">Màu sắc chủ đạo (Accent Color)</p>
                    <div className="flex flex-wrap gap-2.5 pt-1">
                      {[
                        { id: "blue", label: "Xanh dương", color: "bg-blue-600" },
                        { id: "emerald", label: "Xanh lục", color: "bg-emerald-600" },
                        { id: "purple", label: "Tím", color: "bg-purple-600" },
                        { id: "indigo", label: "Chàm", color: "bg-indigo-600" },
                        { id: "amber", label: "Hổ phách", color: "bg-amber-600" },
                      ].map((col) => (
                        <button
                          key={col.id}
                          type="button"
                          onClick={() => handleToggleSetting("accent_color", col.id)}
                          className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
                            (settings?.accent_color || "blue") === col.id
                              ? "border-slate-800 bg-slate-900 text-white shadow-xs"
                              : "border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100"
                          }`}
                        >
                          <span className={`h-3 w-3 rounded-full ${col.color}`} />
                          <span>{col.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  <hr className="border-slate-100" />

                  {/* Language */}
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    <div className="space-y-0.5">
                      <p className="text-sm font-semibold text-slate-800">Ngôn ngữ hiển thị (Language)</p>
                      <p className="text-xs text-slate-400">Chọn ngôn ngữ cho toàn bộ ứng dụng.</p>
                    </div>
                    <select
                      value={settings?.language || "vi"}
                      onChange={(e) => handleToggleSetting("language", e.target.value)}
                      className="h-9 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-700 focus:border-blue-500 focus:outline-none"
                    >
                      <option value="vi">Tiếng Việt (Mặc định)</option>
                      <option value="en">English (US)</option>
                    </select>
                  </div>
                </Card>
              </div>
            )}

            {/* ================================================================= */}
            {/* TAB 7: VỀ ỨNG DỤNG */}
            {/* ================================================================= */}
            {activeTab === "about" && (
              <div className="space-y-6">
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-6 shadow-sm">
                  <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
                    <div className="h-12 w-12 rounded-2xl bg-blue-600 text-white flex items-center justify-center font-bold text-xl shadow-md">
                      M
                    </div>
                    <div>
                      <h2 className="text-base font-bold text-slate-800">MemoryChat App</h2>
                      <p className="text-xs text-slate-400">Nền tảng nhắn tin thông minh tích hợp Trợ lý AI Multi-Agent</p>
                    </div>
                  </div>

                  <div className="space-y-3 text-xs">
                    <div className="flex justify-between py-2 border-b border-slate-50">
                      <span className="text-slate-400">Phiên bản ứng dụng</span>
                      <span className="font-semibold text-slate-800">v2.2.0 (Stable Production)</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-slate-50">
                      <span className="text-slate-400">Kiến trúc AI</span>
                      <span className="font-semibold text-slate-800">LangGraph Multi-Agent + Vector Qdrant</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-slate-50">
                      <span className="text-slate-400">Cơ sở dữ liệu</span>
                      <span className="font-semibold text-slate-800">PostgreSQL (SQLAlchemy 2.0)</span>
                    </div>
                  </div>

                  <div className="pt-2 text-xs text-slate-400 leading-relaxed">
                    © 2026 MemoryChat Platform. Được thiết kế và bảo vệ theo tiêu chuẩn bảo mật dữ liệu người dùng.
                  </div>
                </Card>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
