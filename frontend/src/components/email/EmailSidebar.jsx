import {
    Inbox,
    Mail,
    Star,
    Archive,
    AlertCircle
} from "lucide-react";

const menus = [

    {
        name: "Inbox",
        icon: Inbox
    },

    {
        name: "Unread",
        icon: Mail
    },

    {
        name: "Important",
        icon: AlertCircle
    },

    {
        name: "Starred",
        icon: Star
    },

    {
        name: "Archived",
        icon: Archive
    }

];

const EmailSidebar = ({

    folder,

    setFolder

}) => {

    return (

        <div className="w-56 border-r border-border bg-surface p-3 shrink-0">

            <h2 className="text-xs font-medium text-ink-faint uppercase tracking-wide px-2 mb-3">
                Gmail
            </h2>

            <div className="space-y-0.5">

                {

                    menus.map((item) => {

                        const Icon = item.icon;

                        return (

                            <button

                                key={item.name}

                                onClick={() =>

                                    setFolder(item.name)

                                }

                                className={`flex items-center gap-2.5 w-full px-2.5 py-1.5 rounded-md text-sm transition-colors ${
                                    folder === item.name
                                        ? "bg-surface-hover text-ink font-medium"
                                        : "text-ink-muted hover:bg-surface-hover hover:text-ink"
                                }`}

                            >

                                <Icon size={15} />

                                <span>

                                    {item.name}

                                </span>

                            </button>

                        );

                    })

                }

            </div>

        </div>

    );

};

export default EmailSidebar;
