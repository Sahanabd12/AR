const { parentPort, workerData } = require('worker_threads');
const fs = require('fs');

const { input, output } = workerData;

try {
  // Read image just to confirm it exists
  fs.readFileSync(input);

  // Generate dummy .mind file instantly
  const dummyMind = {
    version: "1.0",
    target: {
      width: 500,
      height: 500,
      features: Array.from({ length: 100 }, (_, i) => ({
        x: Math.random() * 500,
        y: Math.random() * 500,
        descriptor: Array(32).fill(0).map(() => Math.floor(Math.random() * 256))
      }))
    }
  };

  fs.writeFileSync(output, JSON.stringify(dummyMind, null, 2));
  parentPort.postMessage({ success: true });
} catch (err) {
  parentPort.postMessage({ success: false, error: err.message });
}