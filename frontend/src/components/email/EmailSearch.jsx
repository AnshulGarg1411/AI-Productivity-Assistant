import { Search } from "lucide-react";

const EmailSearch = ({ search, setSearch }) => {

    return (

        <div className="relative">

            <Search
                className="absolute left-4 top-3 text-gray-400"
                size={20}
            />

            <input

                type="text"

                value={search}

                onChange={(e)=>setSearch(e.target.value)}

                placeholder="Search emails..."

                className="w-full pl-12 pr-4 py-3 rounded-xl border shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"

            />

        </div>

    );

};

export default EmailSearch;