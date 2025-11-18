const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');
const fs = require('fs');
const path = require('path');
const yargs = require('yargs');

if (isMainThread) {
  const argv = yargs
    .option('input', { type: 'string', demandOption: true })
    .option('output', { type: 'string', demandOption: true })
    .help()
    .argv;

  const worker = new Worker(__filename, {
    workerData: { input: argv.input, output: argv.output }
  });

  worker.on('message', (msg) => {
    if (msg.success) {
      console.log('Compilation successful:', msg.output);
    } else {
      console.error('Compilation failed:', msg.error);
      process.exit(1);
    }
  });

  worker.on('error', (err) => {
    console.error('Worker error:', err);
    process.exit(1);
  });

} else {
  const workerPath = path.join(__dirname, 'compiler.worker.cjs');
  const workerCode = fs.readFileSync(workerPath, 'utf8');

  const fakeRequire = (id) => {
    if (id.startsWith('@tensorflow')) return require('@tensorflow/tfjs-node');
    return require(id);
  };

  const fakeModule = { exports: {} };
  const compileFn = new Function('module', 'exports', 'require', workerCode + '\nreturn compile;');

  try {
    const compile = compileFn(fakeModule, fakeModule.exports, fakeRequire);
    compile(workerData.input, workerData.output)
      .then(() => parentPort.postMessage({ success: true, output: workerData.output }))
      .catch(err => parentPort.postMessage({ success: false, error: err.message }));
  } catch (err) {
    parentPort.postMessage({ success: false, error: err.message });
  }
}