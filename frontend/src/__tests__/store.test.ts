import { store, type RootState, type AppDispatch } from "../store";

describe("Redux Store", () => {
  it("should initialize with correct structure", () => {
    const state = store.getState();
    expect(state).toBeDefined();
    expect(typeof state).toBe("object");
  });

  it("should have the correct initial state structure", () => {
    const state = store.getState();
    // The store should have the API slice
    expect(state).toHaveProperty("api");
    expect(state.api).toHaveProperty("queries");
    expect(state.api).toHaveProperty("mutations");
  });

  it("should be able to dispatch actions", () => {
    expect(store.dispatch).toBeDefined();
    expect(typeof store.dispatch).toBe("function");
  });

  it("should have proper TypeScript types", () => {
    const state: RootState = store.getState();
    const dispatch: AppDispatch = store.dispatch;

    expect(state).toBeDefined();
    expect(dispatch).toBeDefined();
  });

  it("should be configurable", () => {
    expect(store).toBeDefined();
    expect(store.getState).toBeDefined();
    expect(store.dispatch).toBeDefined();
    expect(store.subscribe).toBeDefined();
  });

  it("should handle subscription", () => {
    const unsubscribe = store.subscribe(() => {
      // Test subscription callback
    });

    expect(typeof unsubscribe).toBe("function");
    unsubscribe();
  });
});
