import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import toast from "react-hot-toast";

import {
    getEmails,
    getUnreadEmails,
    getImportantEmails,
    getStarredEmails,
    getArchivedEmails,
    searchEmails,
    syncGmail
} from "../api/emailApi";

import { useEmails } from "../hooks/useEmails";

import EmailSidebar from "../components/email/EmailSidebar";
import EmailToolbar from "../components/email/EmailToolbar";
import EmailList from "../components/email/EmailList";
import EmailViewer from "../components/email/EmailViewer";

const Emails = () => {

    const { readMutation } = useEmails();

    const [folder, setFolder] = useState("Inbox");

    const [selectedEmail, setSelectedEmail] = useState(null);

    const [search, setSearch] = useState("");

    const [syncing, setSyncing] = useState(false);

    // ===========================================
    // MARK EMAIL AS READ
    // ===========================================

    useEffect(() => {

        if (

            selectedEmail &&

            selectedEmail.unread

        ) {

            readMutation.mutate(

                selectedEmail.id

            );

        }

    }, [selectedEmail]);

    // ===========================================
    // FETCH EMAILS
    // ===========================================

    const fetchEmails = async () => {

        if (search.trim() !== "") {

            return await searchEmails(search);

        }

        switch (folder) {

            case "Unread":

                return await getUnreadEmails();

            case "Important":

                return await getImportantEmails();

            case "Starred":

                return await getStarredEmails();

            case "Archived":

                return await getArchivedEmails();

            default:

                return await getEmails();

        }

    };

    const {

        data: emails = [],

        isLoading,

        refetch

    } = useQuery({

        queryKey: [

            "emails",

            folder,

            search

        ],

        queryFn: fetchEmails

    });

    // ===========================================
    // GMAIL SYNC
    // ===========================================

    const handleSync = async () => {

        try {

            setSyncing(true);

            await syncGmail();

            toast.success(

                "Gmail Synced Successfully"

            );

            refetch();

        }

        catch (error) {

            toast.error(

                "Failed to Sync Gmail"

            );

        }

        finally {

            setSyncing(false);

        }

    };

    if (isLoading)

        return (

            <div className="flex justify-center items-center h-[calc(100vh-3rem)]">
                <p className="text-sm text-ink-muted">Loading emails...</p>
            </div>

        );

    return (

        <div className="flex h-[calc(100vh-3rem)]">

            <EmailSidebar

                folder={folder}

                setFolder={setFolder}

            />

            <div className="flex-1 flex flex-col min-w-0">

                <EmailToolbar

                    folder={folder}

                    onSearch={setSearch}

                    onRefresh={refetch}

                    onSync={handleSync}

                    syncing={syncing}

                />

                <div className="flex flex-1 overflow-hidden">

                    <EmailList

                        emails={emails}

                        selectedEmail={selectedEmail}

                        setSelectedEmail={setSelectedEmail}

                    />

                    <EmailViewer

                        email={selectedEmail}

                    />

                </div>

            </div>

        </div>

    );

};

export default Emails;
