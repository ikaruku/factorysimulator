interface WakeLockSentinelLike {
  release(): Promise<void>;
}

interface NavigatorWithWakeLock {
  wakeLock?: {
    request(type: "screen"): Promise<WakeLockSentinelLike>;
  };
}

/**
 * Keeps the mobile screen awake during play using the Screen Wake Lock API,
 * gracefully ignoring browsers that do not support it.
 */
export class ScreenWakeLock {
  private sentinel: WakeLockSentinelLike | null = null;
  private requested = false;

  constructor() {
    document.addEventListener("visibilitychange", this.handleVisibilityChange);
  }

  request(): void {
    this.requested = true;
    void this.acquire();
  }

  dispose(): void {
    document.removeEventListener("visibilitychange", this.handleVisibilityChange);
    void this.sentinel?.release();
    this.sentinel = null;
  }

  private readonly handleVisibilityChange = (): void => {
    if (!document.hidden && this.requested) {
      void this.acquire();
    }
  };

  private async acquire(): Promise<void> {
    if (this.sentinel) return;
    const nav = navigator as unknown as NavigatorWithWakeLock;
    if (!nav.wakeLock) return;
    try {
      this.sentinel = await nav.wakeLock.request("screen");
    } catch {
      // Ignore permission or battery-saver rejections.
    }
  }
}
