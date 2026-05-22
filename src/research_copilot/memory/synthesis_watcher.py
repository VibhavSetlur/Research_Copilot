import logging
import time
from pathlib import Path
from typing import Optional

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    class FileSystemEventHandler: pass

logger = logging.getLogger("research.synthesis_watcher")


class SynthesisHandler(FileSystemEventHandler):
    def __init__(self, root: Path):
        self.root = root
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith("decisions.yaml"):
            logger.info(f"Detected change in {event.src_path}, triggering synthesis update.")
            self._update_manuscript()
            
    def _update_manuscript(self):
        """Incrementally updates 01_workspace/live_manuscript.md."""
        manuscript = self.root / "01_workspace" / "live_manuscript.md"
        # Mock synthesis update
        with open(manuscript, "a") as f:
            f.write(f"\n- Auto-synthesis triggered at {time.time()}\n")


class SynthesisWatcher:
    """Continuous Background Synthesis Daemon.
    
    Async file watcher that intercepts decisions.yaml changes and incrementally
    updates the 01_workspace/live_manuscript.md.
    """

    def __init__(self, root: Optional[Path] = None):
        from research_copilot.utils.common import find_project_root
        self.root = root or find_project_root()
        self.observer = None
        self.watch_thread = None

    def start(self):
        """Start the background synthesis watcher."""
        if not HAS_WATCHDOG:
            logger.warning("Watchdog not installed. SynthesisWatcher cannot run.")
            return
            
        if self.observer is not None:
            return
            
        experiments_dir = self.root / "02_experiments"
        if not experiments_dir.exists():
            experiments_dir.mkdir(parents=True)
            
        event_handler = SynthesisHandler(self.root)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(experiments_dir), recursive=True)
        self.observer.start()
        logger.info("Started synthesis watcher in background.")

    def stop(self):
        """Stop the background synthesis watcher."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            logger.info("Stopped synthesis watcher.")
