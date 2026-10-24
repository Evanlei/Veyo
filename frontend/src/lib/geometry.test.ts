import { describe, expect, it } from "vitest";
import { boxStyle, pixelBox, validBox, targetBoundsError } from "./geometry";

describe("canonical target geometry", () => {
  it("maps reversed drags to the same integer region", () => {
    expect(pixelBox([0.8, 0.9], [0.1, 0.2], 1000, 500)).toEqual([
      100, 100, 800, 450,
    ]);
  });
  it("clamps pointer positions to the image", () => {
    expect(pixelBox([-0.1, -0.2], [1.2, 1.1], 100, 80)).toEqual([
      0, 0, 100, 80,
    ]);
  });
  it("keeps display boxes proportional to the canonical grid", () => {
    expect(boxStyle([10, 20, 60, 80], 100, 100)).toEqual({
      left: "10%",
      top: "20%",
      width: "50%",
      height: "60%",
    });
    expect(validBox([1, 1, 2, 2])).toBe(false);
  });
  it("explains invalid target geometry and ambiguous comparison labels", () => {
    expect(
      targetBoundsError(
        [{ box: [0, 0, 200, 100], label: "Product", role: "product" }],
        100,
        100,
      ),
    ).toMatch("bounds");
    const target = {
      box: [0, 0, 50, 50] as [number, number, number, number],
      label: "Product",
      role: "product",
    };
    expect(
      targetBoundsError([target, { ...target, label: "product" }], 100, 100),
    ).toMatch("distinct");
    expect(targetBoundsError([target], 100, 100)).toBeUndefined();
  });
});
