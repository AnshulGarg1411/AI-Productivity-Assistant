// Central color mapping for status/priority/category pills, so every page
// (Tasks, Meetings, Dashboard) renders the same tag for the same value
// instead of each component inventing its own palette.

const TAG = {
  red: "bg-[var(--color-tag-red-bg)] text-[var(--color-tag-red-text)]",
  orange: "bg-[var(--color-tag-orange-bg)] text-[var(--color-tag-orange-text)]",
  yellow: "bg-[var(--color-tag-yellow-bg)] text-[var(--color-tag-yellow-text)]",
  green: "bg-[var(--color-tag-green-bg)] text-[var(--color-tag-green-text)]",
  blue: "bg-[var(--color-tag-blue-bg)] text-[var(--color-tag-blue-text)]",
  purple: "bg-[var(--color-tag-purple-bg)] text-[var(--color-tag-purple-text)]",
  gray: "bg-[var(--color-tag-gray-bg)] text-[var(--color-tag-gray-text)]",
};

export const PRIORITY_TAG = {
  HIGH: TAG.red,
  MEDIUM: TAG.yellow,
  LOW: TAG.green,
};

export const CATEGORY_TAG = {
  WORK: TAG.blue,
  STUDY: TAG.purple,
  PERSONAL: TAG.orange,
  HEALTH: TAG.green,
};

// AI-predicted email categories (see app/ai/email_intelligence_agent.py) --
// a separate universe of values from the task categories above.
export const EMAIL_CATEGORY_TAG = {
  WORK: TAG.blue,
  COLLEGE: TAG.purple,
  FINANCE: TAG.green,
  SHOPPING: TAG.orange,
  TRAVEL: TAG.blue,
  SOCIAL: TAG.purple,
  OTHER: TAG.gray,
};

export const TASK_STATUS_TAG = {
  TODO: TAG.gray,
  IN_PROGRESS: TAG.blue,
  COMPLETED: TAG.green,
};

export const MEETING_STATUS_TAG = {
  CONFIRMED: TAG.green,
  TENTATIVE: TAG.yellow,
  CANCELLED: TAG.gray,
};

export const MEETING_TYPE_TAG = {
  ONLINE: TAG.blue,
  OFFLINE: TAG.purple,
};

export const pill = (colorClasses) =>
  `inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium ${colorClasses}`;
