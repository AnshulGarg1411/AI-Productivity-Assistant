import { useMutation, useQueryClient } from "@tanstack/react-query";

import {

    archiveEmail,

    deleteEmail,

    starEmail,

    unstarEmail,

    markRead,

    summarizeEmail,

    generateReply

} from "../api/emailApi";

import toast from "react-hot-toast";

export const useEmails = () => {

    const queryClient = useQueryClient();

    const refresh = () => {

        queryClient.invalidateQueries({

            queryKey:["emails"]

        });

    };

    const archiveMutation = useMutation({

        mutationFn: archiveEmail,

        onSuccess:()=>{

            toast.success("Email Archived");

            refresh();

        }

    });

    const deleteMutation = useMutation({

        mutationFn: deleteEmail,

        onSuccess:()=>{

            toast.success("Email Deleted");

            refresh();

        }

    });

    const starMutation = useMutation({

        mutationFn: starEmail,

        onSuccess:()=>{

            refresh();

        }

    });

    const unstarMutation = useMutation({

        mutationFn: unstarEmail,

        onSuccess:()=>{

            refresh();

        }

    });

    const readMutation = useMutation({

        mutationFn: markRead,

        onSuccess:()=>{

            refresh();

        }

    });

    const summarizeMutation = useMutation({

        mutationFn: summarizeEmail,

        onSuccess: () => {

            refresh();

        },

        onError: (error) => {

            const detail = error?.response?.data?.detail;

            toast.error(detail || "Could not generate summary");

        }

    });

    const replyMutation = useMutation({

        mutationFn: generateReply,

        onError: (error) => {

            const detail = error?.response?.data?.detail;

            toast.error(detail || "Could not generate reply");

        }

    });

    return{

        archiveMutation,

        deleteMutation,

        starMutation,

        unstarMutation,

        readMutation,

        summarizeMutation,

        replyMutation

    }

}