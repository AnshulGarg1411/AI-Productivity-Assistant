import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";

import {
  getAllTasks,
  getTaskAnalytics,
  createTask,
  updateTask,
  completeTask,
  deleteTask,
} from "../api/taskApi";

export const useTasksQuery = () => {
  return useQuery({
    queryKey: ["tasks"],
    queryFn: getAllTasks,
  });
};

export const useTaskAnalyticsQuery = () => {
  return useQuery({
    queryKey: ["taskAnalytics"],
    queryFn: getTaskAnalytics,
  });
};

export const useTasks = () => {
  const queryClient = useQueryClient();

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ["tasks"] });
    queryClient.invalidateQueries({ queryKey: ["taskAnalytics"] });
    queryClient.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const createMutation = useMutation({
    mutationFn: createTask,
    onSuccess: () => {
      toast.success("Task created");
      refresh();
    },
    onError: () => toast.error("Could not create task"),
  });

  const updateMutation = useMutation({
    mutationFn: updateTask,
    onSuccess: () => {
      toast.success("Task updated");
      refresh();
    },
    onError: () => toast.error("Could not update task"),
  });

  const completeMutation = useMutation({
    mutationFn: completeTask,
    onSuccess: () => {
      toast.success("Task marked as complete");
      refresh();
    },
    onError: () => toast.error("Could not complete task"),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteTask,
    onSuccess: () => {
      toast.success("Task deleted");
      refresh();
    },
    onError: () => toast.error("Could not delete task"),
  });

  return { createMutation, updateMutation, completeMutation, deleteMutation };
};
