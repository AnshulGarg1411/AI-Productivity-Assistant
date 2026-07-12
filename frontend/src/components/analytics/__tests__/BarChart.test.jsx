import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import BarChart from "../BarChart";

describe("BarChart", () => {
  it("renders every label and value", () => {
    render(
      <BarChart
        data={[
          { label: "Completed", value: 8 },
          { label: "Pending", value: 4 },
        ]}
      />
    );

    expect(screen.getByText("Completed")).toBeInTheDocument();
    expect(screen.getByText("8")).toBeInTheDocument();
    expect(screen.getByText("Pending")).toBeInTheDocument();
    expect(screen.getByText("4")).toBeInTheDocument();
  });

  it("appends the value suffix when provided", () => {
    render(
      <BarChart
        data={[{ label: "Estimated Minutes", value: 30 }]}
        valueSuffix=" min"
      />
    );

    expect(screen.getByText("30 min")).toBeInTheDocument();
  });

  it("scales the largest bar to 100% width", () => {
    const { container } = render(
      <BarChart
        data={[
          { label: "A", value: 10 },
          { label: "B", value: 5 },
        ]}
      />
    );

    const bars = container.querySelectorAll(".rounded-full.h-full");
    expect(bars[0].style.width).toBe("100%");
    expect(bars[1].style.width).toBe("50%");
  });

  it("does not divide by zero when every value is 0", () => {
    const { container } = render(
      <BarChart data={[{ label: "Nothing yet", value: 0 }]} />
    );

    const bar = container.querySelector(".rounded-full.h-full");
    expect(bar.style.width).toBe("0%");
  });
});
