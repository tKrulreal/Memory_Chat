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
  Brain,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { getMyProfile, updateMyProfile, ProfileUpdatePayload } from "@/lib/api/profile";
// Settings API moved to AI Hub
import { generateConnections } from "@/lib/api/recommendations";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";


export default function SettingsPage() {
  const queryClient = useQueryClient();
  const router = useRouter();



  const { data: profile, isLoading: isLoadingProfile, error } = useQuery({
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
    if (val) {
      if (!skills.includes(val)) {
        setSkills([...skills, val]);
      }
      setSkillInput("");
    }
  };

  const handleRemoveSkill = (s: string) => {
    setSkills(skills.filter((item) => item !== s));
  };

  const handleAddInterest = () => {
    const val = interestInput.trim();
    if (val) {
      if (!interests.includes(val)) {
        setInterests([...interests, val]);
      }
      setInterestInput("");
    }
  };

  const handleRemoveInterest = (i: string) => {
    setInterests(interests.filter((item) => item !== i));
  };

  const handleAddNeed = () => {
    const val = needInput.trim();
    if (val) {
      if (!lookingFor.includes(val)) {
        setLookingFor([...lookingFor, val]);
      }
      setNeedInput("");
    }
  };

  const handleRemoveNeed = (n: string) => {
    setLookingFor(lookingFor.filter((item) => item !== n));
  };

  const handleAddOffer = () => {
    const val = offerInput.trim();
    if (val) {
      if (!offering.includes(val)) {
        setOffering([...offering, val]);
      }
      setOfferInput("");
    }
  };

  const handleRemoveOffer = (o: string) => {
    setOffering(offering.filter((item) => item !== o));
  };

  // Settings update moved to AI Hub

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

  if (isLoadingProfile) {
    return (
      <main className="flex-1 overflow-y-auto bg-background p-6 md:p-10">
        <div className="mx-auto max-w-4xl space-y-6">
          <Skeleton className="h-10 w-64 rounded-xl" />
          <Skeleton className="h-40 w-full rounded-xl" />
          <Skeleton className="h-96 w-full rounded-xl" />
        </div>
      </main>
    );
  }

  return (
    <main className="flex-1 overflow-y-auto bg-background p-6 md:p-10">
      <div className="mx-auto max-w-4xl space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 border-b border-border pb-4">
          <div>
            <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
              <User className="h-7 w-7 text-primary" />
              Cài đặt & Hồ sơ
            </h1>
          </div>

          <Button
            variant="secondary"
            size="sm"
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="flex items-center gap-1.5 shrink-0"
          >
            <Sparkles size={15} className="text-primary" />
            {generateMutation.isPending ? "Đang quét AI..." : "Quét gợi ý kết nối mới"}
          </Button>
        </div>

        <>
          {/* Priority Explanation Banner */}
        <Card className="rounded-2xl border-slate-100 bg-white p-5 space-y-3 shadow-sm hover:shadow-md transition-all">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-800">
              <ShieldCheck className="h-5 w-5 text-blue-600" />
              <span>Trạng thái nguồn dữ liệu hiện tại:</span>
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
            <strong className="text-slate-700">Quy tắc ưu tiên của AI Matchmaker:</strong> Khi bạn nhập thông tin ở biểu mẫu bên dưới, hệ thống sẽ <strong className="text-blue-600">lưu vào bảng hồ sơ riêng và ưu tiên 100% dữ liệu này</strong> để so sánh. Nếu trường nào bạn để trống, hệ thống sẽ tự động sử dụng thông tin trích xuất được từ nội dung hội thoại thực tế của bạn.
          </p>
        </Card>

        {/* Success Alert */}
        {saveSuccess && (
          <div className="flex items-center gap-2.5 rounded-xl border border-blue-500/30 bg-blue-50 p-4 text-sm text-blue-600">
            <CheckCircle2 size={18} />
            <span>Hồ sơ đã được lưu thành công vào cơ sở dữ liệu! AI Matchmaker sẽ ưu tiên dữ liệu này khi tìm kiếm người phù hợp.</span>
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
          {/* Card: Basic Identity */}
          <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-6 shadow-sm">
            <h2 className="text-lg font-bold border-b border-slate-100 pb-4 flex items-center gap-2 text-slate-800">
              <Briefcase size={20} className="text-blue-600" />
              Thông tin Công việc & Địa điểm
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">
                  Họ và tên
                </label>
                <Input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Ví dụ: Nguyễn Hoàng Long"
                  className="w-full bg-background"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">
                  Email (Không đổi)
                </label>
                <Input
                  type="email"
                  value={profile?.email || ""}
                  disabled
                  className="w-full bg-muted text-muted-foreground cursor-not-allowed"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">
                  Số điện thoại
                </label>
                <Input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="Ví dụ: 0912345678"
                  className="w-full bg-background"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">
                  Giới tính
                </label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                  className="flex h-9 w-full rounded-xl border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <option value="">Chọn giới tính</option>
                  <option value="male">Nam</option>
                  <option value="female">Nữ</option>
                  <option value="other">Khác</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">
                  Chức danh / Nghề nghiệp chính (Profession)
                </label>
                <Input
                  type="text"
                  value={profession}
                  onChange={(e) => setProfession(e.target.value)}
                  placeholder="Ví dụ: Senior AI / LLM Engineer, Tech Product Lead..."
                  className="w-full bg-background"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">
                  Công ty / Tổ chức (Company)
                </label>
                <Input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  placeholder="Ví dụ: VinAI Research, NextGen Innovation..."
                  className="w-full bg-background"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-xs font-medium text-muted-foreground mb-1 flex items-center gap-1">
                  <MapPin size={12} className="text-primary" />
                  Địa điểm / Khu vực sinh sống (Location)
                </label>
                <Input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="Ví dụ: Hà Nội, TP. Hồ Chí Minh, Đà Nẵng..."
                  className="w-full bg-background"
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
              <label className="block text-xs font-medium text-muted-foreground">
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
                  placeholder="Nhập kỹ năng rồi bấm Thêm (ví dụ: Python, PyTorch, RAG, Flutter...)"
                  className="flex-1 bg-background"
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
                      className="flex items-center gap-1 rounded-full bg-secondary border px-2.5 py-1 text-xs text-secondary-foreground"
                    >
                      {s}
                      <Button variant="ghost"
                        type="button"
                        onClick={() => handleRemoveSkill(s)}
                        className="hover:text-destructive text-muted-foreground h-auto p-1 ml-1"
                      >
                        <X size={12} />
                      </Button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Interests */}
            <div className="space-y-2">
              <label className="block text-xs font-medium text-muted-foreground">
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
                  placeholder="Nhập chủ đề quan tâm (ví dụ: Generative AI, EdTech, Startups...)"
                  className="flex-1 bg-background"
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
                      className="flex items-center gap-1 rounded-full bg-muted border border-border px-2.5 py-1 text-xs text-muted-foreground"
                    >
                      #{i}
                      <Button variant="ghost"
                        type="button"
                        onClick={() => handleRemoveInterest(i)}
                        className="hover:text-destructive text-muted-foreground h-auto p-1 ml-1"
                      >
                        <X size={12} />
                      </Button>
                    </span>
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
                  className="flex-1 bg-background"
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
                      className="flex items-center justify-between rounded-lg bg-primary/10 border border-primary/20 px-3 py-1.5 text-xs text-primary"
                    >
                      <span>• {need}</span>
                      <Button variant="ghost"
                        type="button"
                        onClick={() => handleRemoveNeed(need)}
                        className="hover:text-destructive text-primary/70 ml-2 h-auto p-1"
                      >
                        <X size={13} />
                      </Button>
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
                  className="flex-1 bg-background"
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
                      className="flex items-center justify-between rounded-lg bg-green-50 border border-green-200 px-3 py-1.5 text-xs text-green-600"
                    >
                      <span>• {offer}</span>
                      <Button variant="ghost"
                        type="button"
                        onClick={() => handleRemoveOffer(offer)}
                        className="hover:text-red-500 text-green-400 ml-2"
                      >
                        <X size={13} />
                      </Button>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Bio */}
            <div className="space-y-1 pt-2">
              <label className="block text-xs font-medium text-muted-foreground">
                Giới thiệu ngắn về bản thân (Bio)
              </label>
              <Textarea
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                rows={3}
                placeholder="Mô tả ngắn gọn về kinh nghiệm, định hướng và mục tiêu giao lưu kết nối của bạn..."
                className="w-full bg-background resize-none"
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
        </>
      </div>
    </main>
  );
}
