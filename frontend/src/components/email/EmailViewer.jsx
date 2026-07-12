import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {

    User,

    Calendar,

    Paperclip,

    Star,

    Archive,

    Trash2,

    Sparkles,

    Copy,

    CheckSquare

} from "lucide-react";

import toast from "react-hot-toast";

import { useEmails } from "../../hooks/useEmails";
import { PRIORITY_TAG, EMAIL_CATEGORY_TAG, pill } from "../../lib/tagStyles";

const TONES = [
    { key: "friendly", label: "Friendly" },
    { key: "formal", label: "Formal" },
    { key: "short", label: "Short" },
    { key: "detailed", label: "Detailed" },
];

const EmailViewer = ({ email }) => {

    const {

        starMutation,

        unstarMutation,

        archiveMutation,

        deleteMutation,

        summarizeMutation,

        replyMutation

    } = useEmails();

    const [tone, setTone] = useState("friendly");
    const [replyText, setReplyText] = useState("");

    // Reset the draft reply whenever the viewed email changes
    useEffect(() => {
        setReplyText("");
        setTone("friendly");
    }, [email?.id]);

    if (!email)

        return (

            <div className="flex-1 flex items-center justify-center bg-surface">

                <div className="text-center">

                    <h2 className="text-sm font-medium text-ink-muted">

                        Select an email

                    </h2>

                    <p className="text-sm text-ink-faint mt-1">

                        Choose an email to read

                    </p>

                </div>

            </div>

        );

    const handleGenerateReply = () => {
        replyMutation.mutate(
            { id: email.id, tone },
            {
                onSuccess: (data) => setReplyText(data.reply),
            }
        );
    };

    const handleCopyReply = () => {
        navigator.clipboard.writeText(replyText);
        toast.success("Reply copied to clipboard");
    };

    return (

        <div className="flex-1 flex flex-col overflow-hidden min-w-0">

            {/* Header */}

            <div className="border-b border-border p-5">

                <div className="flex justify-between items-start gap-4">

                    <div className="min-w-0">

                        <h1 className="text-lg font-semibold text-ink truncate">

                            {email.subject}

                        </h1>

                        <div className="mt-2 flex flex-col gap-1.5 text-sm text-ink-muted">

                            <div className="flex items-center gap-2">

                                <User size={14} />

                                {email.sender}

                            </div>

                            <div className="flex items-center gap-2 font-mono">

                                <Calendar size={14} />

                                {

                                    new Date(

                                        email.received_at

                                    ).toLocaleString()

                                }

                            </div>

                            {

                                email.has_attachment &&

                                <div className="flex items-center gap-2">

                                    <Paperclip size={14} />

                                    Attachment available

                                </div>

                            }

                        </div>

                        <div className="flex items-center gap-1.5 mt-2">
                            {email.ai_priority && (
                                <span className={pill(PRIORITY_TAG[email.ai_priority])}>
                                    <Sparkles size={9} className="mr-1" />
                                    {email.ai_priority}
                                </span>
                            )}
                            {email.category && EMAIL_CATEGORY_TAG[email.category] && (
                                <span className={pill(EMAIL_CATEGORY_TAG[email.category])}>
                                    {email.category}
                                </span>
                            )}
                        </div>

                    </div>

                    {/* Actions */}

                    <div className="flex gap-0.5 shrink-0">

                        {/* Star */}

                        <button

                            onClick={(e) => {

                                e.stopPropagation();

                                if (email.starred) {

                                    unstarMutation.mutate(

                                        email.id

                                    );

                                }

                                else {

                                    starMutation.mutate(

                                        email.id

                                    );

                                }

                            }}

                            className="p-1.5 rounded-md hover:bg-surface-hover"

                        >

                            <Star

                                size={17}

                                fill={

                                    email.starred

                                        ?

                                        "currentColor"

                                        :

                                        "none"

                                }

                                className={

                                    email.starred

                                        ?

                                        "text-[var(--color-tag-yellow-text)]"

                                        :

                                        "text-ink-faint"

                                }

                            />

                        </button>

                        {/* Archive */}

                        <button

                            onClick={(e) => {

                                e.stopPropagation();

                                archiveMutation.mutate(

                                    email.id

                                );

                            }}

                            className="p-1.5 rounded-md hover:bg-surface-hover"

                        >

                            <Archive size={17} className="text-ink-faint" />

                        </button>

                        {/* Delete */}

                        <button

                            onClick={(e) => {

                                e.stopPropagation();

                                if (

                                    window.confirm(

                                        "Delete this email?"

                                    )

                                ) {

                                    deleteMutation.mutate(

                                        email.id

                                    );

                                }

                            }}

                            className="p-1.5 rounded-md hover:bg-[var(--color-tag-red-bg)]"

                        >

                            <Trash2

                                size={17}

                                className="text-[var(--color-tag-red-text)]"

                            />

                        </button>

                    </div>

                </div>

            </div>

            {/* Email Body */}

            <div className="flex-1 overflow-y-auto p-5">

                <p className="whitespace-pre-wrap leading-7 text-sm text-ink">

                    {

                        email.body

                            ? email.body

                            : email.snippet

                    }

                </p>

            </div>

            {/* AI Assistant -- real, working functionality */}

            <div className="border-t border-border bg-surface p-4 max-h-[45%] overflow-y-auto">

                <h2 className="text-sm font-semibold text-ink mb-3 flex items-center gap-1.5">
                    <Sparkles size={14} className="text-[var(--color-tag-yellow-text)]" />
                    AI Assistant
                </h2>

                <div className="space-y-2">

                    {/* Summary */}
                    <div className="bg-canvas border border-border rounded-md p-3">

                        <div className="flex justify-between items-center">
                            <h3 className="text-xs font-medium text-ink-muted uppercase tracking-wide">
                                Summary
                            </h3>
                            {!email.ai_summary && (
                                <button
                                    onClick={() => summarizeMutation.mutate(email.id)}
                                    disabled={summarizeMutation.isPending}
                                    className="text-xs font-medium text-accent hover:underline disabled:opacity-50"
                                >
                                    {summarizeMutation.isPending ? "Generating..." : "Generate"}
                                </button>
                            )}
                        </div>

                        <p className="text-sm text-ink mt-1">
                            {email.ai_summary || "No summary yet."}
                        </p>
                    </div>

                    {/* Smart Reply */}
                    <div className="bg-canvas border border-border rounded-md p-3">

                        <div className="flex justify-between items-center flex-wrap gap-2">
                            <h3 className="text-xs font-medium text-ink-muted uppercase tracking-wide">
                                Smart reply
                            </h3>
                            <div className="flex items-center gap-1">
                                {TONES.map((t) => (
                                    <button
                                        key={t.key}
                                        onClick={() => setTone(t.key)}
                                        className={`text-xs px-2 py-0.5 rounded-md transition-colors ${
                                            tone === t.key
                                                ? "bg-accent text-white"
                                                : "text-ink-muted hover:bg-surface-hover"
                                        }`}
                                    >
                                        {t.label}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <button
                            onClick={handleGenerateReply}
                            disabled={replyMutation.isPending}
                            className="text-xs font-medium text-accent hover:underline mt-2 disabled:opacity-50"
                        >
                            {replyMutation.isPending ? "Generating..." : "Generate reply"}
                        </button>

                        {replyText && (
                            <div className="mt-2">
                                <textarea
                                    value={replyText}
                                    onChange={(e) => setReplyText(e.target.value)}
                                    rows={4}
                                    className="w-full text-sm border border-border rounded-md p-2 bg-canvas text-ink focus:outline-none focus:ring-2 focus:ring-accent/40"
                                />
                                <button
                                    onClick={handleCopyReply}
                                    className="flex items-center gap-1 text-xs text-ink-muted hover:text-ink mt-1"
                                >
                                    <Copy size={12} />
                                    Copy
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Action items -> points to the real feature (task extraction) */}
                    <div className="bg-canvas border border-border rounded-md p-3">

                        <h3 className="text-xs font-medium text-ink-muted uppercase tracking-wide">
                            Action items
                        </h3>

                        <p className="text-sm text-ink-faint mt-1 flex items-center gap-1.5">
                            <CheckSquare size={13} />
                            Tasks detected in your emails are created
                            automatically —{" "}
                            <Link to="/tasks" className="text-accent hover:underline">
                                view them on the Tasks page
                            </Link>
                        </p>
                    </div>

                </div>

            </div>

        </div>

    );

};

export default EmailViewer;
