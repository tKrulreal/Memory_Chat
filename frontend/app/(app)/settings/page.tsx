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
  Globe,
  Github,
  Linkedin,
  GraduationCap,
  Eye,
  EyeOff,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { getMyProfile, updateMyProfile, ProfileUpdatePayload } from "@/lib/api/profile";
import { generateConnections } from "@/lib/api/recommendations";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { ExperienceItem, EducationItem } from "@/types";

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const router = useRouter();

  const { data: profile, isLoading: isLoadingProfile } = useQuery({
    queryKey: ["my-profile"],
    queryFn: getMyProfile,
  });

  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [gender, setGender] = useState("");
  const [profession, setProfession] = useState("");
  const [company, setCompany] = useState("");
  const [location, setLocation] = useState("");
  const [isPublic, setIsPublic] = useState(true);
  const [github, setGithub] = useState("");
  const [linkedin, setLinkedin] = useState("");
  const [website, setWebsite] = useState("");

  const [skills, setSkills] = useState<string[]>([]);
  const [skillInput, setSkillInput] = useState("");

  const [interests, setInterests] = useState<string[]>([]);
  const [interestInput, setInterestInput] = useState("");

  const [lookingFor, setLookingFor] = useState<string[]>([]);
  const [needInput, setNeedInput] = useState("");

  const [offering, setOffering] = useState<string[]>([]);
  const [offerInput, setOfferInput] = useState("");

  const [bio, setBio] = useState("");

  // Experience state
  const [experience, setExperience] = useState<ExperienceItem[]>([]);
  const [expTitle, setExpTitle] = useState("");
  const [expCompany, setExpCompany] = useState("");
  const [expPeriod, setExpPeriod] = useState("");

  // Education state
  const [education, setEducation] = useState<EducationItem[]>([]);
  const [eduSchool, setEduSchool] = useState("");
  const [eduDegree, setEduDegree] = useState("");
  const [eduYear, setEduYear] = useState("");

  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (profile) {
      setFullName(profile.full_name || "");
      setPhone(profile.phone || "");
      setGender(profile.gender || "");
      setProfession(profile.profession || "");
      setCompany(profile.company || "");
      setLocation(profile.location || "");
      setIsPublic(profile.is_public !== false);
      setGithub(profile.github || "");
      setLinkedin(profile.linkedin || "");
      setWebsite(profile.website || "");
      setSkills(profile.skills || []);
      setInterests(profile.interests || []);
      setLookingFor(profile.looking_for || []);
      setOffering(profile.offering || []);
      setBio(profile.bio || "");
      setExperience(profile.experience || []);
      setEducation(profile.education || []);
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

  const handleAddExperience = () => {
    if (expTitle.trim() && expCompany.trim()) {
      setExperience([
        ...experience,
        {
          title: expTitle.trim(),
          company: expCompany.trim(),
          period: expPeriod.trim() || undefined,
        },
      ]);
      setExpTitle("");
      setExpCompany("");
      setExpPeriod("");
    }
  };

  const handleRemoveExperience = (idx: number) => {
    setExperience(experience.filter((_, i) => i !== idx));
  };

  const handleAddEducation = () => {
    if (eduSchool.trim()) {
      setEducation([
        ...education,
        {
          school: eduSchool.trim(),
          degree: eduDegree.trim() || undefined,
          year: eduYear.trim() || undefined,
        },
      ]);
      setEduSchool("");
      setEduDegree("");
      setEduYear("");
    }
  };

  const handleRemoveEducation = (idx: number) => {
    setEducation(education.filter((_, i) => i !== idx));
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
      is_public: isPublic,
      github: github.trim() || null,
      linkedin: linkedin.trim() || null,
      website: website.trim() || null,
      skills,
      interests,
      looking_for: lookingFor,
      offering,
      bio: bio.trim() || null,
      experience,
      education,
    });
  };

  if (isLoadingProfile) {
    return (
      <main className="flex-1 overflow-y-auto bg-slate-50 p-6 md:p-10">
        <div className="mx-auto max-w-4xl space-y-6">
          <Skeleton className="h-10 w-64 rounded-xl" />
          <Skeleton className="h-40 w-full rounded-xl" />
          <Skeleton className="h-96 w-full rounded-xl" />
        </div>
      </main>
    );
  }

  return (
    <main className="flex-1 overflow-y-auto bg-slate-50 p-6 md:p-10">
      <div className="mx-auto max-w-4xl space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 border-b border-slate-200 pb-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
              <User className="h-7 w-7 text-blue-600" />
              Cài đặt & Hồ sơ Cá nhân
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Quản lý thông tin hồ sơ, quyền riêng tư công khai và dữ liệu phục vụ AI Copilot.
            </p>
          </div>

          <div className="flex items-center gap-2">
            {profile?.user_id && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push(`/profile/${profile.user_id}`)}
                className="flex items-center gap-1.5"
              >
                <Eye size={15} />
                Xem trang cá nhân
              </Button>
            )}
            <Button
              variant="secondary"
              size="sm"
              onClick={() => generateMutation.mutate()}
              disabled={generateMutation.isPending}
              className="flex items-center gap-1.5 shrink-0"
            >
              <Sparkles size={15} className="text-blue-600" />
              {generateMutation.isPending ? "Đang quét AI..." : "Quét gợi ý kết nối"}
            </Button>
          </div>
        </div>

        {/* Priority & Privacy Explanation Banner */}
        <Card className="rounded-2xl border-slate-100 bg-white p-5 space-y-3 shadow-sm hover:shadow-md transition-all">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-800">
              <ShieldCheck className="h-5 w-5 text-blue-600" />
              <span>Trạng thái nguồn dữ liệu:</span>
            </div>
            {profile?.is_custom_profile ? (
              <Badge variant="outline" className="bg-blue-50 border-blue-200 px-3 py-1 text-xs font-semibold text-blue-700 shadow-sm">
                ✓ Đang ưu tiên: Dữ liệu bạn tự nhập
              </Badge>
            ) : (
              <Badge variant="secondary" className="bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600 shadow-sm">
                🤖 Đang tự động trích xuất từ đoạn chat
              </Badge>
            )}
          </div>
          <p className="text-sm font-medium text-slate-500 leading-relaxed">
            <strong className="text-slate-700">Quy tắc AI Matchmaker & Copilot:</strong> Khi bạn nhập thông tin, hệ thống sẽ ưu tiên 100% dữ liệu này để so khớp tìm kiếm kỹ năng, việc làm và kết nối đối tác.
          </p>
        </Card>

        {/* Success Alert */}
        {saveSuccess && (
          <div className="flex items-center gap-2.5 rounded-xl border border-blue-500/30 bg-blue-50 p-4 text-sm text-blue-600">
            <CheckCircle2 size={18} />
            <span>Hồ sơ đã được lưu thành công! AI Copilot và hệ thống tìm kiếm đã được cập nhật.</span>
          </div>
        )}

        {/* Error Alert */}
        {updateMutation.isError && (
          <div className="flex items-center gap-2.5 rounded-xl border border-red-500/30 bg-red-50 p-4 text-sm text-red-600">
            <AlertCircle size={18} />
            <span>{updateMutation.error?.message || "Có lỗi xảy ra khi lưu hồ sơ."}</span>
          </div>
        )}

        {/* Main Profile Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Card: Public Profile Toggle */}
          <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-4 shadow-sm">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="space-y-1 max-w-xl">
                <div className="flex items-center gap-2 text-base font-bold text-slate-800">
                  {isPublic ? <Eye className="h-5 w-5 text-green-600" /> : <EyeOff className="h-5 w-5 text-slate-400" />}
                  <span>Chế độ Công khai Hồ sơ (Public Profile)</span>
                </div>
                <p className="text-xs text-slate-500 leading-relaxed">
                  {isPublic
                    ? "BẬT: Hồ sơ của bạn sẽ hiển thị công khai trên mạng, cho phép người dùng khác và AI Copilot tìm thấy bạn qua kỹ năng, sở thích, kinh nghiệm để kết nối."
                    : "TẮT (Riêng tư): Hồ sơ của bạn được ẩn hoàn toàn với người lạ. AI Copilot sẽ không đọc hồ sơ của bạn để gợi ý cho người chưa từng trò chuyện."}
                </p>
              </div>

              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={isPublic}
                  onChange={(e) => setIsPublic(e.target.checked)}
                />
                <div className="w-12 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
              </label>
            </div>
          </Card>

          {/* Card: Basic Identity */}
          <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-6 shadow-sm">
            <h2 className="text-lg font-bold border-b border-slate-100 pb-4 flex items-center gap-2 text-slate-800">
              <Briefcase size={20} className="text-blue-600" />
              Thông tin Cơ bản & Công việc
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">
                  Họ và tên
                </label>
                <Input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Ví dụ: Nguyễn Hoàng Long"
                  className="w-full bg-slate-50"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">
                  Email (Không đổi)
                </label>
                <Input
                  type="email"
                  value={profile?.email || ""}
                  disabled
                  className="w-full bg-slate-100 text-slate-400 cursor-not-allowed"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">
                  Số điện thoại
                </label>
                <Input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="Ví dụ: 0912345678"
                  className="w-full bg-slate-50"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">
                  Giới tính
                </label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                  className="flex h-9 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-blue-500"
                >
                  <option value="">Chọn giới tính</option>
                  <option value="male">Nam</option>
                  <option value="female">Nữ</option>
                  <option value="other">Khác</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">
                  Chức danh / Nghề nghiệp chính (Profession)
                </label>
                <Input
                  type="text"
                  value={profession}
                  onChange={(e) => setProfession(e.target.value)}
                  placeholder="Ví dụ: Senior AI / LLM Engineer, Tech Lead..."
                  className="w-full bg-slate-50"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">
                  Công ty / Tổ chức (Company)
                </label>
                <Input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  placeholder="Ví dụ: VinAI, FPT Software..."
                  className="w-full bg-slate-50"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-xs font-medium text-slate-600 mb-1 flex items-center gap-1">
                  <MapPin size={12} className="text-blue-600" />
                  Địa điểm / Khu vực (Location)
                </label>
                <Input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="Ví dụ: Hà Nội, TP. Hồ Chí Minh, Đà Nẵng..."
                  className="w-full bg-slate-50"
                />
              </div>
            </div>
          </Card>

          {/* Card: Social & Portfolio Links */}
          <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-6 shadow-sm">
            <h2 className="text-lg font-bold border-b border-slate-100 pb-4 flex items-center gap-2 text-slate-800">
              <Globe size={20} className="text-blue-600" />
              Liên kết Mạng Xã hội & Portfolio
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1 flex items-center gap-1.5">
                  <Github size={13} className="text-slate-700" />
                  GitHub URL
                </label>
                <Input
                  type="text"
                  value={github}
                  onChange={(e) => setGithub(e.target.value)}
                  placeholder="https://github.com/username"
                  className="w-full bg-slate-50"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1 flex items-center gap-1.5">
                  <Linkedin size={13} className="text-blue-600" />
                  LinkedIn URL
                </label>
                <Input
                  type="text"
                  value={linkedin}
                  onChange={(e) => setLinkedin(e.target.value)}
                  placeholder="https://linkedin.com/in/username"
                  className="w-full bg-slate-50"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1 flex items-center gap-1.5">
                  <Globe size={13} className="text-green-600" />
                  Website / Portfolio
                </label>
                <Input
                  type="text"
                  value={website}
                  onChange={(e) => setWebsite(e.target.value)}
                  placeholder="https://myportfolio.dev"
                  className="w-full bg-slate-50"
                />
              </div>
            </div>
          </Card>

          {/* Card: Skills & Interests */}
          <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-6 shadow-sm">
            <h2 className="text-lg font-bold border-b border-slate-100 pb-4 flex items-center gap-2 text-slate-800">
              <Sparkles size={20} className="text-blue-600" />
              Kỹ năng & Mối quan tâm chuyên môn
            </h2>

            {/* Skills */}
            <div className="space-y-2">
              <label className="block text-xs font-medium text-slate-600">
                Kỹ năng chuyên môn (Skills)
              </label>
              <div className="flex gap-2">
                <Input
                  type="text"
                  value={skillInput}
                  onChange={(e) => setSkillInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      handleAddSkill();
                    }
                  }}
                  placeholder="Nhập kỹ năng rồi bấm Thêm (ví dụ: Python, PyTorch, RAG, Next.js...)"
                  className="flex-1 bg-slate-50"
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
                      className="flex items-center gap-1 rounded-full bg-blue-50 border border-blue-200 px-3 py-1 text-xs font-medium text-blue-700 shadow-2xs"
                    >
                      {s}
                      <button
                        type="button"
                        onClick={() => handleRemoveSkill(s)}
                        className="hover:text-red-600 text-blue-400 ml-1 cursor-pointer"
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
              <label className="block text-xs font-medium text-slate-600">
                Lĩnh vực / Mối quan tâm (Interests)
              </label>
              <div className="flex gap-2">
                <Input
                  type="text"
                  value={interestInput}
                  onChange={(e) => setInterestInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      handleAddInterest();
                    }
                  }}
                  placeholder="Nhập chủ đề quan tâm (ví dụ: Agentic AI, AI Automation, Startups...)"
                  className="flex-1 bg-slate-50"
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
                      className="flex items-center gap-1 rounded-full bg-slate-100 border border-slate-200 px-3 py-1 text-xs font-medium text-slate-700 shadow-2xs"
                    >
                      #{i}
                      <button
                        type="button"
                        onClick={() => handleRemoveInterest(i)}
                        className="hover:text-red-600 text-slate-400 ml-1 cursor-pointer"
                      >
                        <X size={12} />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>
          </Card>

          {/* Card: Experience & Education */}
          <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-6 shadow-sm">
            <h2 className="text-lg font-bold border-b border-slate-100 pb-4 flex items-center gap-2 text-slate-800">
              <GraduationCap size={20} className="text-blue-600" />
              Kinh nghiệm Làm việc & Học vấn
            </h2>

            {/* Work Experience */}
            <div className="space-y-3">
              <label className="block text-xs font-medium text-slate-700">
                Kinh nghiệm làm việc (Experience)
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                <Input
                  type="text"
                  value={expTitle}
                  onChange={(e) => setExpTitle(e.target.value)}
                  placeholder="Vị trí (e.g. Lead AI Engineer)"
                  className="bg-slate-50"
                />
                <Input
                  type="text"
                  value={expCompany}
                  onChange={(e) => setExpCompany(e.target.value)}
                  placeholder="Công ty (e.g. VinAI Research)"
                  className="bg-slate-50"
                />
                <div className="flex gap-2">
                  <Input
                    type="text"
                    value={expPeriod}
                    onChange={(e) => setExpPeriod(e.target.value)}
                    placeholder="Thời gian (e.g. 2022 - Nay)"
                    className="bg-slate-50 flex-1"
                  />
                  <Button type="button" variant="secondary" size="sm" onClick={handleAddExperience}>
                    <Plus size={14} /> Thêm
                  </Button>
                </div>
              </div>

              {experience.length > 0 && (
                <div className="space-y-2 pt-1">
                  {experience.map((exp, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between rounded-xl bg-slate-50 border border-slate-200 p-3 text-xs"
                    >
                      <div>
                        <span className="font-semibold text-slate-800">{exp.title}</span>
                        <span className="text-slate-500"> tại {exp.company}</span>
                        {exp.period && <span className="text-slate-400 ml-2">({exp.period})</span>}
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoveExperience(idx)}
                        className="text-slate-400 hover:text-red-500 cursor-pointer"
                      >
                        <X size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Education */}
            <div className="space-y-3 pt-4 border-t border-slate-100">
              <label className="block text-xs font-medium text-slate-700">
                Học vấn & Bằng cấp (Education)
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                <Input
                  type="text"
                  value={eduSchool}
                  onChange={(e) => setEduSchool(e.target.value)}
                  placeholder="Trường (e.g. ĐH Bách Khoa Hà Nội)"
                  className="bg-slate-50"
                />
                <Input
                  type="text"
                  value={eduDegree}
                  onChange={(e) => setEduDegree(e.target.value)}
                  placeholder="Ngành/Bằng cấp (e.g. Kỹ sư CNTT)"
                  className="bg-slate-50"
                />
                <div className="flex gap-2">
                  <Input
                    type="text"
                    value={eduYear}
                    onChange={(e) => setEduYear(e.target.value)}
                    placeholder="Năm tốt nghiệp (e.g. 2021)"
                    className="bg-slate-50 flex-1"
                  />
                  <Button type="button" variant="secondary" size="sm" onClick={handleAddEducation}>
                    <Plus size={14} /> Thêm
                  </Button>
                </div>
              </div>

              {education.length > 0 && (
                <div className="space-y-2 pt-1">
                  {education.map((edu, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between rounded-xl bg-slate-50 border border-slate-200 p-3 text-xs"
                    >
                      <div>
                        <span className="font-semibold text-slate-800">{edu.school}</span>
                        {edu.degree && <span className="text-slate-500"> — {edu.degree}</span>}
                        {edu.year && <span className="text-slate-400 ml-2">({edu.year})</span>}
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoveEducation(idx)}
                        className="text-slate-400 hover:text-red-500 cursor-pointer"
                      >
                        <X size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Card>

          {/* Card: Looking for & Offering Matrix */}
          <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-6 shadow-sm">
            <h2 className="text-lg font-bold border-b border-slate-100 pb-4 flex items-center gap-2 text-slate-800">
              <ArrowRight size={20} className="text-blue-600" />
              Nhu cầu Tìm kiếm & Giá trị Chia sẻ
            </h2>

            {/* Looking For */}
            <div className="space-y-2">
              <label className="block text-xs font-medium text-blue-600">
                Looking for — Nhu cầu bạn đang tìm kiếm (Dự án, đối tác, tuyển dụng...)
              </label>
              <div className="flex gap-2">
                <Input
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
                  className="flex-1 bg-slate-50"
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
                      className="flex items-center justify-between rounded-lg bg-blue-50 border border-blue-100 px-3 py-1.5 text-xs text-blue-700"
                    >
                      <span>• {need}</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveNeed(need)}
                        className="hover:text-red-600 text-blue-400 ml-2 cursor-pointer"
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
              <label className="block text-xs font-medium text-green-600">
                Offering — Giá trị / Kinh nghiệm bạn có thể chia sẻ, hỗ trợ đối phương
              </label>
              <div className="flex gap-2">
                <Input
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
                  className="flex-1 bg-slate-50"
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
                      className="flex items-center justify-between rounded-lg bg-green-50 border border-green-200 px-3 py-1.5 text-xs text-green-700"
                    >
                      <span>• {offer}</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveOffer(offer)}
                        className="hover:text-red-500 text-green-400 ml-2 cursor-pointer"
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
              <label className="block text-xs font-medium text-slate-600">
                Giới thiệu ngắn về bản thân (Bio)
              </label>
              <Textarea
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                rows={3}
                placeholder="Mô tả ngắn gọn về kinh nghiệm, định hướng và mục tiêu giao lưu kết nối của bạn..."
                className="w-full bg-slate-50 resize-none"
              />
            </div>
          </Card>

          {/* Submit Button */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <Button
              type="submit"
              variant="primary"
              size="default"
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
