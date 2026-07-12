import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import RingStat from "../RingStat";

describe("RingStat", () => {
  it("renders the rounded value as text", () => {
    render(<RingStat value={72.4} label="Task Completion Rate" />);
    expect(screen.getByText("72")).toBeInTheDocument();
    expect(screen.getByText("Task Completion Rate")).toBeInTheDocument();
  });

  it("rounds down/up correctly at the boundary", () => {
    render(<RingStat value={49.5} label="x" />);
    expect(screen.getByText("50")).toBeInTheDocument();
  });

  it(
    "regression: a 0-100 percentage value (like completion_rate from the " +
      "API) is displayed as-is, not re-scaled -- this is exactly the bug " +
      "where Analytics.jsx once multiplied an already-0-100 value by 100",
    () => {
      render(<RingStat value={85} max={100} label="Completion" />);
      expect(screen.getByText("85")).toBeInTheDocument();
      expect(screen.queryByText("8500")).not.toBeInTheDocument();
    }
  );

  it("defaults max to 100 when not provided", () => {
    const { container } = render(<RingStat value={100} label="Full" />);
    const progressCircle = container.querySelectorAll("circle")[1];
    expect(progressCircle.getAttribute("stroke-dashoffset")).toBe("0");
  });
});
