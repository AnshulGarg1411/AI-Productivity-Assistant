import { Star } from "lucide-react";

const EmailCard = ({ email, onSelect }) => {

    return (

        <div

            onClick={()=>onSelect(email)}

            className="bg-white rounded-xl p-5 shadow cursor-pointer hover:shadow-lg transition"

        >

            <div className="flex justify-between">

                <h2 className="font-semibold">

                    {email.sender}

                </h2>

                {

                    email.importance &&

                    <Star
                        className="text-yellow-500"
                        fill="gold"
                    />

                }

            </div>

            <h3 className="font-medium mt-2">

                {email.subject}

            </h3>

            <p className="text-gray-500 mt-2 line-clamp-2">

                {email.snippet}

            </p>

        </div>

    );

};

export default EmailCard;