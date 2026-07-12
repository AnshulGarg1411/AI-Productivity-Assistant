import { Search, RefreshCw, RotateCw } from "lucide-react";
import { useState } from "react";

const EmailToolbar = ({

    folder,

    onSearch,

    onRefresh,
    onSync,

    syncing

}) => {

    const [query, setQuery] = useState("");

    return (

        <div className="flex items-center justify-between border-b border-border px-5 py-3 shrink-0">

            <h1 className="text-lg font-semibold text-ink">

                {folder}

            </h1>

            <div className="flex items-center gap-2">

                <div className="relative">

                    <Search
                        size={14}
                        className="absolute left-2.5 top-1/2 -translate-y-1/2 text-ink-faint"
                    />

                    <input

                        type="text"

                        value={query}

                        placeholder="Search emails..."

                        onChange={(e) =>

                            setQuery(e.target.value)

                        }

                        onKeyDown={(e) => {

                            if (e.key === "Enter") {

                                onSearch(query);

                            }

                        }}

                        className="pl-8 pr-3 py-1.5 bg-canvas border border-border rounded-md w-64 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent"

                    />

                </div>

                <div className="flex gap-1.5">

                    <button

                        onClick={onSync}

                        disabled={syncing}

                        className="flex items-center gap-1.5 px-3 py-1.5 bg-accent text-white text-sm font-medium rounded-md hover:bg-accent-hover disabled:opacity-50 transition-colors"

                    >

                        <RotateCw

                            className={

                                syncing

                                    ?

                                    "animate-spin"

                                    :

                                    ""

                            }

                            size={14}

                        />

                        {

                            syncing

                                ?

                                "Syncing..."

                                :

                                "Sync Gmail"

                        }

                    </button>

                    <button

                        onClick={onRefresh}

                        className="p-1.5 rounded-md border border-border text-ink-muted hover:bg-surface-hover hover:text-ink transition-colors"

                    >

                        <RefreshCw size={14} />

                    </button>

                </div>

            </div>

        </div>

    );

};

export default EmailToolbar;
