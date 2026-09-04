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
    chat_copilot: true,
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

  const chatCopilotSettings = {
    contextMode: aiConfig?.value?.chat_copilot_context_mode ?? "scoped_chat",
    messageLimit: aiConfig?.value?.chat_copilot_message_limit ?? 20,
    quickActions: aiConfig?.value?.chat_copilot_quick_actions !== false,
  };

  const rawScore = aiConfig?.value?.min_matching_score ?? 50;
  const minMatchingScore = rawScore <= 1.0 ? Math.round(rawScore * 100) : rawScore;
  const notificationInterval = aiConfig?.value?.notification_interval ?? "24h";

  return {
    features,
    isLoading,
    rawConfig: aiConfig,
    chatCopilotSettings,
    minMatchingScore,
    notificationInterval,
  };
}
