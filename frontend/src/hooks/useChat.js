import { useMutation } from "@tanstack/react-query";
import { sendChatMessage } from "../api/chatApi";

export const useChat = () => {
  return useMutation({
    mutationFn: sendChatMessage,
  });
};
