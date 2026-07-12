const GreetingCard = ({ user }) => {
  const hour = new Date().getHours();

  let greeting = "Good evening";
  if (hour < 12) greeting = "Good morning";
  else if (hour < 18) greeting = "Good afternoon";

  const firstName = user?.name?.split(" ")[0] || "there";

  return (
    <div className="pb-2">
      <div className="text-4xl mb-3 leading-none">👋</div>
      <h1 className="text-3xl font-semibold text-ink tracking-tight">
        {greeting}, {firstName}
      </h1>
      <p className="text-sm text-ink-muted mt-1.5">
        Here's what's on your plate today.
      </p>
    </div>
  );
};

export default GreetingCard;
