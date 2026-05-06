import argparse
import platform
import statistics
import time

from config import GSConfig
from utilities.gelsightmini import GelSightMini
from utilities.logger import log_message


def resolve_device_index(device_index: int | None, config: GSConfig) -> int | None:
    if device_index is not None:
        return device_index
    if platform.system() == "Windows":
        return None
    return config.config.default_camera_index


def summarize_intervals(intervals: list[float], measurement_seconds: float) -> None:
    if not intervals:
        log_message("No frames captured after warmup; no frequency data to report.")
        return

    mean_interval = statistics.mean(intervals)
    min_interval = min(intervals)
    max_interval = max(intervals)
    stdev_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0.0

    mean_fps = 1.0 / mean_interval if mean_interval > 0 else 0.0
    max_fps = 1.0 / min_interval if min_interval > 0 else 0.0
    min_fps = 1.0 / max_interval if max_interval > 0 else 0.0

    log_message(f"Captured {len(intervals)} frame intervals in {measurement_seconds:.2f}s.")
    log_message(
        "FPS summary -> "
        f"mean: {mean_fps:.2f}, min: {min_fps:.2f}, max: {max_fps:.2f}"
    )
    log_message(
        "Interval summary -> "
        f"mean: {mean_interval * 1000:.2f}ms, "
        f"min: {min_interval * 1000:.2f}ms, "
        f"max: {max_interval * 1000:.2f}ms, "
        f"stdev: {stdev_interval * 1000:.2f}ms"
    )


def run_frequency_test(
    config: GSConfig,
    device_index: int | None,
    duration_s: float,
    max_frames: int,
    warmup_frames: int,
    target_hz: float,
) -> None:
    cam = GelSightMini(
        target_width=config.config.camera_width,
        target_height=config.config.camera_height,
        border_fraction=config.config.border_fraction,
    )

    device_index = resolve_device_index(device_index, config)

    if device_index is None and platform.system() != "Windows":
        log_message("No device index provided. Use --device-index to select a camera.")
        return

    cam.select_device(device_index)
    cam.start()

    log_message("Starting frequency test (RGB frames only). Press Ctrl+C to stop.")
    log_message(
        f"Target frequency: {target_hz:.2f} Hz"
        if target_hz > 0
        else "Target frequency: max (no throttling)."
    )

    intervals: list[float] = []
    frame_count = 0
    warmup_remaining = max(warmup_frames, 0)
    initial_warmup = warmup_remaining
    start_time = time.perf_counter()
    measurement_start = None
    last_capture_time = None

    try:
        while True:
            loop_start = time.perf_counter()
            frame = cam.update(0.0)  # GelSightMini.update ignores dt but keeps a compatible signature.

            if frame is None:
                continue

            capture_time = time.perf_counter()

            if warmup_remaining > 0:
                warmup_remaining -= 1
                last_capture_time = capture_time
            else:
                if measurement_start is None:
                    measurement_start = capture_time
                if last_capture_time is not None:
                    intervals.append(capture_time - last_capture_time)
                last_capture_time = capture_time
                frame_count += 1

            if max_frames > 0 and frame_count >= max_frames:
                break
            if duration_s > 0:
                if measurement_start is None:
                    if (
                        warmup_remaining == initial_warmup
                        and capture_time - start_time >= duration_s
                    ):
                        break
                elif capture_time - measurement_start >= duration_s:
                    break

            if target_hz > 0:
                target_period = 1.0 / target_hz
                elapsed = time.perf_counter() - loop_start
                sleep_time = target_period - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
    except KeyboardInterrupt:
        log_message("Interrupted by user. Reporting collected statistics.")
    finally:
        if cam.camera:
            cam.camera.release()

    measurement_end = last_capture_time or time.perf_counter()
    measurement_seconds = (
        measurement_end - measurement_start if measurement_start else 0.0
    )
    summarize_intervals(intervals, measurement_seconds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Measure GelSight Mini capture frequency using RGB frames."
    )
    parser.add_argument(
        "--gs-config",
        type=str,
        default=None,
        help="Path to the JSON configuration file. Defaults to default_config.json.",
    )
    parser.add_argument(
        "--device-index",
        type=int,
        default=None,
        help="Camera device index (ignored on Windows when auto-detecting GelSight Mini).",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=10.0,
        help="Duration of the frequency test in seconds (0 to disable).",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=0,
        help="Number of frames to capture after warmup (0 to disable).",
    )
    parser.add_argument(
        "--warmup-frames",
        type=int,
        default=10,
        help="Number of initial frames to ignore while the camera stabilizes.",
    )
    parser.add_argument(
        "--target-hz",
        type=float,
        default=0.0,
        help="Target loop frequency (0 for max throughput).",
    )

    args = parser.parse_args()

    gs_config = GSConfig(args.gs_config or "default_config.json")
    run_frequency_test(
        config=gs_config,
        device_index=args.device_index,
        duration_s=args.duration,
        max_frames=args.frames,
        warmup_frames=args.warmup_frames,
        target_hz=args.target_hz,
    )
