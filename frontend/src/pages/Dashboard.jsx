import { useQuery } from "@tanstack/react-query";

import { getDashboard } from "../api/dashboardApi";

import GreetingCard from "../components/dashboard/GreetingCard";
import ProductivityCard from "../components/dashboard/ProductivityCard";
import FocusCard from "../components/dashboard/FocusCard";
import EmailCard from "../components/dashboard/EmailCard";
import MeetingCard from "../components/dashboard/MeetingCard";
import TaskCard from "../components/dashboard/TaskCard";
import UrgentEmailCard from "../components/dashboard/UrgentEmailCard";
import TodayScheduleCard from "../components/dashboard/TodayScheduleCard";
import TodayTaskCard from "../components/dashboard/TodayTaskCard";
import MorningBriefCard from "../components/dashboard/MorningBriefCard";
import RecommendationCard from "../components/dashboard/RecommendationCard";

const Dashboard = () => {

    const {
        data,
        isLoading,
        error
    } = useQuery({

        queryKey: ["dashboard"],

        queryFn: getDashboard

    });

    if (isLoading) {

        return (

            <div className="flex justify-center items-center h-64">

                <p className="text-sm text-ink-muted">
                    Loading dashboard...
                </p>

            </div>

        );

    }

    if (error) {

        return (

            <div className="flex justify-center items-center h-64">

                <p className="text-sm text-[var(--color-tag-red-text)]">
                    Failed to load dashboard
                </p>

            </div>

        );

    }

    return (

        <div className="max-w-5xl mx-auto px-10 py-8 space-y-8">

            {/* Greeting */}

            <GreetingCard
                user={data.user}
            />

            {/* Productivity + Focus */}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                <ProductivityCard
                    productivity={data.productivity}
                />

                <FocusCard
                    focus={data.focus}
                />

            </div>

            {/* Emails + Meetings */}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                <EmailCard
                    emails={data.emails}
                />

                <MeetingCard
                    meetings={data.meetings}
                />

            </div>

            {/* Tasks + Today's Tasks */}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                <TaskCard
                    tasks={data.tasks}
                />

                <TodayTaskCard
                    tasks={data.today_tasks}
                />

            </div>

            {/* Urgent Emails + Today's Schedule */}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                <UrgentEmailCard
                    emails={data.urgent_emails}
                />

                <TodayScheduleCard
                    meetings={data.today_schedule}
                />

            </div>

            {/* Morning Brief */}

            <MorningBriefCard
                brief={data.morning_brief}
            />

            {/* Recommendations */}

            <RecommendationCard
                recommendations={data.recommendations}
            />

        </div>

    );

};

export default Dashboard;