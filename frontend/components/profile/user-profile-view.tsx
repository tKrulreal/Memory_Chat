"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  User,
  Briefcase,
  MapPin,
  Sparkles,
  MessageSquare,
  UserPlus,
  Clock,
  CheckCircle2,
  Globe,
  Github,
  Linkedin,
  GraduationCap,
  Lock,
  ArrowLeft,
  Mail,
  Phone,
  Shield,
  Loader2,
  ExternalLink,
} from "lucide-react";
import { getUserPublicProfile } from "@/lib/api/profile";
import { sendConnectionRequest, acceptConnectionRequest } from "@/lib/api/connection-requests";
import { createConversation } from "@/lib/api/conversations";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";

interface UserProfileViewProps {
  userId: string;
  isModal?: boolean;
  onClose?: () => void;
}

export function UserProfileView({ userId, isModal = false, onClose }: UserProfileViewProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const setActive = useConversationStore((s) => s.setActiveConversation);

  const { data: profile, isLoading, error } = useQuery({
    queryKey: ["public-profile", userId],
    queryFn: () => getUserPublicProfile(userId),
    enabled: !!userId,
  });

  const [isActionLoading, setIsActionLoading] = useState(false);

  const handleOpenChat = async () => {
    if (profile?.conversation_id) {
      setActive(profile.conversation_id);
      if (onClose) onClose();
      router.push("/chats");
      return;
    }

    // Try creating a conversation
    setIsActionLoading(true);
    try {
      const newConv = await createConversation(userId);
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      setActive(newConv.id);
      if (onClose) onClose();
      router.push("/chats");
    } catch (err: any) {
      toast.error(err?.message || "Không thể mở đoạn chat.");
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleSendFriendRequest = async () => {
    setIsActionLoading(true);
    try {
      await sendConnectionRequest(userId);
      queryClient.invalidateQueries({ queryKey: ["public-profile", userId] });
      queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
      toast.success(`Đã gửi lời mời kết bạn đến ${profile?.full_name || "người dùng"}`);
    } catch (err: any) {
      const msg = err?.message || "";
      if (msg.includes("409") || msg.toLowerCase().includes("already") || msg.toLowerCase().includes("conflict")) {
        queryClient.invalidateQueries({ queryKey: ["public-profile", userId] });
        toast.info("Bạn đã gửi lời mời kết bạn trước đó.");
      } else {
        toast.error(msg || "Không thể gửi lời mời kết bạn.");
      }
    } finally {
      setIsActionLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6 p-6 max-w-3xl mx-auto">
        <div className="flex items-center gap-4">
          <Skeleton className="h-20 w-20 rounded-full" />
          <div className="space-y-2">
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-32" />
          </div>
        </div>
        <Skeleton className="h-32 w-full rounded-2xl" />
        <Skeleton className="h-48 w-full rounded-2xl" />
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center">
        <Lock className="h-12 w-12 text-slate-300 mb-3" />
        <h2 className="text-lg font-bold text-slate-700">Không tìm thấy hồ sơ người dùng</h2>
        <p className="text-sm text-slate-400 mt-1">Người dùng này có thể không tồn tại hoặc đã bị xóa.</p>
        {!isModal && (
          <Button variant="outline" size="sm" onClick={() => router.back()} className="mt-4">
            <ArrowLeft size={14} className="mr-1" /> Quay lại
          </Button>
        )}
      </div>
    );
  }

  const initials = profile.full_name
    ? profile.full_name
        .split(" ")
        .map((n) => n[0])
        .slice(0, 2)
        .join("")
        .toUpperCase()
    : "MC";

  return (
    <div className="space-y-6 max-w-3xl mx-auto pb-10">
      {/* Top Header Card */}
      <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 shadow-sm relative overflow-hidden">
        {/* Background gradient banner */}
        <div className="absolute top-0 left-0 right-0 h-28 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 opacity-90"></div>

        <div className="relative pt-12 flex flex-col sm:flex-row items-start sm:items-end justify-between gap-4">
          {/* Avatar */}
          <div className="flex items-end gap-4">
            <div className="flex h-24 w-24 shrink-0 items-center justify-center rounded-3xl bg-white p-1 shadow-lg ring-4 ring-white">
              {profile.avatar ? (
                <img
                  src={profile.avatar}
                  alt={profile.full_name || "Avatar"}
                  className="h-full w-full rounded-2xl object-cover"
                />
              ) : (
                <div className="flex h-full w-full items-center justify-center rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 font-bold text-2xl text-white">
                  {initials}
                </div>
              )}
            </div>

            <div className="space-y-1">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-xl font-bold text-slate-900">{profile.full_name || profile.email}</h1>
                {profile.connection_status === "CONNECTED" && (
                  <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200 text-xs font-semibold">
                    ✓ Bạn bè
                  </Badge>
                )}
                {!profile.is_public && (
                  <Badge variant="outline" className="bg-slate-100 text-slate-600 border-slate-200 text-xs flex items-center gap-1">
                    <Lock size={10} /> Riêng tư
                  </Badge>
                )}
              </div>

              {(profile.profession || profile.company) && (
                <p className="text-sm font-medium text-slate-600 flex items-center gap-1.5 flex-wrap">
                  {profile.profession && <span>{profile.profession}</span>}
                  {profile.profession && profile.company && <span>•</span>}
                  {profile.company && <span className="text-slate-500">{profile.company}</span>}
                </p>
              )}

              {profile.location && (
                <p className="text-xs text-slate-400 flex items-center gap-1">
                  <MapPin size={12} className="text-blue-500" />
                  {profile.location}
                </p>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2 shrink-0 pt-2 sm:pt-0 w-full sm:w-auto">
            {profile.connection_status === "CONNECTED" ? (
              <Button
                variant="primary"
                size="default"
                onClick={handleOpenChat}
                disabled={isActionLoading}
                className="w-full sm:w-auto flex items-center justify-center gap-2 shadow-sm"
              >
                <MessageSquare size={16} />
                <span>Nhắn tin ngay</span>
              </Button>
            ) : profile.connection_status === "PENDING_SENT" ? (
              <Button
                variant="outline"
                size="default"
                disabled
                className="w-full sm:w-auto flex items-center justify-center gap-2 bg-slate-100 border-slate-200 text-slate-500 cursor-not-allowed"
              >
                <Clock size={16} />
                <span>Đã gửi lời mời</span>
              </Button>
            ) : (
              <Button
                variant="primary"
                size="default"
                onClick={handleSendFriendRequest}
                disabled={isActionLoading}
                className="w-full sm:w-auto flex items-center justify-center gap-2 shadow-sm bg-gradient-to-r from-blue-600 to-indigo-600 hover:opacity-95"
              >
                {isActionLoading ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    <span>Đang gửi...</span>
                  </>
                ) : (
                  <>
                    <UserPlus size={16} />
                    <span>Kết bạn</span>
                  </>
                )}
              </Button>
            )}
          </div>
        </div>

        {/* Social Links */}
        {(profile.github || profile.linkedin || profile.website || profile.email || profile.phone) && (
          <div className="mt-6 pt-5 border-t border-slate-100 flex flex-wrap items-center gap-4 text-xs text-slate-600">
            {profile.email && (
              <span className="flex items-center gap-1.5 text-slate-500">
                <Mail size={13} className="text-blue-500" />
                {profile.email}
              </span>
            )}
            {profile.phone && (
              <span className="flex items-center gap-1.5 text-slate-500">
                <Phone size={13} className="text-green-500" />
                {profile.phone}
              </span>
            )}
            {profile.github && (
              <a
                href={profile.github.startsWith("http") ? profile.github : `https://${profile.github}`}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1.5 text-slate-700 hover:text-blue-600 transition-colors"
              >
                <Github size={13} />
                <span>GitHub</span>
                <ExternalLink size={10} className="text-slate-400" />
              </a>
            )}
            {profile.linkedin && (
              <a
                href={profile.linkedin.startsWith("http") ? profile.linkedin : `https://${profile.linkedin}`}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1.5 text-blue-600 hover:underline"
              >
                <Linkedin size={13} />
                <span>LinkedIn</span>
                <ExternalLink size={10} className="text-slate-400" />
              </a>
            )}
            {profile.website && (
              <a
                href={profile.website.startsWith("http") ? profile.website : `https://${profile.website}`}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1.5 text-indigo-600 hover:underline"
              >
                <Globe size={13} />
                <span>Portfolio</span>
                <ExternalLink size={10} className="text-slate-400" />
              </a>
            )}
          </div>
        )}
      </Card>

      {/* Private Profile Notice */}
      {!profile.is_public && profile.connection_status !== "CONNECTED" && (
        <Card className="rounded-3xl border-amber-200/60 bg-amber-50/70 p-6 text-center space-y-2 shadow-sm">
          <Shield className="h-8 w-8 text-amber-600 mx-auto" />
          <h3 className="text-sm font-bold text-amber-900">Hồ sơ được đặt ở chế độ riêng tư</h3>
          <p className="text-xs text-amber-700 max-w-md mx-auto">
            Người dùng này đã tắt công khai hồ sơ. Bạn chỉ có thể xem đầy đủ kỹ năng, kinh nghiệm và học vấn sau khi kết nối bạn bè thành công.
          </p>
        </Card>
      )}

      {/* Public Profile Content */}
      {(profile.is_public || profile.connection_status === "CONNECTED") && (
        <>
          {/* Bio */}
          {profile.bio && (
            <Card className="rounded-3xl border-slate-100 bg-white p-6 shadow-sm space-y-3">
              <h2 className="text-sm font-bold text-slate-800 flex items-center gap-2">
                <User size={16} className="text-blue-600" />
                Giới thiệu bản thân
              </h2>
              <p className="text-xs font-normal text-slate-600 leading-relaxed whitespace-pre-wrap">
                {profile.bio}
              </p>
            </Card>
          )}

          {/* Skills & Interests */}
          {(profile.skills.length > 0 || profile.interests.length > 0) && (
            <Card className="rounded-3xl border-slate-100 bg-white p-6 shadow-sm space-y-5">
              <h2 className="text-sm font-bold text-slate-800 flex items-center gap-2">
                <Sparkles size={16} className="text-blue-600" />
                Kỹ năng & Mối quan tâm
              </h2>

              {profile.skills.length > 0 && (
                <div className="space-y-2">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Kỹ năng chuyên môn
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {profile.skills.map((skill, idx) => (
                      <span
                        key={idx}
                        className="rounded-full bg-blue-50 border border-blue-200 px-3 py-1 text-xs font-semibold text-blue-700 shadow-2xs"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {profile.interests.length > 0 && (
                <div className="space-y-2 pt-2 border-t border-slate-100">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Lĩnh vực quan tâm
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {profile.interests.map((interest, idx) => (
                      <span
                        key={idx}
                        className="rounded-full bg-slate-100 border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-700 shadow-2xs"
                      >
                        #{interest}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </Card>
          )}

          {/* Looking For & Offering */}
          {(profile.looking_for.length > 0 || profile.offering.length > 0) && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {profile.looking_for.length > 0 && (
                <Card className="rounded-3xl border-slate-100 bg-white p-6 shadow-sm space-y-3">
                  <h3 className="text-xs font-bold text-blue-700 flex items-center gap-2 uppercase tracking-wider">
                    🎯 Nhu cầu tìm kiếm (Looking for)
                  </h3>
                  <ul className="space-y-2">
                    {profile.looking_for.map((item, idx) => (
                      <li key={idx} className="rounded-xl bg-blue-50/70 border border-blue-100 p-2.5 text-xs text-blue-900 leading-relaxed">
                        • {item}
                      </li>
                    ))}
                  </ul>
                </Card>
              )}

              {profile.offering.length > 0 && (
                <Card className="rounded-3xl border-slate-100 bg-white p-6 shadow-sm space-y-3">
                  <h3 className="text-xs font-bold text-emerald-700 flex items-center gap-2 uppercase tracking-wider">
                    🤝 Giá trị chia sẻ (Offering)
                  </h3>
                  <ul className="space-y-2">
                    {profile.offering.map((item, idx) => (
                      <li key={idx} className="rounded-xl bg-emerald-50/70 border border-emerald-100 p-2.5 text-xs text-emerald-900 leading-relaxed">
                        • {item}
                      </li>
                    ))}
                  </ul>
                </Card>
              )}
            </div>
          )}

          {/* Experience Timeline */}
          {profile.experience && profile.experience.length > 0 && (
            <Card className="rounded-3xl border-slate-100 bg-white p-6 shadow-sm space-y-4">
              <h2 className="text-sm font-bold text-slate-800 flex items-center gap-2">
                <Briefcase size={16} className="text-blue-600" />
                Kinh nghiệm làm việc
              </h2>
              <div className="space-y-3 pl-2 border-l-2 border-slate-100">
                {profile.experience.map((exp, idx) => (
                  <div key={idx} className="relative pl-4 space-y-0.5">
                    <div className="absolute -left-[21px] top-1.5 h-2.5 w-2.5 rounded-full bg-blue-500 ring-4 ring-blue-100"></div>
                    <h4 className="text-xs font-bold text-slate-900">{exp.title}</h4>
                    <p className="text-xs text-slate-600 font-medium">{exp.company}</p>
                    {exp.period && <p className="text-[11px] text-slate-400">{exp.period}</p>}
                    {exp.description && <p className="text-xs text-slate-500 mt-1">{exp.description}</p>}
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Education Timeline */}
          {profile.education && profile.education.length > 0 && (
            <Card className="rounded-3xl border-slate-100 bg-white p-6 shadow-sm space-y-4">
              <h2 className="text-sm font-bold text-slate-800 flex items-center gap-2">
                <GraduationCap size={16} className="text-blue-600" />
                Học vấn & Bằng cấp
              </h2>
              <div className="space-y-3 pl-2 border-l-2 border-slate-100">
                {profile.education.map((edu, idx) => (
                  <div key={idx} className="relative pl-4 space-y-0.5">
                    <div className="absolute -left-[21px] top-1.5 h-2.5 w-2.5 rounded-full bg-indigo-500 ring-4 ring-indigo-100"></div>
                    <h4 className="text-xs font-bold text-slate-900">{edu.school}</h4>
                    {edu.degree && <p className="text-xs text-slate-600 font-medium">{edu.degree}</p>}
                    {edu.year && <p className="text-[11px] text-slate-400">Tốt nghiệp năm {edu.year}</p>}
                  </div>
                ))}
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
