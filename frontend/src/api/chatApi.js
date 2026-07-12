import api from "./axios";

export const sendChatMessage = async ({ message, history }) => {
  const response = await api.post("/chat/", { message, history });
  return response.data;
};
