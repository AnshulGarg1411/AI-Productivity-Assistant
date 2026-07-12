import {

    Paperclip,

    Star,

    Sparkles

} from "lucide-react";

import { PRIORITY_TAG, EMAIL_CATEGORY_TAG, pill } from "../../lib/tagStyles";

const EmailRow = ({

    email,

    selected,

    onClick

}) => {

    // Prefer the AI's priority classification (reads actual content) when
    // this email has been analyzed; fall back to Gmail's own IMPORTANT
    // label otherwise -- mirrors the same preference used server-side in
    // get_urgent_emails().
    const isAiAnalyzed = Boolean(email.ai_summary);

    return (

        <div

            onClick={onClick}

            className={`cursor-pointer border-b border-border px-4 py-3 hover:bg-surface transition-colors ${
                selected ? "bg-accent-soft" : ""
            }`}

        >

            <div className="flex justify-between items-center gap-2">

                <div className="flex items-center gap-1.5 min-w-0">

                    {

                        email.starred &&

                        <Star

                            size={13}

                            className="text-[var(--color-tag-yellow-text)] shrink-0"

                            fill="currentColor"

                        />

                    }

                    <span

                        className={`text-sm truncate ${
                            email.unread ? "font-semibold text-ink" : "font-medium text-ink-muted"
                        }`}

                    >

                        {email.sender}

                    </span>

                </div>

                <div className="text-xs text-ink-faint font-mono shrink-0">

                    {

                        new Date(

                            email.received_at

                        ).toLocaleDateString()

                    }

                </div>

            </div>

            <div

                className={`mt-1 text-sm truncate ${
                    email.unread ? "font-semibold text-ink" : "text-ink"
                }`}

            >

                {email.subject}

            </div>

            <div className="text-ink-faint text-xs mt-1 line-clamp-2">

                {isAiAnalyzed ? email.ai_summary : email.snippet}

            </div>

            <div className="flex items-center gap-1.5 mt-2 flex-wrap">

                {

                    email.has_attachment &&

                    <Paperclip

                        size={13}

                        className="text-ink-faint"

                    />

                }

                {

                    email.ai_priority ? (

                        <span className={pill(PRIORITY_TAG[email.ai_priority])}>

                            <Sparkles size={9} className="mr-1" />

                            {email.ai_priority}

                        </span>

                    ) : email.importance && (

                        <span className="inline-flex items-center px-1.5 py-0.5 rounded-md text-[10px] font-medium bg-[var(--color-tag-red-bg)] text-[var(--color-tag-red-text)]">

                            Important

                        </span>

                    )

                }

                {

                    email.category && EMAIL_CATEGORY_TAG[email.category] && (

                        <span className={pill(EMAIL_CATEGORY_TAG[email.category])}>

                            {isAiAnalyzed && <Sparkles size={9} className="mr-1" />}

                            {email.category}

                        </span>

                    )

                }

                {

                    email.archived &&

                    <span className="inline-flex items-center px-1.5 py-0.5 rounded-md text-[10px] font-medium bg-[var(--color-tag-gray-bg)] text-[var(--color-tag-gray-text)]">

                        Archived

                    </span>

                }
            </div>

        </div>

    );

};

export default EmailRow;
