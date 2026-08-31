import { useQuery } from "@tanstack/react-query";
import { getAiConfigs } from "@/lib/api/tags";

export function useAISettings(enabled = true) {
  const { data: configs = [], isLoading } = useQuery({
    queryKey: ["system-configs"],
    queryFn: getAiConfigs,
    enabled,
  });

  const aiConfig = configs.find(c => c.key === "ai_settings");
  let features = {
    copilot: true,
    recommendation: true,
    memory: true,
    tagging: true,
  };

  if (aiConfig && aiConfig.value && aiConfig.value.features) {
    features = {
      ...features,
      ...aiConfig.value.features,
    };
  }

  return {
    features,
    isLoading,
    rawConfig: aiConfig,
  };
}
