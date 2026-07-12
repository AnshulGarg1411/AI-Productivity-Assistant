import api from "./axios";

export const getAllTasks = async () => {
  const response = await api.get("/tasks/");
  return response.data;
};

export const getPendingTasks = async () => {
  const response = await api.get("/tasks/pending");
  return response.data;
};

export const getCompletedTasks = async () => {
  const response = await api.get("/tasks/completed");
  return response.data;
};

export const getTodayTasks = async () => {
  const response = await api.get("/tasks/today");
  return response.data;
};

export const getTaskAnalytics = async () => {
  const response = await api.get("/tasks/analytics");
  return response.data;
};

export const createTask = async (task) => {
  const response = await api.post("/tasks/", task);
  return response.data;
};

export const updateTask = async ({ id, task }) => {
  const response = await api.put(`/tasks/${id}`, task);
  return response.data;
};

export const completeTask = async ({ id, actualMinutes }) => {
  const response = await api.patch(
    `/tasks/${id}/complete?actual_minutes=${actualMinutes}`
  );
  return response.data;
};

export const deleteTask = async (id) => {
  const response = await api.delete(`/tasks/${id}`);
  return response.data;
};
