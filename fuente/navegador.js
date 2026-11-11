// Ubica Chrome/Chromium para puppeteer-core: variable CHROME_PATH, Chrome de Windows o Chromium de Linux.
const fs = require("fs");
const CANDIDATOS = [
  process.env.CHROME_PATH,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  "/opt/pw-browsers/chromium",
  "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
];
function rutaNavegador() {
  const r = CANDIDATOS.find((c) => c && fs.existsSync(c));
  if (!r) throw new Error("No se encontró Chrome: definir la variable CHROME_PATH");
  return r;
}
// argumentos para que WebGL ande sin placa de video (servidores, máquinas virtuales)
// (en Linux como root Chrome exige --no-sandbox)
const SIN_SANDBOX = process.getuid && process.getuid() === 0 ? ["--no-sandbox"] : [];
const ARGS_WEBGL = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--enable-webgl", "--ignore-gpu-blocklist", "--allow-file-access-from-files", ...SIN_SANDBOX];
module.exports = { rutaNavegador, ARGS_WEBGL, SIN_SANDBOX };
