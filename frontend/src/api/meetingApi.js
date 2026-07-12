import api from "./axios";

export const getAllMeetings = async () => {
  const response = await api.get("/meetings/");
  return response.data;
};

export const getTodayMeetings = async () => {
  const response = await api.get("/meetings/today");
  return response.data;
};

export const getUpcomingMeetings = async () => {
  const response = await api.get("/meetings/upcoming");
  return response.data;
};

export const getMeetingAnalytics = async () => {
  const response = await api.get("/meetings/analytics");
  return response.data;
};

export const createMeeting = async (meeting) => {
  const response = await api.post("/meetings/", meeting);
  return response.data;
};

export const syncCalendar = async () => {
  const response = await api.get("/calendar/sync");
  return response.data;
};
