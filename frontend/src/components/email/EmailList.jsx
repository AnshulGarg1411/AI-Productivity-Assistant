import EmailRow from "./EmailRow";

const EmailList = ({

    emails,

    selectedEmail,

    setSelectedEmail

}) => {

    if (emails.length === 0)

        return (

            <div className="flex-1 flex items-center justify-center border-r border-border">

                <p className="text-sm text-ink-faint">

                    No emails found

                </p>

            </div>

        );

    return (

        <div className="w-[38%] border-r border-border overflow-y-auto shrink-0">

            {

                emails.map((email) => (

                    <EmailRow

                        key={email.id}

                        email={email}

                        selected={

                            selectedEmail?.id === email.id

                        }

                        onClick={() =>

                            setSelectedEmail(email)

                        }

                    />

                ))

            }

        </div>

    );

};

export default EmailList;
