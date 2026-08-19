import { useMutation, useQueryClient } from "@tanstack/react-query";
import { sendMessage } from "@/lib/api/messages";
import type { Message } from "@/types";

export function useSendMessage(conversationId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ content, clientMessageId }: { content: string; clientMessageId: string }) =>
      sendMessage(conversationId, content, clientMessageId),
    onMutate: async ({ content, clientMessageId }) => {
      await queryClient.cancelQueries({ queryKey: ["messages", conversationId] });
      const previousMessages = queryClient.getQueryData(["messages", conversationId]);
      
      const optimisticMessage: Message = {
        id: clientMessageId,
        conversation_id: conversationId,
        sender_user_id: "optimistic",
        content,
        created_at: new Date().toISOString(),
        client_message_id: clientMessageId,
        local_status: "sending",
      };
      
      queryClient.setQueryData(["messages", conversationId], (old: any) => {
        if (!old || !old.pages || old.pages.length === 0) {
          return {
            pages: [{ data: [optimisticMessage], pagination: { page: 1, limit: 50, total: 1 } }],
            pageParams: [undefined],
          };
        }
        
        const newPages = [...old.pages];
        const firstPage = { ...newPages[0] };
        
        // Remove existing if retry
        const filteredData = firstPage.data.filter((m: Message) => m.client_message_id !== clientMessageId);
        firstPage.data = [optimisticMessage, ...filteredData];
        newPages[0] = firstPage;
        
        return { ...old, pages: newPages };
      });

      return { previousMessages, clientMessageId };
    },
    onError: (err, variables, context) => {
      // Instead of rolling back, we mark the specific message as failed
      queryClient.setQueryData(["messages", conversationId], (old: any) => {
        if (!old || !old.pages) return old;
        
        const newPages = old.pages.map((page: any) => ({
          ...page,
          data: page.data.map((m: Message) => 
            m.client_message_id === variables.clientMessageId
              ? { ...m, local_status: "failed" }
              : m
          )
        }));
        
        return { ...old, pages: newPages };
      });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
    },
  });
}
