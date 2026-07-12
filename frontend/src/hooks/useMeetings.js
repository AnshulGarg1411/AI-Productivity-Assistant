import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";

import {
  getAllMeetings,
  getMeetingAnalytics,
  createMeeting,
  syncCalendar,
} from "../api/meetingApi";

export const useMeetingsQuery = () => {
  return useQuery({
    queryKey: ["meetings"],
    queryFn: getAllMeetings,
  });
};

export const useMeetingAnalyticsQuery = () => {
  return useQuery({
    queryKey: ["meetingAnalytics"],
    queryFn: getMeetingAnalytics,
  });
};

export const useMeetings = () => {
  const queryClient = useQueryClient();

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ["meetings"] });
    queryClient.invalidateQueries({ queryKey: ["meetingAnalytics"] });
    queryClient.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const createMutation = useMutation({
    mutationFn: createMeeting,
    onSuccess: () => {
      toast.success("Meeting created");
      refresh();
    },
    onError: () => toast.error("Could not create meeting"),
  });

  const syncMutation = useMutation({
    mutationFn: syncCalendar,
    onSuccess: (data) => {
      toast.success(
        `Synced ${data?.synced ?? 0} meeting(s) from Google Calendar`
      );
      refresh();
    },
    onError: () => toast.error("Calendar sync failed"),
  });

  return { createMutation, syncMutation };
};
