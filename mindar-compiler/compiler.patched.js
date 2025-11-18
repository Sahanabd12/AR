const { Worker } = require('worker_threads');
const fs = require('fs');
const path = require('path');
const yargs = require('yargs');

const argv = yargs
  .option('input', { type: 'string', demandOption: true })
  .option('output', { type: 'string', demandOption: true })
  .help()
  .argv;

const runWorker = (input, output) => {
  return new Promise((resolve, reject) => {
    const worker = new Worker(path.join(__dirname, 'compiler.worker.cjs'), {
      workerData: { input, output }
    });

    worker.on('message', (msg) => {
      if (msg.success) resolve();
      else reject(new Error(msg.error));
    });

    worker.on('error', reject);
    worker.on('exit', (code) => {
      if (code !== 0) reject(new Error(`Worker stopped with exit code ${code}`));
    });
  });
};

runWorker(argv.input, argv.output)
  .then(() => console.log('Compilation successful:', argv.output))
  .catch(err => {
    console.error('Compilation failed:', err.message);
    process.exit(1);
  });