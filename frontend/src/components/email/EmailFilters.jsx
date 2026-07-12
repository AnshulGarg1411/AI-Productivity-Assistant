const EmailFilters = ({ filter, setFilter }) => {

    return (

        <div className="flex gap-4">

            <button

                onClick={()=>setFilter("all")}

                className={`px-5 py-2 rounded-lg ${
                    filter==="all"
                        ? "bg-blue-600 text-white"
                        : "bg-white"
                }`}

            >

                All

            </button>

            <button

                onClick={()=>setFilter("unread")}

                className={`px-5 py-2 rounded-lg ${
                    filter==="unread"
                        ? "bg-blue-600 text-white"
                        : "bg-white"
                }`}

            >

                Unread

            </button>

            <button

                onClick={()=>setFilter("important")}

                className={`px-5 py-2 rounded-lg ${
                    filter==="important"
                        ? "bg-blue-600 text-white"
                        : "bg-white"
                }`}

            >

                Important

            </button>

        </div>

    );

};

export default EmailFilters;