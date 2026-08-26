"use client";

import { use } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { UserProfileView } from "@/components/profile/user-profile-view";

interface ProfilePageProps {
  params: Promise<{
    id: string;
  }>;
}

export default function ProfilePage({ params }: ProfilePageProps) {
  const router = useRouter();
  const resolvedParams = use(params);
  const userId = resolvedParams.id;

  return (
    <main className="flex-1 overflow-y-auto bg-slate-50 p-6 md:p-10">
      <div className="mx-auto max-w-3xl mb-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.back()}
          className="text-slate-600 hover:text-slate-900"
        >
          <ArrowLeft size={16} className="mr-1.5" />
          <span>Quay lại</span>
        </Button>
      </div>

      <UserProfileView userId={userId} />
    </main>
  );
}
