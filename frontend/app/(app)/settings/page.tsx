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
  Sun,
  Moon,
  Monitor,
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
import { getLanguage, translate } from "@/lib/i18n";

type SettingTab =
  | "account"
  | "chat"
  | "privacy"
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
    onMutate: async (data) => {
      await queryClient.cancelQueries({ queryKey: ["my-settings"] });
      const previousSettings = queryClient.getQueryData<Setting>(["my-settings"]);
      queryClient.setQueryData<Setting>(["my-settings"], (current) =>
        current ? { ...current, ...data } : current,
      );
      return { previousSettings };
    },
    onSuccess: (newSettings) => {
      queryClient.setQueryData(["my-settings"], newSettings);
      showToast("Cài đặt đã được cập nhật thành công!");
    },
    onError: (err: any, _data, context) => {
      if (context?.previousSettings) queryClient.setQueryData(["my-settings"], context.previousSettings);
      queryClient.invalidateQueries({ queryKey: ["my-settings"] });
      showToast(err.message || "Không thể lưu cài đặt. Vui lòng thử lại.");
    },
  });

  const updateProfileMutation = useMutation({
    mutationFn: (payload: any) => updateMyProfile(payload),
    onMutate: async (payload) => {
      await queryClient.cancelQueries({ queryKey: ["my-profile"] });
      const previousProfile = queryClient.getQueryData(["my-profile"]);
      queryClient.setQueryData(["my-profile"], (current: any) =>
        current ? { ...current, ...payload } : current,
      );
      return { previousProfile };
    },
    onSuccess: (data) => {
      queryClient.setQueryData(["my-profile"], data);
      showToast("Hồ sơ đã được cập nhật!");
    },
    onError: (err: any, _data, context) => {
      if (context?.previousProfile) queryClient.setQueryData(["my-profile"], context.previousProfile);
      queryClient.invalidateQueries({ queryKey: ["my-profile"] });
      showToast(err.message || "Không thể cập nhật hồ sơ.");
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
      <main className="settings-page flex-1 overflow-y-auto bg-background p-6 md:p-10">
        <div className="mx-auto max-w-5xl space-y-6">
          <Skeleton className="h-10 w-64 rounded-xl" />
          <Skeleton className="h-48 w-full rounded-2xl" />
          <Skeleton className="h-80 w-full rounded-2xl" />
        </div>
      </main>
    );
  }

  const language = getLanguage(settings?.language);
  const t = (key: Parameters<typeof translate>[1]) => translate(language, key);
  const TABS = [
    { id: "account", label: t("accountSecurity"), icon: Shield },
    { id: "chat", label: t("chatsMedia"), icon: MessageSquare },
    { id: "privacy", label: t("privacy"), icon: Lock },
    { id: "notifications", label: t("notifications"), icon: Bell },
    { id: "appearance", label: t("appearance"), icon: Palette },
    { id: "about", label: t("about"), icon: Info },
  ] as const;

  return (
    <main className="settings-page flex-1 overflow-y-auto bg-background p-6 md:p-10">
      <div className="mx-auto max-w-5xl space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-4">
          <div>
            <h1 className="text-2xl font-bold text-foreground flex items-center gap-2.5">
              <SettingsIcon className="h-7 w-7 text-accent" />
              {t("settings")}
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              {t("settingsDescription")}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push("/ai-hub")}
              className="flex items-center gap-1.5 rounded-xl shadow-xs text-accent border-accent/30 hover:bg-accent/10"
            >
              <Sparkles size={14} />
              {t("configureAi")}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push("/profile")}
              className="flex items-center gap-1.5 rounded-xl shadow-xs"
            >
              <ExternalLink size={14} />
              {t("editProfile")}
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
          <Card className="md:col-span-4 rounded-3xl border-border bg-card p-3 shadow-sm space-y-1">
            {TABS.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as SettingTab)}
                  className={`w-full flex items-center justify-between p-3.5 rounded-2xl text-sm font-semibold transition-all cursor-pointer ${
                    isActive
                      ? "bg-accent text-accent-foreground shadow-sm shadow-accent/20"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon size={18} className={isActive ? "text-accent-foreground" : "text-muted-foreground"} />
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
                       {t("accountInfo")}
                    </h2>
                    <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200 text-xs">
                       {t("active")}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                    <div>
                       <span className="text-xs text-slate-400 font-medium">{t("fullName")}</span>
                       <p className="font-semibold text-slate-800 mt-0.5">{user?.full_name || profile?.full_name || t("unnamed")}</p>
                    </div>
                    <div>
                       <span className="text-xs text-slate-400 font-medium">{t("loginEmail")}</span>
                      <p className="font-semibold text-slate-800 mt-0.5">{user?.email || profile?.email}</p>
                    </div>
                    <div>
                       <span className="text-xs text-slate-400 font-medium">{t("phone")}</span>
                       <p className="font-semibold text-slate-800 mt-0.5">{profile?.phone || t("notLinked")}</p>
                    </div>
                    <div>
                       <span className="text-xs text-slate-400 font-medium">{t("profession")}</span>
                       <p className="font-semibold text-slate-800 mt-0.5">{profile?.profession || t("notUpdated")}</p>
                    </div>
                  </div>

                  <div className="pt-2 flex justify-end">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => router.push("/profile")}
                      className="rounded-xl text-xs font-semibold"
                    >
                       {t("editProfilePage")}
                    </Button>
                  </div>
                </Card>

                {/* Change Password Card */}
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-5 shadow-sm">
                  <h2 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-4 flex items-center gap-2">
                    <KeyRound size={18} className="text-blue-600" />
                     {t("changePassword")}
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
                         {t("currentPassword")}
                      </label>
                      <div className="relative">
                        <Input
                          type={showCurrentPw ? "text" : "password"}
                          value={currentPassword}
                          onChange={(e) => setCurrentPassword(e.target.value)}
                           placeholder={t("currentPasswordPlaceholder")}
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
                           {t("newPassword")}
                        </label>
                        <div className="relative">
                          <Input
                            type={showNewPw ? "text" : "password"}
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                             placeholder={t("minimumSix")}
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
                           {t("confirmPassword")}
                        </label>
                        <Input
                          type={showNewPw ? "text" : "password"}
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                           placeholder={t("confirmPasswordPlaceholder")}
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
                         {changePwMutation.isPending ? t("processing") : t("updatePassword")}
                      </Button>
                    </div>
                  </form>
                </Card>

                {/* Active Sessions & Security Info */}
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-4 shadow-sm">
                  <h2 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-3 flex items-center gap-2">
                    <Smartphone size={18} className="text-blue-600" />
                     {t("sessions")}
                  </h2>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 border border-slate-100">
                      <div className="flex items-center gap-3">
                        <div className="h-9 w-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
                          💻
                        </div>
                        <div>
                           <p className="text-xs font-bold text-slate-800">{t("currentBrowser")}</p>
                           <p className="text-[11px] text-slate-400">{t("onlineLocal")}</p>
                        </div>
                      </div>
                      <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200 text-[10px]">
                         {t("thisDevice")}
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
                     {t("chatBehavior")}
                  </h2>

                  {/* Enter to Send */}
                  <div className="flex items-center justify-between gap-4">
                    <div className="space-y-0.5">
                       <p className="text-sm font-semibold text-slate-800">{t("enterSend")}</p>
                      <p className="text-xs text-slate-400">
                         {t("enterHelp")}
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
                       <p className="text-sm font-semibold text-slate-800">{t("autoMedia")}</p>
                      <p className="text-xs text-slate-400">
                         {t("autoMediaHelp")}
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
                       <p className="text-sm font-semibold text-slate-800">{t("chatFont")}</p>
                       <p className="text-xs text-slate-400">{t("chatFontHelp")}</p>
                    </div>
                    <select
                      value={settings?.font_size || "medium"}
                      onChange={(e) => handleToggleSetting("font_size", e.target.value)}
                      className="h-9 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-700 focus:border-blue-500 focus:outline-none"
                    >
                       <option value="small">{t("small")}</option>
                       <option value="medium">{t("standard")}</option>
                       <option value="large">{t("large")}</option>
                    </select>
                  </div>
                </Card>

                {/* Storage and Cache */}
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-4 shadow-sm">
                  <h2 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-3 flex items-center gap-2">
                    <HardDrive size={18} className="text-blue-600" />
                     {t("storage")}
                  </h2>

                  <div className="flex items-center justify-between">
                    <div>
                       <p className="text-sm font-semibold text-slate-800">{t("clearLocalCache")}</p>
                      <p className="text-xs text-slate-400">
                         {t("clearCacheHelp")}
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleClearChatCache}
                      className="text-red-600 hover:bg-red-50 hover:border-red-200 rounded-xl text-xs"
                    >
                      <Trash2 size={14} className="mr-1" />
                       {t("clearCache")}
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
                <Card className="rounded-3xl border-border bg-card p-6 md:p-8 space-y-6 shadow-sm">
                  <h2 className="text-base font-bold text-foreground border-b border-border pb-4 flex items-center gap-2">
                    <Lock size={18} className="text-accent" />
                     {t("privacyVisibility")}
                  </h2>

                  {/* Public Profile */}
                  <div className="flex items-center justify-between gap-4">
                    <div className="space-y-0.5">
                       <p className="text-sm font-semibold text-foreground">{t("publicProfile")}</p>
                      <p className="text-xs text-muted-foreground">
                         {t("publicProfileHelp")}
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={profile?.is_public !== false}
                        onChange={(e) => updateProfileMutation.mutate({ is_public: e.target.checked })}
                      />
                      <div className="w-11 h-6 bg-muted peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-border after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent"></div>
                    </label>
                  </div>

                  <hr className="border-border" />

                  {/* Read Receipts */}
                  <div className="flex items-center justify-between gap-4">
                    <div className="space-y-0.5">
                       <p className="text-sm font-semibold text-foreground">{t("readReceipts")}</p>
                      <p className="text-xs text-muted-foreground">
                         {t("readReceiptsHelp")}
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={settings?.read_receipts !== false}
                        onChange={(e) => handleToggleSetting("read_receipts", e.target.checked)}
                      />
                      <div className="w-11 h-6 bg-muted peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-border after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent"></div>
                    </label>
                  </div>

                  <hr className="border-border" />

                  {/* Online Status */}
                  <div className="flex items-center justify-between gap-4">
                    <div className="space-y-0.5">
                       <p className="text-sm font-semibold text-foreground">{t("onlineStatus")}</p>
                      <p className="text-xs text-muted-foreground">
                         {t("onlineStatusHelp")}
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={settings?.online_status !== false}
                        onChange={(e) => handleToggleSetting("online_status", e.target.checked)}
                      />
                      <div className="w-11 h-6 bg-muted peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-border after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent"></div>
                    </label>
                  </div>
                </Card>

                {/* Blocked Users Card */}
                <Card className="rounded-3xl border-border bg-card p-6 md:p-8 space-y-4 shadow-sm">
                  <div className="flex items-center justify-between border-b border-border pb-3">
                    <h2 className="text-base font-bold text-foreground flex items-center gap-2">
                      <UserX size={18} className="text-red-500" />
                       {t("blockedUsers")} ({blockedUsers.length})
                    </h2>
                  </div>

                  {blockedUsers.length === 0 ? (
                     <p className="text-xs text-muted-foreground py-3">{t("noBlockedUsers")}</p>
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
                             {t("unblock")}
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </Card>
              </div>
            )}

            {/* ================================================================= */}
            {/* TAB 4: THÔNG BÁO & ÂM THANH */}
            {/* ================================================================= */}
            {activeTab === "notifications" && (
              <div className="space-y-6">
                <Card className="rounded-3xl border-border bg-card ring-0 p-6 md:p-8 space-y-6 shadow-sm">
                  <h2 className="text-base font-bold text-foreground border-b border-border pb-4 flex items-center gap-2">
                    <Bell size={18} className="text-accent" />
                     {t("notificationsTitle")}
                  </h2>

                  {/* Push Notifications */}
                  <div className="flex items-center justify-between gap-4">
                    <div className="space-y-0.5">
                       <p className="text-sm font-semibold text-foreground">{t("pushNotifications")}</p>
                      <p className="text-xs text-muted-foreground">
                         {t("pushHelp")}
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={settings?.notification !== false}
                        onChange={(e) => handleToggleSetting("notification", e.target.checked)}
                      />
                      <div className="w-11 h-6 bg-muted peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-border after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent"></div>
                    </label>
                  </div>

                  <hr className="border-border" />

                  {/* Sound Alerts */}
                  <div className="flex items-center justify-between gap-4">
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-1.5">
                          {settings?.sound_enabled !== false ? <Volume2 size={16} className="text-accent" /> : <VolumeX size={16} className="text-muted-foreground" />}
                           <p className="text-sm font-semibold text-foreground">{t("incomingSound")}</p>
                      </div>
                       <p className="text-xs text-muted-foreground">{t("soundHelp")}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={settings?.sound_enabled !== false}
                        onChange={(e) => handleToggleSetting("sound_enabled", e.target.checked)}
                      />
                      <div className="w-11 h-6 bg-muted peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-border after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent"></div>
                    </label>
                  </div>

                  <hr className="border-border" />

                  {/* Message Preview */}
                  <div className="flex items-center justify-between gap-4">
                    <div className="space-y-0.5">
                       <p className="text-sm font-semibold text-foreground">{t("messagePreview")}</p>
                      <p className="text-xs text-muted-foreground">
                         {t("previewHelp")}
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={settings?.message_preview !== false}
                        onChange={(e) => handleToggleSetting("message_preview", e.target.checked)}
                      />
                      <div className="w-11 h-6 bg-muted peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-border after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent"></div>
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
                <Card className="rounded-3xl border-border bg-card p-6 md:p-8 space-y-6 shadow-sm">
                  <h2 className="text-base font-bold text-foreground border-b border-border pb-4 flex items-center gap-2">
                    <Palette size={18} className="text-accent" />
                    {t("appearanceTitle")}
                  </h2>

                  {/* Theme Selector */}
                  <div className="space-y-2">
                    <p className="text-sm font-semibold text-foreground">{t("themeMode")}</p>
                    <div className="grid grid-cols-3 gap-3 pt-1">
                      {[
                        { id: "light", label: t("light"), icon: Sun },
                        { id: "dark", label: t("dark"), icon: Moon },
                        { id: "system", label: t("system"), icon: Monitor },
                      ].map((th) => (
                        <button
                          key={th.id}
                          type="button"
                          onClick={() => handleToggleSetting("theme", th.id)}
                          className={`flex flex-col items-center justify-center p-3.5 rounded-2xl border text-xs font-bold transition-all cursor-pointer ${
                            (settings?.theme || "system") === th.id
                              ? "border-accent bg-accent/10 text-accent shadow-xs"
                              : "border-border bg-muted text-muted-foreground hover:bg-accent/10"
                          }`}
                        >
                          <th.icon size={20} className="mb-1" aria-hidden="true" />
                          <span>{th.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  <hr className="border-border" />

                  {/* Accent Color */}
                  <div className="space-y-2">
                    <p className="text-sm font-semibold text-foreground">{t("accentColor")}</p>
                    <div className="flex flex-wrap gap-2.5 pt-1">
                      {[
                        { id: "blue", label: t("blue"), color: "#2563eb" },
                        { id: "emerald", label: t("emerald"), color: "#059669" },
                        { id: "purple", label: t("purple"), color: "#9333ea" },
                        { id: "indigo", label: t("indigo"), color: "#4f46e5" },
                        { id: "amber", label: t("amber"), color: "#d97706" },
                      ].map((col) => (
                        <button
                          key={col.id}
                          type="button"
                          onClick={() => handleToggleSetting("accent_color", col.id)}
                          className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
                            (settings?.accent_color || "blue") === col.id
                              ? "border-accent bg-accent text-accent-foreground shadow-xs"
                              : "border-border bg-muted text-foreground hover:bg-accent/10"
                          }`}
                        >
                          <span className="h-3 w-3 rounded-full" style={{ backgroundColor: col.color }} />
                          <span>{col.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  <hr className="border-border" />

                  {/* Language */}
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    <div className="space-y-0.5">
                      <p className="text-sm font-semibold text-foreground">{t("displayLanguage")}</p>
                      <p className="text-xs text-muted-foreground">{t("languageHelp")}</p>
                    </div>
                    <select
                      value={settings?.language || "vi"}
                      onChange={(e) => handleToggleSetting("language", e.target.value)}
                      className="h-9 rounded-xl border border-border bg-muted px-3 py-1 text-xs font-semibold text-foreground focus:border-ring focus:outline-none"
                    >
                      <option value="vi">{t("vietnamese")}</option>
                      <option value="en">{t("english")}</option>
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
                       <p className="text-xs text-slate-400">{t("appTagline")}</p>
                    </div>
                  </div>

                  <div className="space-y-3 text-xs">
                    <div className="flex justify-between py-2 border-b border-slate-50">
                       <span className="text-slate-400">{t("appVersion")}</span>
                      <span className="font-semibold text-slate-800">v2.2.0 (Stable Production)</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-slate-50">
                       <span className="text-slate-400">{t("aiArchitecture")}</span>
                      <span className="font-semibold text-slate-800">LangGraph Multi-Agent + Vector Qdrant</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-slate-50">
                       <span className="text-slate-400">{t("database")}</span>
                      <span className="font-semibold text-slate-800">PostgreSQL (SQLAlchemy 2.0)</span>
                    </div>
                  </div>

                  <div className="pt-2 text-xs text-slate-400 leading-relaxed">
                     {t("copyright")}
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
