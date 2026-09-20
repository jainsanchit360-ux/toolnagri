/* ToolNagri PDF engine — shared helpers for all PDF tools.
   Loads pdf.js (Mozilla, open-source) from jsDelivr on demand, plus a small
   compatibility polyfill for Map.prototype.getOrInsertComputed, a very new
   JS Map method that pdf.js 5.x calls internally but which many current
   browsers (including the one used to build/test this) do not yet implement. */
(function () {
  "use strict";

  var PDFJS_VERSION = "5.6.205";
  var PDFJS_BASE = "https://cdn.jsdelivr.net/npm/pdfjs-dist@" + PDFJS_VERSION + "/build/";

  if (!Map.prototype.getOrInsertComputed) {
    Map.prototype.getOrInsertComputed = function (key, callbackfn) {
      if (!this.has(key)) this.set(key, callbackfn(key));
      return this.get(key);
    };
  }

  var pdfjsLibPromise = null;
  function ensurePdfJs() {
    if (pdfjsLibPromise) return pdfjsLibPromise;
    pdfjsLibPromise = import(/* webpackIgnore: true */ PDFJS_BASE + "pdf.min.mjs")
      .then(function (mod) {
        mod.GlobalWorkerOptions.workerSrc = PDFJS_BASE + "pdf.worker.min.mjs";
        return mod;
      });
    return pdfjsLibPromise;
  }

  function loadScriptOnce(url) {
    return new Promise(function (resolve, reject) {
      var existing = document.querySelector('script[data-src="' + url + '"]');
      if (existing) {
        if (existing.getAttribute("data-loaded") === "true") return resolve();
        existing.addEventListener("load", resolve);
        existing.addEventListener("error", function () { reject(new Error("load_failed")); });
        return;
      }
      var s = document.createElement("script");
      s.src = url;
      s.setAttribute("data-src", url);
      s.onload = function () { s.setAttribute("data-loaded", "true"); resolve(); };
      s.onerror = function () { reject(new Error("load_failed")); };
      document.head.appendChild(s);
    });
  }

  var jszipPromise = null;
  function ensureJSZip() {
    if (jszipPromise) return jszipPromise;
    jszipPromise = loadScriptOnce("https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js")
      .then(function () {
        if (typeof JSZip === "undefined") throw new Error("load_failed");
        return JSZip;
      });
    return jszipPromise;
  }

  var docxPromise = null;
  function ensureDocx() {
    if (docxPromise) return docxPromise;
    docxPromise = loadScriptOnce("https://cdn.jsdelivr.net/npm/docx@9.6.1/dist/index.umd.cjs")
      .then(function () {
        if (typeof window.docx === "undefined") throw new Error("load_failed");
        return window.docx;
      });
    return docxPromise;
  }

  var pptxPromise = null;
  function ensurePptxGenJS() {
    if (pptxPromise) return pptxPromise;
    pptxPromise = loadScriptOnce("https://cdn.jsdelivr.net/npm/pptxgenjs@4.0.1/dist/pptxgen.bundle.js")
      .then(function () {
        if (typeof window.PptxGenJS === "undefined") throw new Error("load_failed");
        return window.PptxGenJS;
      });
    return pptxPromise;
  }

  var xlsxHelperReady = null;
  function ensureXlsxHelper() {
    // Builds minimal, valid .xlsx files directly (OOXML + inline strings) using JSZip,
    // rather than depending on a third-party spreadsheet library from a CDN. This was
    // switched from a SheetJS CDN dependency after that dependency could not be verified
    // to work in this environment; the format below has been independently validated by
    // opening its output with openpyxl.
    if (xlsxHelperReady) return xlsxHelperReady;
    xlsxHelperReady = ensureJSZip().then(function (JSZip) {
      function esc(s) {
        return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;").replace(/\r?\n/g, " ");
      }
      function colLetter(n) {
        var s = ""; n = n + 1;
        while (n > 0) { var rem = (n - 1) % 26; s = String.fromCharCode(65 + rem) + s; n = Math.floor((n - 1) / 26); }
        return s;
      }
      function safeSheetName(n) {
        var cleaned = String(n).slice(0, 31).replace(/[\\\/\?\*\[\]:]/g, " ").trim();
        return cleaned || "Sheet";
      }
      // sheets: array of { name, rows: [[cellText, ...], ...] }
      async function buildXlsxBlob(sheets) {
        var zip = new JSZip();
        zip.file("[Content_Types].xml",
          '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' +
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">' +
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>' +
          '<Default Extension="xml" ContentType="application/xml"/>' +
          '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>' +
          sheets.map(function (s, i) { return '<Override PartName="/xl/worksheets/sheet' + (i + 1) + '.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'; }).join("") +
          "</Types>");
        zip.folder("_rels").file(".rels",
          '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' +
          '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
          '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>' +
          "</Relationships>");
        zip.folder("xl").file("workbook.xml",
          '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' +
          '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">' +
          "<sheets>" +
          sheets.map(function (s, i) { return '<sheet name="' + esc(safeSheetName(s.name)) + '" sheetId="' + (i + 1) + '" r:id="rId' + (i + 1) + '"/>'; }).join("") +
          "</sheets></workbook>");
        zip.folder("xl").folder("_rels").file("workbook.xml.rels",
          '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' +
          '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
          sheets.map(function (s, i) { return '<Relationship Id="rId' + (i + 1) + '" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet' + (i + 1) + '.xml"/>'; }).join("") +
          "</Relationships>");
        sheets.forEach(function (sheet, si) {
          var rowsXml = sheet.rows.map(function (row, ri) {
            var cellsXml = row.map(function (cellVal, ci) {
              var ref = colLetter(ci) + (ri + 1);
              var text = cellVal === null || cellVal === undefined ? "" : String(cellVal);
              return '<c r="' + ref + '" t="inlineStr"><is><t xml:space="preserve">' + esc(text) + "</t></is></c>";
            }).join("");
            return '<row r="' + (ri + 1) + '">' + cellsXml + "</row>";
          }).join("");
          zip.folder("xl").folder("worksheets").file("sheet" + (si + 1) + ".xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' +
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>' +
            rowsXml + "</sheetData></worksheet>");
        });
        return zip.generateAsync({ type: "blob" });
      }
      return { buildXlsxBlob: buildXlsxBlob };
    });
    return xlsxHelperReady;
  }

  var pdfLibPromise = null;
  function ensurePdfLib() {
    if (pdfLibPromise) return pdfLibPromise;
    pdfLibPromise = loadScriptOnce("https://cdnjs.cloudflare.com/ajax/libs/pdf-lib/1.17.1/pdf-lib.min.js")
      .then(function () {
        if (typeof PDFLib === "undefined") throw new Error("load_failed");
        return PDFLib;
      });
    return pdfLibPromise;
  }

  async function renderPageToCanvas(pdf, pageNumber, scale) {
    var page = await pdf.getPage(pageNumber);
    var viewport = page.getViewport({ scale: scale || 1.5 });
    var canvas = document.createElement("canvas");
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    var ctx = canvas.getContext("2d");
    await page.render({ canvasContext: ctx, viewport: viewport }).promise;
    return canvas;
  }

  async function extractPageText(pdf, pageNumber) {
    var page = await pdf.getPage(pageNumber);
    var content = await page.getTextContent();
    return content.items.map(function (it) { return it.str; }).join(" ");
  }

  // Groups text items into approximate rows/columns using their transform matrix (x,y),
  // for a best-effort table reconstruction. Works reasonably for simple, grid-like PDFs;
  // complex multi-column layouts will not extract perfectly.
  async function extractPageTable(pdf, pageNumber, yTolerance) {
    var page = await pdf.getPage(pageNumber);
    var content = await page.getTextContent();
    var items = content.items.map(function (it) {
      return { text: it.str, x: it.transform[4], y: Math.round(it.transform[5]) };
    }).filter(function (it) { return it.text.trim() !== ""; });

    var tol = yTolerance || 3;
    var rows = [];
    items.forEach(function (it) {
      var row = rows.find(function (r) { return Math.abs(r.y - it.y) <= tol; });
      if (!row) { row = { y: it.y, items: [] }; rows.push(row); }
      row.items.push(it);
    });
    rows.sort(function (a, b) { return b.y - a.y; }); // PDF y-axis grows upward
    return rows.map(function (row) {
      row.items.sort(function (a, b) { return a.x - b.x; });
      return row.items.map(function (it) { return it.text; });
    });
  }

  function downloadBlob(blob, filename) {
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url; a.download = filename;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
  }

  function formatBytes(b) {
    if (b < 1024) return b + " B";
    if (b < 1024 * 1024) return (b / 1024).toFixed(1) + " KB";
    return (b / 1024 / 1024).toFixed(2) + " MB";
  }

  window.ToolNagriPDF = {
    ensurePdfJs: ensurePdfJs,
    ensureJSZip: ensureJSZip,
    ensureDocx: ensureDocx,
    ensurePptxGenJS: ensurePptxGenJS,
    ensureXlsxHelper: ensureXlsxHelper,
    ensurePdfLib: ensurePdfLib,
    renderPageToCanvas: renderPageToCanvas,
    extractPageText: extractPageText,
    extractPageTable: extractPageTable,
    downloadBlob: downloadBlob,
    formatBytes: formatBytes,
  };
})();
