import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import Navbar from "./Navbar";
import { useRouter } from "next/navigation";
import type { AppRouterInstance } from "next/dist/shared/lib/app-router-context.shared-runtime";

vi.mock("next/navigation", () => ({
  useRouter: vi.fn(),
}));

vi.mock("./SearchBar", () => ({
  default: () => <div data-testid="search-bar">SearchBar</div>,
}));

describe("Navbar", () => {
  const mockPush = vi.fn();
  const mockReplace = vi.fn();
  const mockRouter: Partial<AppRouterInstance> = {
    push: mockPush,
    replace: mockReplace,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useRouter).mockReturnValue(mockRouter as AppRouterInstance);
  });

  it("should render the logo", () => {
    render(<Navbar />);

    const logo = screen.getByText("GOAL IMPACT");
    expect(logo).toBeInTheDocument();
    expect(logo.closest("a")).toHaveAttribute("href", "/");
  });

  it("should render all navigation links", () => {
    render(<Navbar />);

    expect(screen.getByText("Nations").closest("a")).toHaveAttribute(
      "href",
      "/nations",
    );
    expect(screen.getByText("Leagues").closest("a")).toHaveAttribute(
      "href",
      "/leagues",
    );
    expect(screen.getByText("Clubs").closest("a")).toHaveAttribute(
      "href",
      "/clubs",
    );
    expect(screen.getByText("Leaders").closest("a")).toHaveAttribute(
      "href",
      "/leaders",
    );
  });

  it("should render SearchBar component", () => {
    render(<Navbar />);

    expect(screen.getByTestId("search-bar")).toBeInTheDocument();
  });

  it("should have correct container structure", () => {
    const { container } = render(<Navbar />);

    const nav = container.querySelector("nav");
    expect(nav).toBeInTheDocument();
    expect(nav).toHaveClass("bg-orange-400", "w-full");

    const innerContainer = nav?.querySelector(".max-w-7xl");
    expect(innerContainer).toBeInTheDocument();
  });

  it("should have correct link styling classes", () => {
    render(<Navbar />);

    const nationsLink = screen.getByText("Nations").closest("a");
    expect(nationsLink).toHaveClass(
      "text-black",
      "font-semibold",
      "text-base",
      "sm:text-lg",
      "uppercase",
      "tracking-wide",
      "hover:text-slate-700",
      "transition-colors",
    );
  });

  it("should have correct logo styling classes", () => {
    render(<Navbar />);

    const logo = screen.getByText("GOAL IMPACT").closest("a");
    expect(logo).toHaveClass(
      "text-black",
      "font-bold",
      "text-xl",
      "sm:text-2xl",
      "uppercase",
      "tracking-wide",
      "hover:text-slate-700",
      "transition-colors",
      "mr-2",
      "sm:mr-6",
    );
  });
});
