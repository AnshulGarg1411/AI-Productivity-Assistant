const EmailDetails = ({ email }) => {

    if(!email){

        return(

            <div className="bg-white rounded-xl shadow p-6">

                Select an email.

            </div>

        );

    }

    return(

        <div className="bg-white rounded-xl shadow p-6">

            <h2 className="text-2xl font-bold">

                {email.subject}

            </h2>

            <p className="text-gray-500 mt-2">

                {email.sender}

            </p>

            <hr className="my-4"/>

            <p>

                {email.snippet}

            </p>

        </div>

    );

};

export default EmailDetails;