"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  User,
  Briefcase,
  MapPin,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Plus,
  X,
  Save,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { getMyProfile, updateMyProfile, ProfileUpdatePayload } from "@/lib/api/profile";
import { generateConnections } from "@/lib/api/recommendations";
import { useRouter } from "next/navigation";


export default function SettingsPage() {
  const queryClient = useQueryClient();
  const router = useRouter();

  const { data: profile, isLoading, error } = useQuery({
    queryKey: ["my-profile"],
    queryFn: getMyProfile,
  });

  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [gender, setGender] = useState("");
  const [profession, setProfession] = useState("");
  const [company, setCompany] = useState("");
  const [location, setLocation] = useState("");
  const [skills, setSkills] = useState<string[]>([]);
  const [skillInput, setSkillInput] = useState("");
  const [interests, setInterests] = useState<string[]>([]);
  const [interestInput, setInterestInput] = useState("");
  const [lookingFor, setLookingFor] = useState<string[]>([]);
  const [needInput, setNeedInput] = useState("");
  const [offering, setOffering] = useState<string[]>([]);
  const [offerInput, setOfferInput] = useState("");
  const [bio, setBio] = useState("");
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (profile) {
      setFullName(profile.full_name || "");
      setPhone(profile.phone || "");
      setGender(profile.gender || "");
      setProfession(profile.profession || "");
      setCompany(profile.company || "");
      setLocation(profile.location || "");
      setSkills(profile.skills || []);
      setInterests(profile.interests || []);
      setLookingFor(profile.looking_for || []);
      setOffering(profile.offering || []);
      setBio(profile.bio || "");
    }
  }, [profile]);

  const updateMutation = useMutation({
    mutationFn: (payload: ProfileUpdatePayload) => updateMyProfile(payload),
    onSuccess: (data) => {
      queryClient.setQueryData(["my-profile"], data);
      queryClient.invalidateQueries({ queryKey: ["connection-recommendations"] });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 4000);
    },
  });

  const generateMutation = useMutation({
    mutationFn: () => generateConnections(),
    onSuccess: () => {

      queryClient.invalidateQueries({ queryKey: ["connection-recommendations"] });
      router.push("/recommendations");
    },
  });

  const handleAddSkill = () => {
    const val = skillInput.trim();
    if (val && !skills.includes(val)) {
      setSkills([...skills, val]);
      setSkillInput("");
    }
  };

  const handleRemoveSkill = (s: string) => {
    setSkills(skills.filter((item) => item !== s));
  };

  const handleAddInterest = () => {
    const val = interestInput.trim();
    if (val && !interests.includes(val)) {
      setInterests([...interests, val]);
      setInterestInput("");
    }
  };

  const handleRemoveInterest = (i: string) => {
    setInterests(interests.filter((item) => item !== i));
  };

  const handleAddNeed = () => {
    const val = needInput.trim();
    if (val && !lookingFor.includes(val)) {
      setLookingFor([...lookingFor, val]);
      setNeedInput("");
    }
  };

  const handleRemoveNeed = (n: string) => {
    setLookingFor(lookingFor.filter((item) => item !== n));
  };

  const handleAddOffer = () => {
    const val = offerInput.trim();
    if (val && !offering.includes(val)) {
      setOffering([...offering, val]);
      setOfferInput("");
    }
  };

  const handleRemoveOffer = (o: string) => {
    setOffering(offering.filter((item) => item !== o));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate({
      full_name: fullName.trim() || null,
      phone: phone.trim() || null,
      gender: gender || null,
      profession: profession.trim() || null,
      company: company.trim() || null,
      location: location.trim() || null,
      skills,
      interests,
      looking_for: lookingFor,
      offering,
      bio: bio.trim() || null,
    });
  };

  if (isLoading) {
    return (
      <main className="flex-1 overflow-y-auto bg-app p-6 md:p-10">
        <div className="mx-auto max-w-4xl space-y-6">
          <Skeleton className="h-10 w-64 rounded-card" />
          <Skeleton className="h-40 w-full rounded-card" />
          <Skeleton className="h-96 w-full rounded-card" />
        </div>
      </main>
    );
  }

  return (
    <main className="flex-1 overflow-y-auto bg-app p-6 md:p-10">
      <div className="mx-auto max-w-4xl space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-primary flex items-center gap-2">
              <User className="h-7 w-7 text-accent" />
              Hồ sơ & Tiêu chí Kết nối AI
            </h1>
            <p className="text-sm text-secondary mt-1">
              Nhập trực tiếp các thông tin của bạn để AI Matchmaker ưu tiên so khớp với những đối tác phù hợp nhất.
            </p>
          </div>

          <Button
            variant="secondary"
            size="sm"
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="flex items-center gap-1.5 shrink-0"
          >
            <Sparkles size={15} className="text-accent" />
            {generateMutation.isPending ? "Đang quét AI..." : "Quét gợi ý kết nối mới"}
          </Button>
        </div>

        {/* Priority Explanation Banner */}
        <div className="rounded-card border border-subtle bg-surface p-4.5 space-y-2">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2 text-sm font-semibold text-primary">
              <ShieldCheck className="h-5 w-5 text-accent" />
              <span>Trạng thái nguồn dữ liệu hiện tại:</span>
            </div>
            {profile?.is_custom_profile ? (
              <span className="rounded-full bg-accent/20 border border-accent/40 px-3 py-1 text-xs font-semibold text-accent">
                ✓ Đang ưu tiên: Dữ liệu bạn tự nhập
              </span>
            ) : (
              <span className="rounded-full bg-blue-500/20 border border-blue-500/40 px-3 py-1 text-xs font-semibold text-blue-400">
                🤖 Đang tự động trích xuất từ đoạn chat
              </span>
            )}
          </div>
          <p className="text-xs text-secondary leading-relaxed">
            <strong>Quy tắc ưu tiên của AI Matchmaker:</strong> Khi bạn nhập thông tin ở biểu mẫu bên dưới, hệ thống sẽ <strong>lưu vào bảng hồ sơ riêng và ưu tiên 100% dữ liệu này</strong> để so sánh. Nếu trường nào bạn để trống, hệ thống sẽ tự động sử dụng thông tin trích xuất được từ nội dung hội thoại thực tế của bạn.
          </p>
        </div>

        {/* Success Alert */}
        {saveSuccess && (
          <div className="flex items-center gap-2.5 rounded-card border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-400">
            <CheckCircle2 size={18} />
            <span>Hồ sơ đã được lưu thành công vào cơ sở dữ liệu! AI Matchmaker sẽ ưu tiên dữ liệu này khi tìm kiếm người phù hợp.</span>
          </div>
        )}

        {/* Error Alert */}
        {updateMutation.isError && (
          <div className="flex items-center gap-2.5 rounded-card border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
            <AlertCircle size={18} />
            <span>{updateMutation.error?.message || "Có lỗi xảy ra khi lưu hồ sơ."}</span>
          </div>
        )}

        {/* Main Profile Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Card: Basic Identity */}
          <div className="rounded-card border border-subtle bg-surface p-6 space-y-4">
            <h2 className="text-base font-semibold text-primary border-b border-subtle pb-2 flex items-center gap-2">
              <Briefcase size={18} className="text-accent" />
              Thông tin Công việc & Địa điểm
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-secondary mb-1">
                  Họ và tên
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Ví dụ: Nguyễn Hoàng Long"
                  className="w-full rounded-button border border-subtle bg-elevated px-3 py-2 text-sm text-primary placeholder:text-secondary/50 focus:border-accent focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-secondary mb-1">
                  Email (Không đổi)
                </label>
                <input
                  type="email"
                  value={profile?.email || ""}
                  disabled
                  className="w-full rounded-button border border-subtle bg-elevated/40 px-3 py-2 text-sm text-secondary/70 cursor-not-allowed"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-secondary mb-1">
                  Số điện thoại
                </label>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="Ví dụ: 0912345678"
                  className="w-full rounded-button border border-subtle bg-elevated px-3 py-2 text-sm text-primary placeholder:text-secondary/50 focus:border-accent focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-secondary mb-1">
                  Giới tính
                </label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                  className="w-full rounded-button border border-subtle bg-elevated px-3 py-2 text-sm text-primary focus:border-accent focus:outline-none"
                >
                  <option value="">Chọn giới tính</option>
                  <option value="male">Nam</option>
                  <option value="female">Nữ</option>
                  <option value="other">Khác</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-secondary mb-1">
                  Chức danh / Nghề nghiệp chính (Profession)
                </label>
                <input
                  type="text"
                  value={profession}
                  onChange={(e) => setProfession(e.target.value)}
                  placeholder="Ví dụ: Senior AI / LLM Engineer, Tech Product Lead..."
                  className="w-full rounded-button border border-subtle bg-elevated px-3 py-2 text-sm text-primary placeholder:text-secondary/50 focus:border-accent focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-secondary mb-1">
                  Công ty / Tổ chức (Company)
                </label>
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  placeholder="Ví dụ: VinAI Research, NextGen Innovation..."
                  className="w-full rounded-button border border-subtle bg-elevated px-3 py-2 text-sm text-primary placeholder:text-secondary/50 focus:border-accent focus:outline-none"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-xs font-medium text-secondary mb-1 flex items-center gap-1">
                  <MapPin size={12} className="text-accent" />
                  Địa điểm / Khu vực sinh sống (Location)
                </label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="Ví dụ: Hà Nội, TP. Hồ Chí Minh, Đà Nẵng..."
                  className="w-full rounded-button border border-subtle bg-elevated px-3 py-2 text-sm text-primary placeholder:text-secondary/50 focus:border-accent focus:outline-none"
                />
              </div>
            </div>
          </div>

          {/* Card: Skills & Interests */}
          <div className="rounded-card border border-subtle bg-surface p-6 space-y-5">
            <h2 className="text-base font-semibold text-primary border-b border-subtle pb-2 flex items-center gap-2">
              <Sparkles size={18} className="text-accent" />
              Kỹ năng & Mối quan tâm chuyên môn
            </h2>

            {/* Skills */}
            <div className="space-y-2">
              <label className="block text-xs font-medium text-secondary">
                Kỹ năng chuyên môn (Skills)
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={skillInput}
                  onChange={(e) => setSkillInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      handleAddSkill();
                    }
                  }}
                  placeholder="Nhập kỹ năng rồi bấm Thêm (ví dụ: Python, PyTorch, RAG, Flutter...)"
                  className="flex-1 rounded-button border border-subtle bg-elevated px-3 py-2 text-sm text-primary placeholder:text-secondary/50 focus:border-accent focus:outline-none"
                />
                <Button type="button" variant="secondary" size="sm" onClick={handleAddSkill}>
                  <Plus size={14} className="mr-1" /> Thêm
                </Button>
              </div>

              {skills.length > 0 && (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {skills.map((s, idx) => (
                    <span
                      key={idx}
                      className="flex items-center gap-1 rounded-full bg-elevated border border-subtle px-2.5 py-1 text-xs text-accent"
                    >
                      {s}
                      <button
                        type="button"
                        onClick={() => handleRemoveSkill(s)}
                        className="hover:text-red-400 text-secondary"
                      >
                        <X size={12} />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Interests */}
            <div className="space-y-2">
              <label className="block text-xs font-medium text-secondary">
                Lĩnh vực / Mối quan tâm (Interests)
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={interestInput}
                  onChange={(e) => setInterestInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      handleAddInterest();
                    }
                  }}
                  placeholder="Nhập chủ đề quan tâm (ví dụ: Generative AI, EdTech, Startups...)"
                  className="flex-1 rounded-button border border-subtle bg-elevated px-3 py-2 text-sm text-primary placeholder:text-secondary/50 focus:border-accent focus:outline-none"
                />
                <Button type="button" variant="secondary" size="sm" onClick={handleAddInterest}>
                  <Plus size={14} className="mr-1" /> Thêm
                </Button>
              </div>

              {interests.length > 0 && (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {interests.map((i, idx) => (
                    <span
                      key={idx}
                      className="flex items-center gap-1 rounded-full bg-elevated/70 border border-subtle px-2.5 py-1 text-xs text-blue-300"
                    >
                      #{i}
                      <button
                        type="button"
                        onClick={() => handleRemoveInterest(i)}
                        className="hover:text-red-400 text-secondary"
                      >
                        <X size={12} />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Card: Looking for & Offering Matrix */}
          <div className="rounded-card border border-subtle bg-surface p-6 space-y-5">
            <h2 className="text-base font-semibold text-primary border-b border-subtle pb-2 flex items-center gap-2">
              <ArrowRight size={18} className="text-accent" />
              Nhu cầu Tìm kiếm & Giá trị Chia sẻ
            </h2>

            {/* Looking For */}
            <div className="space-y-2">
              <label className="block text-xs font-medium text-blue-400">
                Looking for — Nhu cầu bạn đang tìm kiếm (Dự án, đối tác, tuyển dụng...)
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={needInput}
                  onChange={(e) => setNeedInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      handleAddNeed();
                    }
                  }}
                  placeholder="Ví dụ: Tìm Senior AI Engineer tư vấn hệ thống RAG..."
                  className="flex-1 rounded-button border border-subtle bg-elevated px-3 py-2 text-sm text-primary placeholder:text-secondary/50 focus:border-accent focus:outline-none"
                />
                <Button type="button" variant="secondary" size="sm" onClick={handleAddNeed}>
                  <Plus size={14} className="mr-1" /> Thêm
                </Button>
              </div>

              {lookingFor.length > 0 && (
                <ul className="space-y-1.5 pt-1">
                  {lookingFor.map((need, idx) => (
                    <li
                      key={idx}
                      className="flex items-center justify-between rounded-button bg-blue-500/10 border border-blue-500/20 px-3 py-1.5 text-xs text-blue-200"
                    >
                      <span>• {need}</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveNeed(need)}
                        className="hover:text-red-400 text-blue-300 ml-2"
                      >
                        <X size={13} />
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Offering */}
            <div className="space-y-2">
              <label className="block text-xs font-medium text-emerald-400">
                Offering — Giá trị / Kinh nghiệm bạn có thể chia sẻ, hỗ trợ đối phương
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={offerInput}
                  onChange={(e) => setOfferInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      handleAddOffer();
                    }
                  }}
                  placeholder="Ví dụ: Tư vấn kiến trúc Agentic AI, chia sẻ kinh nghiệm Product Delivery..."
                  className="flex-1 rounded-button border border-subtle bg-elevated px-3 py-2 text-sm text-primary placeholder:text-secondary/50 focus:border-accent focus:outline-none"
                />
                <Button type="button" variant="secondary" size="sm" onClick={handleAddOffer}>
                  <Plus size={14} className="mr-1" /> Thêm
                </Button>
              </div>

              {offering.length > 0 && (
                <ul className="space-y-1.5 pt-1">
                  {offering.map((offer, idx) => (
                    <li
                      key={idx}
                      className="flex items-center justify-between rounded-button bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 text-xs text-emerald-200"
                    >
                      <span>• {offer}</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveOffer(offer)}
                        className="hover:text-red-400 text-emerald-300 ml-2"
                      >
                        <X size={13} />
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Bio */}
            <div className="space-y-1 pt-2">
              <label className="block text-xs font-medium text-secondary">
                Giới thiệu ngắn về bản thân (Bio)
              </label>
              <textarea
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                rows={3}
                placeholder="Mô tả ngắn gọn về kinh nghiệm, định hướng và mục tiêu giao lưu kết nối của bạn..."
                className="w-full rounded-button border border-subtle bg-elevated px-3 py-2 text-sm text-primary placeholder:text-secondary/50 focus:border-accent focus:outline-none resize-none"
              />
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <Button
              type="submit"
              variant="primary"
              size="md"
              disabled={updateMutation.isPending}
              className="flex items-center gap-2"
            >
              <Save size={16} />
              {updateMutation.isPending ? "Đang lưu vào CSDL..." : "Lưu Hồ sơ & Áp dụng cho AI"}
            </Button>
          </div>
        </form>
      </div>
    </main>
  );
}
