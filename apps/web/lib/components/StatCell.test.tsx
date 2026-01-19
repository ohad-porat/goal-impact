import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatCell } from "./StatCell";

describe("StatCell", () => {
  describe("Basic rendering", () => {
    it("should render number value", () => {
      render(
        <table>
          <tbody>
            <tr>
              <StatCell value={42} />
            </tr>
          </tbody>
        </table>,
      );

      expect(screen.getByText("42")).toBeInTheDocument();
    });

    it("should render string value", () => {
      render(
        <table>
          <tbody>
            <tr>
              <StatCell value="Test" />
            </tr>
          </tbody>
        </table>,
      );

      expect(screen.getByText("Test")).toBeInTheDocument();
    });

    it('should render "-" for null value', () => {
      render(
        <table>
          <tbody>
            <tr>
              <StatCell value={null} />
            </tr>
          </tbody>
        </table>,
      );

      expect(screen.getByText("-")).toBeInTheDocument();
    });
  });

  describe("Formatter", () => {
    it("should format number with formatter function", () => {
      const formatter = (val: number) => `$${val.toFixed(2)}`;

      render(
        <table>
          <tbody>
            <tr>
              <StatCell value={42.5} formatter={formatter} />
            </tr>
          </tbody>
        </table>,
      );

      expect(screen.getByText("$42.50")).toBeInTheDocument();
    });

    it("should not format string values even with formatter", () => {
      const formatter = (val: number) => `$${val}`;

      render(
        <table>
          <tbody>
            <tr>
              <StatCell value="Test" formatter={formatter} />
            </tr>
          </tbody>
        </table>,
      );

      expect(screen.getByText("Test")).toBeInTheDocument();
    });

    it("should not format null values", () => {
      const formatter = (val: number) => `$${val}`;

      render(
        <table>
          <tbody>
            <tr>
              <StatCell value={null} formatter={formatter} />
            </tr>
          </tbody>
        </table>,
      );

      expect(screen.getByText("-")).toBeInTheDocument();
    });
  });

  describe("Style variants", () => {
    it("should use statsTable style by default", () => {
      const { container } = render(
        <table>
          <tbody>
            <tr>
              <StatCell value={10} />
            </tr>
          </tbody>
        </table>,
      );

      const cell = container.querySelector("td");
      expect(cell).toHaveClass("px-3", "py-2", "text-center");
    });

    it("should use compact style when specified", () => {
      const { container } = render(
        <table>
          <tbody>
            <tr>
              <StatCell value={10} style="compact" />
            </tr>
          </tbody>
        </table>,
      );

      const cell = container.querySelector("td");
      expect(cell).toHaveClass(
        "px-3",
        "py-2",
        "whitespace-nowrap",
        "text-center",
      );
    });
  });

  describe("Text style variants", () => {
    it("should use center text style by default", () => {
      const { container } = render(
        <table>
          <tbody>
            <tr>
              <StatCell value={10} />
            </tr>
          </tbody>
        </table>,
      );

      const span = container.querySelector("span");
      expect(span).toHaveClass("text-center", "text-gray-300");
    });

    it("should use points text style for compact style", () => {
      const { container } = render(
        <table>
          <tbody>
            <tr>
              <StatCell value={10} style="compact" textStyle="points" />
            </tr>
          </tbody>
        </table>,
      );

      const span = container.querySelector("span");
      expect(span).toHaveClass("text-center", "text-white", "font-bold");
    });

    it("should use primary text style for compact style", () => {
      const { container } = render(
        <table>
          <tbody>
            <tr>
              <StatCell value={10} style="compact" textStyle="primary" />
            </tr>
          </tbody>
        </table>,
      );

      const span = container.querySelector("span");
      expect(span).toHaveClass("text-sm", "font-medium", "text-white");
    });

    it("should use secondary text style for compact style", () => {
      const { container } = render(
        <table>
          <tbody>
            <tr>
              <StatCell value={10} style="compact" textStyle="secondary" />
            </tr>
          </tbody>
        </table>,
      );

      const span = container.querySelector("span");
      expect(span).toHaveClass("text-sm", "text-gray-300");
    });
  });

  describe("Custom className", () => {
    it("should apply custom className", () => {
      const { container } = render(
        <table>
          <tbody>
            <tr>
              <StatCell value={10} className="custom-class" />
            </tr>
          </tbody>
        </table>,
      );

      const cell = container.querySelector("td");
      expect(cell).toHaveClass("custom-class");
    });

    it("should combine custom className with default classes", () => {
      const { container } = render(
        <table>
          <tbody>
            <tr>
              <StatCell value={10} className="custom-class" />
            </tr>
          </tbody>
        </table>,
      );

      const cell = container.querySelector("td");
      expect(cell?.className).toContain("custom-class");
      expect(cell?.className).toContain("px-3");
    });
  });

  describe("Edge cases", () => {
    it("should handle zero value", () => {
      render(
        <table>
          <tbody>
            <tr>
              <StatCell value={0} />
            </tr>
          </tbody>
        </table>,
      );

      expect(screen.getByText("0")).toBeInTheDocument();
    });

    it("should handle negative numbers", () => {
      render(
        <table>
          <tbody>
            <tr>
              <StatCell value={-5} />
            </tr>
          </tbody>
        </table>,
      );

      expect(screen.getByText("-5")).toBeInTheDocument();
    });

    it("should handle very large numbers", () => {
      render(
        <table>
          <tbody>
            <tr>
              <StatCell value={999999} />
            </tr>
          </tbody>
        </table>,
      );

      expect(screen.getByText("999999")).toBeInTheDocument();
    });

    it("should handle decimal numbers", () => {
      render(
        <table>
          <tbody>
            <tr>
              <StatCell value={3.14159} />
            </tr>
          </tbody>
        </table>,
      );

      expect(screen.getByText("3.14159")).toBeInTheDocument();
    });
  });
});
